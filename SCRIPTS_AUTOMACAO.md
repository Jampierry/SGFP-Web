# Scripts de Automação - SGFP

Este documento descreve os scripts de automação disponíveis no projeto SGFP para facilitar o desenvolvimento e manutenção do repositório Git.

## 📋 Índice

1. [Scripts Disponíveis](#scripts-disponíveis)
2. [setup_github.py](#setup_githubpy)
3. [update_git.py](#update_gitpy)
4. [Scripts Git Avançados](#scripts-git-avançados)
5. [Troubleshooting](#troubleshooting)

## 🚀 Scripts Disponíveis

### Scripts Principais

| Script | Descrição | Uso |
|--------|-----------|-----|
| `setup_github.py` | Configuração inicial do repositório | Primeira vez |
| `update_git.py` | Atualizações automáticas | Uso diário |
| `Scripts git/atualiza_git_v2.py` | Script avançado | Uso avançado |

### Scripts de Suporte

| Script | Descrição | Plataforma |
|--------|-----------|------------|
| `Scripts git/atualiza_git.ps1` | Script PowerShell | Windows |
| `Scripts git/atualiza_git.sh` | Script Bash | Linux/Mac |

## 🔧 setup_github.py

Script completo para configuração inicial do repositório GitHub.

### Funcionalidades

- ✅ Cria arquivo `.gitignore` apropriado para Django
- ✅ Remove arquivos desnecessários (`__pycache__`, `.pyc`)
- ✅ Inicializa repositório Git
- ✅ Adiciona remote do GitHub
- ✅ Cria commit inicial
- ✅ Configura branch `main`
- ✅ Faz push para GitHub
- ✅ Verifica configuração

### Uso

```bash
python setup_github.py
```

### Exemplo de Saída

```
🎯 Iniciando configuração do repositório GitHub...
📁 Diretório do projeto: /path/to/project
🔗 URL do repositório: https://github.com/Jampierry/SGFP-Web.git

🧹 Limpando arquivos desnecessários...
🗑️ Removido: /path/to/project/__pycache__
✅ Arquivo .gitignore criado com sucesso!
🚀 Configurando repositório Git...
✅ Repositório Git inicializado!
🔗 Configurando remote do GitHub...
✅ Remote do GitHub configurado!
📝 Criando commit inicial...
✅ Commit inicial criado!
🌿 Configurando branch main...
✅ Branch main configurada!
🚀 Enviando para o GitHub...
✅ Projeto enviado para o GitHub com sucesso!
🔍 Verificando configuração...
✅ Remote configurado corretamente
✅ Branch main configurada
✅ Status do repositório verificado

🎉 Configuração concluída com sucesso!
🌐 Seu projeto está disponível em: https://github.com/Jampierry/SGFP-Web.git
```

## 🔄 update_git.py

Script principal para atualizações automáticas do repositório.

### Funcionalidades

- ✅ Verifica se é um repositório Git
- ✅ Usa script V2 se disponível
- ✅ Método básico como fallback
- ✅ Limpeza de locks do Git
- ✅ Verificação de status
- ✅ Commit e push automáticos

### Uso

```bash
python update_git.py
```

### Exemplo de Saída

```
🚀 Script de Atualização Git - SGFP
==================================================
🔄 Usando script de atualização V2...
🚀 Executando script de atualização Git V2...
🚀 Iniciando atualização do repositório Git...
📁 Diretório do projeto: /path/to/project
🌿 Branch atual: main
🔄 Sincronizando com o repositório remoto...
⬇️ Baixando alterações do repositório remoto...
✅ Sincronização concluída com sucesso.
📝 Alterações detectadas:
   📝 Modificado: core/models.py
   ➕ Adicionado: setup_github.py
📦 Adicionando alterações...
💾 Fazendo commit: 🔧 Atualizações em 2 arquivos - 2025-07-03 19:30:00
✅ Commit realizado: [main abc1234] 🔧 Atualizações em 2 arquivos - 2025-07-03 19:30:00
🚀 Enviando para o GitHub...
✅ Alterações enviadas para o GitHub na branch main!
```

## 📁 Scripts Git Avançados

### atualiza_git_v2.py

Script avançado com recursos adicionais.

#### Funcionalidades Avançadas

- 🔄 Sincronização automática com repositório remoto
- 🔧 Resolução automática de conflitos
- 📝 Mensagens de commit personalizadas
- 🧹 Limpeza automática de locks
- 📊 Análise detalhada de alterações
- ⚡ Tratamento robusto de erros

#### Uso

```bash
python "Scripts git/atualiza_git_v2.py"
```

### atualiza_git.ps1 (PowerShell)

Script para Windows usando PowerShell.

#### Uso

```powershell
.\Scripts git\atualiza_git.ps1
```

### atualiza_git.sh (Bash)

Script para Linux/Mac usando Bash.

#### Uso

```bash
bash "Scripts git/atualiza_git.sh"
```

## 🛠️ Troubleshooting

### Problemas Comuns

#### 1. Erro: "Não é um repositório Git"

**Solução:**
```bash
python setup_github.py
```

#### 2. Erro: "Arquivo de lock detectado"

**Solução Automática:**
Os scripts removem automaticamente os locks. Se persistir:

```bash
# Remover locks manualmente
rm -rf .git/index.lock
rm -rf .git/MERGE_HEAD.lock
```

#### 3. Erro: "Conflitos de merge"

**Solução:**
O script V2 resolve automaticamente conflitos simples. Para conflitos complexos:

```bash
# Verificar status
git status

# Resolver conflitos manualmente
# Editar arquivos com conflitos
git add .
git commit -m "Resolvendo conflitos"
```

#### 4. Erro: "Remote não configurado"

**Solução:**
```bash
git remote add origin https://github.com/Jampierry/SGFP-Web.git
```

### Logs e Debug

#### Habilitar Logs Detalhados

```bash
# Para script V2
python "Scripts git/atualiza_git_v2.py" --verbose

# Para script principal
python update_git.py --debug
```

#### Verificar Status do Git

```bash
# Status geral
git status

# Status detalhado
git status --porcelain

# Verificar remotes
git remote -v

# Verificar branches
git branch -a
```

## 📊 Fluxo de Trabalho Recomendado

### Para Desenvolvedores

1. **Configuração Inicial**
   ```bash
   python setup_github.py
   ```

2. **Desenvolvimento Diário**
   ```bash
   # Fazer alterações no código
   # Testar funcionalidades
   python update_git.py
   ```

3. **Atualizações Avançadas**
   ```bash
   python "Scripts git/atualiza_git_v2.py"
   ```

### Para Contribuidores

1. **Fork do Repositório**
2. **Clone do Fork**
3. **Desenvolvimento**
4. **Push para Fork**
5. **Pull Request**

## 🔒 Segurança

### Arquivos Ignorados

O `.gitignore` criado automaticamente ignora:

- Arquivos de cache Python (`__pycache__`, `.pyc`)
- Arquivos de ambiente (`.env`, `.venv`)
- Banco de dados (`*.db`, `*.sqlite`)
- Logs (`logs/`, `*.log`)
- Backups (`backup/`)
- Arquivos temporários

### Boas Práticas

1. **Nunca commitar dados sensíveis**
2. **Sempre testar antes de fazer push**
3. **Usar mensagens de commit descritivas**
4. **Manter o repositório atualizado**

## 📞 Suporte

### Comandos Úteis

```bash
# Verificar versão do Git
git --version

# Verificar configuração
git config --list

# Verificar status do repositório
git status

# Verificar histórico de commits
git log --oneline -10
```

### Recursos Adicionais

- [Documentação Git](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Django Documentation](https://docs.djangoproject.com/)

---

**Última atualização:** 2025-07-03  
**Versão:** 2.0  
**Autor:** SGFP Development Team 