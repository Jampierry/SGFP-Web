# Regras de negócio do SGFP (estado atual do Django)

Referência para a migração. Cada regra tem teste em `core/tests.py` (rodar: `.venv/Scripts/python.exe manage.py test core`).
Itens "QUIRK" são comportamentos atuais que **não** devem ser copiados às cegas: decidir caso a caso na reimplementação.

## Saldo da conta (`Conta.atualizar_saldo`)
`saldo_atual = saldo_inicial + Σ receitas − Σ despesas + Σ transferências recebidas − Σ transferências enviadas`, só registros `ativo=True`.
- Recalculado no `save()` de Receita, Despesa (ramo normal) e Transferência.
- QUIRK: `delete()` não recalcula (saldo defasado até o próximo save).
- QUIRK: alterar `saldo_inicial` só reflete no próximo recálculo.
- QUIRK: `Transferencia.taxa` é ignorada no saldo.
- QUIRK: despesa no cartão debita a conta na hora da compra, não no pagamento da fatura.
- Alvo: saldo calculado em view/função SQL (nunca campo gravado).

## Fatura do cartão (despesa no cartão à vista)
- Compra no dia ≤ `data_fechamento_fatura` → fatura do mês; depois → mês seguinte (dezembro vira janeiro do ano seguinte).
- Vencimento = dia `data_vencimento_fatura` desse mês; se o dia não existe (ex.: 31 em fevereiro) usa o último dia do mês.
- Fatura única por (cartão, vencimento); criada sob demanda com valor 0 e reutilizada.
- `Fatura.valor_calculado()` = soma das despesas ativas do ciclo (data > fechamento anterior e ≤ fechamento atual), a menos que `ajustada=True` (usa o valor manual).
- QUIRK: o ciclo anterior é calculado como `fechamento − 30 dias` (não é o mês anterior exato).
- `limite_utilizado` = soma de TODAS as despesas ativas do cartão (inclusive de faturas pagas); `limite_disponivel = limite_total − utilizado`.

## Parcelamento (`Despesa.save`)
- Regra pretendida (ramo morto): parcela = `round(valor/n, 2)`; o resto de centavos vai na última; cada parcela vai para uma fatura sucessiva (mês a mês) com a data da parcela = vencimento da fatura.
- QUIRK/BUG confirmado por teste: a condição `not self.id` nunca é verdadeira (`id` tem `default=uuid4`), então hoje o parcelamento **não divide**: grava uma única despesa com o valor cheio na fatura da data da compra.
- Alvo: implementar a regra pretendida, em uma única função transacional, e decidir com o usuário o que fazer com os dados já gravados sem divisão.
- O mesmo cálculo de fatura está copiado em `Despesa.save` (2x), `core/utils.py` e o comando `associar_despesas_faturas`.

## Metas
- `percentual_concluido = min(valor_atual/valor_meta × 100, 100)`; `valor_restante = max(valor_meta − valor_atual, 0)`.

## Notificações
Alertas de saldo negativo, meta vencendo e despesas elevadas (`Notificacao.criar_alerta_*`); `marcar_como_lida` grava `data_leitura`.

## Isolamento por usuário
Hoje: filtro `usuario=request.user` nas views (sem garantia no banco). Alvo: RLS no Postgres.

## Decisões do esquema Postgres (Fase 2, `supabase/migrations/0001_schema.sql`)
Testes: `cd supabase/tests && npm install && npm test` (PGlite, Postgres real em WASM; 11 testes).
- **Isolamento:** toda tabela tem `user_id` + RLS "dono" (forçada). FKs compostas `(id, user_id)` impedem apontar para conta/categoria/cartão de outro usuário.
- **Saldo** é a view `contas_saldo` (calculada), então excluir recalcula sozinho (corrige o quirk do `delete`). **Decisão (minha, revisável):** a taxa de transferência passa a ser debitada da conta de origem (o Django a ignorava). A conferência da Fase 3 já desconta essa diferença esperada.
- **Cartão:** sem CVV; só `ultimos4`.
- **Parcelamento:** função `criar_despesa_cartao` (atômica, RLS do chamador) implementa a regra pretendida: `round(valor/n,2)`, resto na última, uma fatura por mês, `data` da parcela = vencimento da fatura, `data_compra` guarda a data real. Arredondamento: Postgres arredonda meio para cima; Python `round` em Decimal arredonda para par (diferença só em casos de meio centavo exato).
- **Fatura:** valor = `valor_ajustado` se houver, senão soma das despesas ligadas por `fatura_id` (não mais o ciclo "fechamento − 30 dias"; pode diferir de faturas antigas, a conferir na Fase 3).
- **Novo usuário:** trigger cria `configuracoes`. Categorias/conta padrão do cadastro antigo: a decidir na Fase 4.

## Migração dos dados (Fase 3, `supabase/etl/django_para_sql.mjs`)
```
python manage.py dumpdata auth.user core configuracoes --indent 1 > dump.json
# usuarios.json: { "username_django": "uuid-do-usuario-no-supabase-auth" }  (crie os usuários no Supabase antes)
node supabase/etl/django_para_sql.mjs dump.json usuarios.json carga.sql
# rode carga.sql no SQL Editor do Supabase (papel postgres ignora RLS); depois confira com conferirSaldos()
```
Nunca commitar `dump.json`, `usuarios.json` nem `carga.sql` (dados pessoais).
- IDs UUID preservados; `Fatura` (pk inteira) ganha uuid determinístico. CVV é descartado; do número do cartão só vão os 4 últimos dígitos.
- Cor inválida vira a cor padrão; frequência vazia vira nulo.
- **Compras parceladas antigas** (gravadas com valor cheio pelo bug) são mantidas como estão e listadas como AVISO na saída do script. Corrigir à mão, caso a caso, se importar.
- `conferirSaldos(db, dump)` compara `saldo_atual` do Django com a view `contas_saldo`; `diferenca_inesperada` ≠ 0 indica saldo defasado no Django (quirk do `delete`) ou erro de carga: investigar conta a conta.
- Testado só com dump sintético (`supabase/tests/etl.test.mjs`); não foi executado contra dados reais.
