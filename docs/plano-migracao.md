# Plano de mudança de tecnologia — SGFP-Web

## Contexto
SGFP-Web é um sistema de gestão financeira pessoal multiusuário (receitas, despesas, transferências, contas, metas, cartões e faturas, relatórios, notificações, backup). Hoje é Django 5.0.7 + SQLite + templates Bootstrap, parado desde 22/07/2025. Não há testes (`core/tests.py` tem 3 linhas), CI nem deploy. O `views.py` tem 2593 linhas.

Há problemas graves de segurança:
- Senha do admin em texto no repositório (`superuser_sysconfec.txt`).
- `SECRET_KEY` fixa, `DEBUG=True`.
- Qualquer usuário logado baixa ou sobrescreve o `db.sqlite3` inteiro e lê os backups de todos.
- O reset de senha (`login/views.py`) leva direto à tela de nova senha com o token.
- CVV do cartão guardado em texto.
- `@csrf_exempt` e mudanças de estado via GET.
- `db.sqlite3`, logs e backups versionados no Git.

A ideia é trocar a base por algo que resolva isso estruturalmente e dê deploy simples. Nada de código compartilhado com `comissao-di-paula` ou `Portal-Intranet`, então o escopo é só o SGFP-Web.

## Stack recomendada (decisão minha, sujeita à sua aprovação)
| Camada | Hoje | Alvo | Por quê |
|---|---|---|---|
| App | Django templates | Next.js (App Router) + TypeScript | Um só código front e back, tipagem, deploy fácil |
| Banco | SQLite | PostgreSQL no Supabase | Multiusuário real; isolamento por usuário com RLS (Row Level Security) |
| Auth | Django auth caseiro | Supabase Auth (e-mail + verificação, reset seguro, Google opcional) | Remove o reset inseguro e o registro aberto |
| Acesso a dados | Django ORM | Drizzle ORM + migrations SQL | Esquema versionado, tipado |
| UI | Bootstrap + 3,3 mil linhas de CSS | Tailwind + shadcn/ui, tema por CSS variables | Cumpre as etapas 3 a 5 do `TODO_TREE.md` |
| Gráficos | Chart.js solto | Recharts | Componentes React |
| Valores | Decimal/float misto | `numeric(14,2)` no banco, centavos inteiros no código | Sem erro de arredondamento nas parcelas |
| Testes | nenhum | Vitest (regras) + Playwright (fluxos) + pgTAP/teste de RLS | Hoje: zero |
| CI/Deploy | nenhum | GitHub Actions + Vercel + Supabase | Gratuito para uso pessoal |

Alternativa descartada: continuar em Django e só modernizar (Postgres + HTMX). É menos trabalho, mas não resolve a hospedagem nem o isolamento por usuário no banco, e o seu ecossistema (Portal, comissão) já está em JS.

## Fases
**Fase 0 — Contenção (antes de migrar, em ~1 dia)**
1. Trocar a senha do admin e o `SECRET_KEY`; remover `superuser_sysconfec.txt`.
2. Tirar do Git: `db.sqlite3`, `logs/`, `backup/`, `__pycache__`, `staticfiles/` (`git rm --cached` e `.gitignore`).
3. Verificar se o repositório GitHub é público. Se for, torná-lo privado e limpar o histórico (`git filter-repo`).
4. Desativar as rotas de banco completo e de backup em disco.
5. Converter `requirements.txt` de UTF-16 para UTF-8.

**Fase 1 — Mapeamento e congelamento do comportamento**
- Documentar as regras em `docs/regras.md`. Pontos principais: geração de parcelas e faturas em `Despesa.save()` (`core/models.py`), recálculo de saldo, transferências com taxa, metas, notificações.
- Exportar os dados atuais para JSON por usuário (usar o comando de backup existente).
- Escrever testes de caracterização das regras de fatura e de saldo, contra o Django atual, para servirem de referência.

**Fase 2 — Esquema e segurança no Postgres**
- Criar as tabelas: `categorias`, `contas`, `receitas`, `despesas`, `transferencias`, `metas`, `cartoes`, `faturas`, `notificacoes`, `configuracoes`.
- Todas com `user_id` e RLS "só o dono".
- Padronizar as chaves em UUID (hoje `Fatura` usa inteiro).
- Cartão: não guardar CVV nem número completo, só os 4 últimos dígitos.
- Saldo da conta como view ou função SQL, não campo recalculado em `save()`.
- Parcelamento e fatura em funções SQL ou server actions transacionais, em uma única implementação (hoje está copiada em 3 lugares).

**Fase 3 — Migração dos dados**
- Script de ETL: JSON do Django → Postgres, com mapeamento de IDs.
- Conferência de saldos por conta e total por mês, antes e depois.

**Fase 4 — Aplicação por módulo (estrangular)**
Ordem: Auth/Configurações → Categorias/Contas → Receitas/Despesas → Transferências → Cartões/Faturas → Metas → Notificações → Dashboard (moderno e clássico viram um só, configurável) → Relatórios → Backup/exportar (CSV, Excel, JSON por usuário).
Cada módulo sai com testes. Descartar o que não é usado: `teste.html`, `dashboard_responsive` duplicado e templates repetidos.

**Fase 5 — Qualidade e publicação**
- ESLint + Prettier + TypeScript estrito.
- GitHub Actions: lint, testes e build.
- Deploy na Vercel com variáveis de ambiente (nenhum segredo no repositório).
- README e docs atualizados; `TODO_TREE.md` reescrito conforme o novo andamento.

## Arquivos de origem relevantes
`core/models.py`, `core/views.py`, `core/forms.py`, `core/utils.py`, `core/context_processors.py`, `login/views.py`, `sgfp_web/settings.py`, `templates/core/*.html`, `static/*.css|js`, `TODO_TREE.md`.

## Verificação
- Fase 0: `git ls-files` sem dados pessoais; senha antiga não funciona mais.
- Fase 3: totais de saldo por conta e por mês idênticos ao Django.
- Fase 4: testes Vitest das regras de parcela e fatura passam; testes Playwright cobrem o fluxo de criar despesa parcelada, pagar fatura e transferir.
- RLS: teste automatizado em que o usuário A não consegue ler nem escrever dados do usuário B.
- CI verde e deploy de preview funcionando.

## Observações
- A migração só começa depois da Fase 0. Ela mexe em histórico do Git e é irreversível, então peço confirmação antes de reescrever o histórico.
- Execução: uma fase por vez, com commit ao fim de cada uma, nos repositórios do SGFP-Web.
