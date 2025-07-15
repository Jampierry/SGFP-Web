# SGFP - Sistema de Gestão Financeira Pessoal

Um sistema web completo para gestão financeira pessoal desenvolvido com Django, Bootstrap 5 e JavaScript moderno.

## 🚀 Funcionalidades

### 📊 Dashboard Inteligente
- Visão geral das finanças do mês atual com métricas em tempo real
- Gráficos interativos de receitas vs despesas (Chart.js)
- Cards de resumo com receitas, despesas e saldo
- Top categorias de gastos com análise visual
- Lista de contas com saldos atualizados automaticamente
- Progresso das metas financeiras
- Últimas transações com filtros inteligentes
- Sistema de alertas e notificações em tempo real
- Análise de tendências e previsões

### 💰 Gestão Completa de Transações
- **Receitas**: Registro de entradas de dinheiro com categorização
- **Despesas**: Controle detalhado de gastos
- **Transferências**: Movimentação entre contas com taxa opcional
- Categorização automática e personalizável
- Transações recorrentes com frequências configuráveis
- Observações e anexos
- Filtros avançados por período, categoria, conta e valor

### 🏦 Gestão de Contas
- Múltiplas contas (corrente, poupança, investimento, cartão de crédito, etc.)
- Saldos automáticos baseados nas transações
- Cores e ícones personalizáveis
- Histórico de movimentações
- Atualização automática de saldos

### 💳 Central de Cartões de Crédito
- Dashboard especializado para cartões de crédito
- Visualização de limites, utilização e disponibilidade
- Gráficos de evolução temporal dos gastos
- Gráfico de pizza com distribuição de gastos por cartão
- Painel de faturas organizadas por status (em aberto, pagas, vencidas, futuras)
- Gráfico de barras com evolução das faturas (12 meses)
- Filtros de data globais para toda a página
- Navegação entre meses nos gráficos
- Associação automática de despesas às faturas corretas
- Ações de pagar, reabrir e ajustar faturas
- Criação manual de faturas
- Seleção/deseleção interativa de cartões e faturas

### 🏷️ Sistema de Categorias
- Categorias personalizáveis para receitas e despesas
- Cores e ícones únicos
- Relatórios por categoria
- Categorias padrão criadas automaticamente
- Validação de duplicatas por usuário

### 🎯 Metas Financeiras
- Definição de metas de economia com prazos
- Acompanhamento do progresso em tempo real
- Alertas de prazo e progresso
- Diferentes tipos de metas (economia, investimento, pagamento, compra)
- Cálculo automático de percentual de conclusão

### 📈 Relatórios Avançados
- Relatórios detalhados por período personalizável
- Filtros por categoria, conta e data
- Gráficos e estatísticas interativas
- Exportação de dados em múltiplos formatos
- Análise de tendências e sazonalidade

### 🔔 Sistema de Notificações
- Notificações em tempo real no dashboard
- Alertas de saldo negativo
- Lembretes de metas próximas do vencimento
- Alertas de despesas elevadas
- Sistema de notificações não lidas
- Histórico completo de notificações

### ⚙️ Configurações Avançadas
- Preferências pessoais por usuário
- Tema escuro/claro
- Configurações de moeda brasileira
- Notificações por email
- Backup automático
- Configurações de formato de data

### 🔄 Sistema de Backup
- Backup automático dos dados
- Exportação manual de dados
- Importação de backups
- Gerenciamento de arquivos de backup
- Backup completo do banco de dados

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.0
- **Frontend**: Bootstrap 5, FontAwesome 6
- **Gráficos**: Chart.js 3.9.1
- **Formulários**: Crispy Forms + Bootstrap 5
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **JavaScript**: ES6+ com funcionalidades modernas
- **CSS**: Custom com variáveis CSS e responsividade
- **Autenticação**: Sistema nativo Django com validações

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Git

## 🚀 Instalação

### Opção 1: Clone do Repositório (Recomendado)

1. **Clone o repositório**
```bash
git clone https://github.com/Jampierry/SGFP-Web.git
cd SGFP-Web
```

2. **Crie um ambiente virtual**
```bash
python -m venv .venv
```

3. **Ative o ambiente virtual**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Instale as dependências**
```bash
pip install -r requirements.txt
```

5. **Configure o banco de dados**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

7. **Execute o servidor de desenvolvimento**
```bash
python manage.py runserver
```

8. **Acesse o sistema**
- URL: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

### Opção 2: Configuração Inicial para Desenvolvimento

Se você está configurando o projeto pela primeira vez:

1. **Configure o repositório GitHub**
```bash
python setup_github.py
```

2. **Siga os passos da Opção 1 (2-8)**

### Scripts de Automação

O projeto inclui scripts para facilitar o desenvolvimento:

```bash
# Configuração inicial do GitHub
python setup_github.py

# Atualizações automáticas
python update_git.py

# Script avançado de atualização
python "Scripts git/atualiza_git_v2.py"
```

## 📁 Estrutura do Projeto

```
SGFP Web - Sistema Gestão Financeira Pessoal/
├── core/                          # Aplicação principal Django
│   ├── models.py                  # Modelos de dados
│   ├── views.py                   # Views e lógica de negócio
│   ├── forms.py                   # Formulários com validações
│   ├── admin.py                   # Interface administrativa
│   ├── urls.py                    # URLs da aplicação
│   ├── templatetags/              # Filtros personalizados
│   │   └── br_filters.py         # Filtros para formatação brasileira
│   └── management/                # Comandos de gerenciamento
│       └── commands/
│           └── gerar_dados_ficticios.py
├── sgfp_web/                      # Configurações do projeto
│   ├── settings.py                # Configurações Django
│   └── urls.py                    # URLs principais
├── templates/                     # Templates HTML
│   ├── base.html                  # Template base com notificações
│   ├── core/                      # Templates da aplicação
│   └── registration/              # Templates de autenticação
├── static/                        # Arquivos estáticos
│   └── core/
│       ├── css/                   # Estilos CSS
│       │   ├── style.css          # Estilos principais
│       │   └── dashboard-themes.css # Temas do dashboard
│       └── js/                    # JavaScript
│           ├── main.js            # JavaScript principal
│           └── dashboard-advanced.js # Dashboard avançado
├── Scripts git/                   # Scripts de automação Git
│   ├── atualiza_git_v2.py         # Script avançado de atualização
│   ├── atualiza_git.py            # Script básico de atualização
│   ├── atualiza_git.ps1           # Script PowerShell
│   ├── atualiza_git.sh            # Script Bash
│   └── README.md                  # Documentação dos scripts
├── backup/                        # Diretório de backups
├── logs/                          # Logs do sistema
├── setup_github.py                # Script de configuração inicial
├── update_git.py                  # Script de atualização principal
├── manage.py                      # Script de gerenciamento Django
├── requirements.txt               # Dependências do projeto
└── README.md                      # Documentação principal
```

## 🎯 Como Usar

### 1. Primeiro Acesso
- Acesse http://127.0.0.1:8000/
- Clique em "Criar conta" para se registrar
- O sistema criará automaticamente:
  - Categorias padrão (Salário, Alimentação, Transporte, etc.)
  - Uma conta principal
  - Configurações padrão

### 2. Configuração Inicial
- Acesse "Contas" e adicione suas contas bancárias
- Configure o saldo inicial de cada conta
- Personalize as categorias conforme necessário

### 3. Registrando Transações
- Use o botão "Nova Receita" ou "Nova Despesa" no dashboard
- Preencha os dados obrigatórios
- Categorize adequadamente para melhor controle
- Configure transações recorrentes se necessário

### 4. Acompanhando Metas
- Crie metas financeiras em "Metas"
- Defina valor objetivo e prazo
- Acompanhe o progresso no dashboard
- Receba alertas de prazo

### 5. Relatórios e Análises
- Acesse "Relatórios" para análises detalhadas
- Use os filtros para períodos específicos
- Visualize gráficos interativos
- Exporte dados se necessário

### 6. Sistema de Notificações
- Receba alertas automáticos no dashboard
- Visualize notificações não lidas
- Acesse histórico completo de notificações
- Configure preferências de notificação

### 7. Central de Cartões de Crédito
- Acesse "Central de Cartões" no menu principal
- Visualize todos os seus cartões de crédito
- Clique em um cartão para filtrar toda a página
- Acompanhe limites, utilização e disponibilidade
- Gerencie faturas (pagar, reabrir, ajustar)
- Use filtros de data para análises específicas
- Navegue pelos gráficos com as setas de navegação
- Crie novas faturas manualmente quando necessário

## 🔧 Configurações Avançadas

### Personalização de Cores
Edite o arquivo `static/core/css/style.css` para personalizar:
- Cores do tema
- Estilos dos componentes
- Animações e transições

### Adicionando Novas Funcionalidades
1. Crie novos modelos em `core/models.py`
2. Adicione views em `core/views.py`
3. Configure URLs em `core/urls.py`
4. Crie templates em `templates/core/`

### Backup e Restauração
```bash
# Backup manual
python manage.py dumpdata > backup.json

# Restauração
python manage.py loaddata backup.json

# Backup automático via interface web
# Acesse: Configurações > Backup
```

### Geração de Dados Fictícios
```bash
# Gerar dados para teste
python manage.py gerar_dados_ficticios --quantidade 100

# Gerar dados para usuário específico
python manage.py gerar_dados_ficticios --usuario admin --quantidade 50

# Gerar dados incluindo cartões e faturas
python manage.py gerar_dados_ficticios --quantidade 30
```

### Scripts de Automação Git
```bash
# Configuração inicial do repositório
python setup_github.py

# Atualizações automáticas
python update_git.py

# Script avançado com mais recursos
python "Scripts git/atualiza_git_v2.py"

# Script PowerShell (Windows)
.\Scripts git\atualiza_git.ps1

# Script Bash (Linux/Mac)
bash Scripts\ git/atualiza_git.sh
```

## 🔮 Próximas Funcionalidades

### Integração com Google Drive
- Backup automático para Google Drive
- Sincronização de configurações
- Compartilhamento seguro de dados
- Acesso offline com sincronização

### Melhorias Planejadas
- App mobile nativo
- Integração com bancos brasileiros
- Sistema de orçamentos
- Relatórios fiscais
- Integração com sistemas de pagamento
- Dashboard de investimentos
- Relatórios de gastos por categoria de cartão
- Sistema de alertas para limites de cartão

## 🐛 Solução de Problemas

### Erro de Migração
```bash
python manage.py makemigrations --empty core
python manage.py makemigrations
python manage.py migrate
```

### Problemas de Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Reset do Banco de Dados
```bash
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Problemas de Formatação
- Verifique se o filtro `br_currency` está funcionando
- Confirme se as configurações de locale estão corretas
- Verifique se o arquivo `br_filters.py` está sendo carregado

## 📊 Funcionalidades Técnicas

### Segurança
- Autenticação de usuários com validação
- Proteção CSRF em todos os formulários
- Validação de formulários no frontend e backend
- Isolamento de dados por usuário
- Validação de permissões em todas as views

### Performance
- Queries otimizadas com select_related
- Cache de consultas frequentes
- Paginação de resultados
- Lazy loading de componentes
- Otimização de imagens e assets

### Responsividade
- Design mobile-first
- Bootstrap 5 responsivo
- Componentes adaptáveis
- Interface touch-friendly
- Sidebar colapsível em dispositivos móveis

### Acessibilidade
- Navegação por teclado
- Labels semânticos
- Contraste adequado
- Estrutura HTML semântica
- Suporte a leitores de tela

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido como projeto de sistema de gestão financeira pessoal.

## 🙏 Agradecimentos

- Django Documentation
- Bootstrap Team
- FontAwesome
- Chart.js
- Comunidade Python/Django

---

**SGFP** - Transformando o controle financeiro em uma experiência simples e eficiente! 💰✨ 

## 🆕 Novidades e Melhorias Recentes

### UI/UX Moderno e Padronizado (2025)
- Filtros de busca em Receitas e Despesas totalmente responsivos, com campos de data compactos e largura fixa.
- Botões de ação (Filtrar/Limpar) em nova linha, alinhados à esquerda, para melhor usabilidade.
- Tabelas de Receitas e Despesas com altura fixa (ajustável), scroll interno e linhas padronizadas (40px de altura).
- Colunas das tabelas padronizadas na mesma ordem para facilitar comparação e navegação.
- Remoção de observações extras na coluna Descrição para visual limpo e consistente.
- Espaçamento e alinhamento refinados entre cards de filtro e tabelas.
- Total responsividade: layout se adapta perfeitamente a qualquer tamanho de tela.
- Melhorias de acessibilidade e navegação por teclado. 