#!/usr/bin/env python3
"""
Script para configurar e enviar o projeto SGFP para o GitHub
Execute: python setup_github.py
"""

import subprocess
import sys
import os
import shutil
from datetime import datetime

class GitHubSetup:
    def __init__(self):
        self.project_root = os.getcwd()
        self.repo_url = "https://github.com/Jampierry/SGFP-Web.git"
        self.branch = "main"
        
    def run_command(self, command, cwd=None):
        """Executa um comando e retorna o resultado"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd or self.project_root
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    def create_gitignore(self):
        """Cria um arquivo .gitignore apropriado para Django"""
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Media files
media/

# Static files (if using collectstatic)
staticfiles/

# Backup files
backup/
*.backup
*.bak

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp

# Database files
*.db
*.sqlite

# Log files
logs/
*.log

# Environment variables
.env.local
.env.production

# Node modules (if using any frontend tools)
node_modules/

# Compiled CSS/JS
*.css.map
*.js.map
"""
        
        gitignore_path = os.path.join(self.project_root, '.gitignore')
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print("✅ Arquivo .gitignore criado com sucesso!")

    def clean_project(self):
        """Remove arquivos desnecessários antes do commit"""
        print("🧹 Limpando arquivos desnecessários...")
        
        # Remove arquivos __pycache__
        for root, dirs, files in os.walk(self.project_root):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    cache_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(cache_path)
                        print(f"🗑️ Removido: {cache_path}")
                    except Exception as e:
                        print(f"⚠️ Erro ao remover {cache_path}: {e}")
        
        # Remove arquivos .pyc
        for root, dirs, files in os.walk(self.project_root):
            for file_name in files:
                if file_name.endswith('.pyc'):
                    pyc_path = os.path.join(root, file_name)
                    try:
                        os.remove(pyc_path)
                        print(f"🗑️ Removido: {pyc_path}")
                    except Exception as e:
                        print(f"⚠️ Erro ao remover {pyc_path}: {e}")

    def setup_git_repository(self):
        """Configura o repositório Git"""
        print("🚀 Configurando repositório Git...")
        
        # Verifica se já é um repositório Git
        if os.path.exists(os.path.join(self.project_root, '.git')):
            print("ℹ️ Repositório Git já existe.")
            return True
        
        # Inicializa o repositório
        success, output, error = self.run_command("git init")
        if not success:
            print(f"❌ Erro ao inicializar Git: {error}")
            return False
        
        print("✅ Repositório Git inicializado!")
        return True

    def add_remote(self):
        """Adiciona o remote do GitHub"""
        print("🔗 Configurando remote do GitHub...")
        
        # Remove remote existente se houver
        self.run_command("git remote remove origin")
        
        # Adiciona o novo remote
        success, output, error = self.run_command(f'git remote add origin {self.repo_url}')
        if not success:
            print(f"❌ Erro ao adicionar remote: {error}")
            return False
        
        print("✅ Remote do GitHub configurado!")
        return True

    def create_initial_commit(self):
        """Cria o commit inicial"""
        print("📝 Criando commit inicial...")
        
        # Adiciona todos os arquivos
        success, output, error = self.run_command("git add .")
        if not success:
            print(f"❌ Erro ao adicionar arquivos: {error}")
            return False
        
        # Commit inicial
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_message = f"🚀 Commit inicial do SGFP - Sistema de Gestão Financeira Pessoal - {timestamp}"
        
        success, output, error = self.run_command(f'git commit -m "{commit_message}"')
        if not success:
            print(f"❌ Erro ao fazer commit: {error}")
            return False
        
        print("✅ Commit inicial criado!")
        return True

    def setup_main_branch(self):
        """Configura a branch main"""
        print("🌿 Configurando branch main...")
        
        # Renomeia para main se necessário
        success, output, error = self.run_command("git branch -M main")
        if not success:
            print(f"❌ Erro ao configurar branch main: {error}")
            return False
        
        print("✅ Branch main configurada!")
        return True

    def push_to_github(self):
        """Faz o push para o GitHub"""
        print("🚀 Enviando para o GitHub...")
        
        # Push inicial com upstream
        success, output, error = self.run_command(f"git push -u origin {self.branch}")
        if not success:
            print(f"❌ Erro ao fazer push: {error}")
            return False
        
        print("✅ Projeto enviado para o GitHub com sucesso!")
        return True

    def verify_setup(self):
        """Verifica se tudo foi configurado corretamente"""
        print("🔍 Verificando configuração...")
        
        # Verifica remote
        success, output, error = self.run_command("git remote -v")
        if success and self.repo_url in output:
            print("✅ Remote configurado corretamente")
        else:
            print("❌ Remote não configurado corretamente")
            return False
        
        # Verifica branch
        success, output, error = self.run_command("git branch")
        if success and "main" in output:
            print("✅ Branch main configurada")
        else:
            print("❌ Branch main não configurada")
            return False
        
        # Verifica status
        success, output, error = self.run_command("git status")
        if success:
            print("✅ Status do repositório verificado")
            print(f"📊 Status atual:\n{output}")
        else:
            print("❌ Erro ao verificar status")
            return False
        
        return True

    def setup_repository(self):
        """Função principal para configurar o repositório"""
        print("🎯 Iniciando configuração do repositório GitHub...")
        print(f"📁 Diretório do projeto: {self.project_root}")
        print(f"🔗 URL do repositório: {self.repo_url}")
        print()
        
        try:
            # 1. Limpa o projeto
            self.clean_project()
            print()
            
            # 2. Cria .gitignore
            self.create_gitignore()
            print()
            
            # 3. Configura repositório Git
            if not self.setup_git_repository():
                return False
            print()
            
            # 4. Adiciona remote
            if not self.add_remote():
                return False
            print()
            
            # 5. Cria commit inicial
            if not self.create_initial_commit():
                return False
            print()
            
            # 6. Configura branch main
            if not self.setup_main_branch():
                return False
            print()
            
            # 7. Push para GitHub
            if not self.push_to_github():
                return False
            print()
            
            # 8. Verifica configuração
            if not self.verify_setup():
                return False
            print()
            
            print("🎉 Configuração concluída com sucesso!")
            print(f"🌐 Seu projeto está disponível em: {self.repo_url}")
            print("📝 Próximos passos:")
            print("   1. Acesse o repositório no GitHub")
            print("   2. Configure as descrições e tags")
            print("   3. Use o script update_git.py para futuras atualizações")
            
            return True
            
        except Exception as e:
            print(f"💥 Erro inesperado: {e}")
            return False

def main():
    """Função principal"""
    try:
        setup = GitHubSetup()
        success = setup.setup_repository()
        
        if not success:
            print("\n💥 Falha na configuração do repositório!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Operação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 