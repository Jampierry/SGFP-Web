#!/usr/bin/env python3
"""
Script Python interativo para atualizar o repositório Git automaticamente
Execute na raiz do projeto: python atualiza_git.py
"""

import subprocess
import sys
import os
from datetime import datetime
import shutil

def run_command(command, cwd=None):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def get_project_root():
    """Obtém o diretório raiz do projeto"""
    current_dir = os.getcwd()
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(os.path.join(current_dir, '.git')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return os.getcwd()

def clean_git_locks(project_root):
    """Remove arquivos de lock do Git se existirem"""
    lock_files = [
        os.path.join(project_root, '.git', 'index.lock'),
        os.path.join(project_root, '.git', 'MERGE_HEAD.lock'),
        os.path.join(project_root, '.git', 'refs', 'heads', 'main.lock')
    ]
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                print(f"🔓 Removido arquivo de lock: {os.path.basename(lock_file)}")
            except Exception as e:
                print(f"⚠️ Não foi possível remover {lock_file}: {e}")

def handle_merge_conflicts(project_root, branch):
    print("⚠️ Detectados conflitos de merge. Tentando resolver...")
    success, output, error = run_command("git status --porcelain", cwd=project_root)
    if not success:
        print(f"❌ Erro ao verificar status: {error}")
        return False
    if "UU" in output:
        print("🔧 Detectados arquivos com conflitos. Tentando resolver...")
        if "logs/sgfp.log" in output:
            print("📝 Detectado arquivo de log com conflito. Sobrescrevendo...")
            success, output, error = run_command("git checkout --ours logs/sgfp.log", cwd=project_root)
            if success:
                success, output, error = run_command("git add logs/sgfp.log", cwd=project_root)
                if success:
                    print("✅ Conflito no arquivo de log resolvido.")
                else:
                    print(f"❌ Erro ao adicionar arquivo de log: {error}")
                    return False
            else:
                print(f"❌ Erro ao resolver conflito no log: {error}")
                return False
        success, output, error = run_command("git commit --no-edit", cwd=project_root)
        if success:
            print("✅ Merge concluído com sucesso.")
            return True
        else:
            print(f"❌ Erro ao finalizar merge: {error}")
            return False
    return True

def sync_with_remote(project_root, branch):
    print("🔄 Sincronizando com o repositório remoto...")
    clean_git_locks(project_root)
    success, output, error = run_command("git status --porcelain", cwd=project_root)
    if not success:
        print(f"❌ Erro ao verificar status: {error}")
        return False
    if output.strip():
        print("📝 Há alterações locais. Deseja commitar antes do pull? [s/N]")
        resp = input().strip().lower()
        if resp == 's':
            success, output, error = run_command("git add .", cwd=project_root)
            if not success:
                if "index.lock" in error:
                    print("🔓 Detectado arquivo de lock. Removendo e tentando novamente...")
                    clean_git_locks(project_root)
                    success, output, error = run_command("git add .", cwd=project_root)
                    if not success:
                        print(f"❌ Erro ao adicionar alterações: {error}")
                        return False
                else:
                    print(f"❌ Erro ao adicionar alterações: {error}")
                    return False
            print("Digite uma mensagem de commit personalizada (ou pressione Enter para mensagem automática):")
            msg = input().strip()
            if not msg:
                msg = f"Alterações locais antes do pull: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            success, output, error = run_command(f'git commit -m "{msg}"', cwd=project_root)
            if not success:
                print(f"❌ Erro ao fazer commit: {error}")
                return False
        else:
            print("⚠️ Pull será feito sem commit das alterações locais!")
    print("⬇️ Baixando alterações do repositório remoto...")
    success, output, error = run_command(f"git pull origin {branch}", cwd=project_root)
    if not success:
        if "conflict" in error.lower() or "merge" in error.lower():
            print("⚠️ Detectados conflitos durante o pull.")
            return handle_merge_conflicts(project_root, branch)
        else:
            print(f"❌ Erro no pull: {error}")
            return False
    print("✅ Sincronização concluída com sucesso.")
    return True

def ensure_git_repo(project_root):
    git_dir = os.path.join(project_root, '.git')
    if os.path.exists(git_dir):
        return True
    print("❌ Não foi encontrado um repositório Git neste diretório.")
    print("Deseja inicializar um novo repositório Git aqui? [S/n]")
    resp = input().strip().lower()
    if resp == 'n':
        print("Operação cancelada pelo usuário.")
        return False
    # Inicializa o repositório
    success, output, error = run_command("git init", cwd=project_root)
    if not success:
        print(f"❌ Erro ao inicializar o repositório: {error}")
        return False
    print("✅ Repositório Git inicializado.")
    print("Deseja adicionar um repositório remoto (GitHub, GitLab, etc)? [S/n]")
    resp = input().strip().lower()
    if resp == 'n':
        print("⚠️ Nenhum repositório remoto configurado. Você pode adicionar depois com 'git remote add origin <url>'")
        return True
    print("Digite a URL do repositório remoto (ex: https://github.com/usuario/repositorio.git):")
    url = input().strip()
    if not url:
        print("⚠️ Nenhuma URL informada. Você pode adicionar depois com 'git remote add origin <url>'")
        return True
    success, output, error = run_command(f"git remote add origin {url}", cwd=project_root)
    if not success:
        print(f"❌ Erro ao adicionar repositório remoto: {error}")
        return False
    print("✅ Repositório remoto adicionado.")
    print("Qual o nome da branch principal? [main]")
    branch = input().strip()
    if not branch:
        branch = 'main'
    # Cria branch principal se não existir
    success, output, error = run_command(f"git checkout -b {branch}", cwd=project_root)
    if not success and 'already exists' not in error:
        print(f"⚠️ Não foi possível criar branch {branch}: {error}")
    print(f"🌿 Branch principal definida: {branch}")
    # Verifica se já existe commit inicial
    success, output, error = run_command("git log --oneline", cwd=project_root)
    if success and output:
        print("⚠️ Este repositório já possui commits.")
        print("Deseja apenas atualizar o repositório (pull/push) ou fazer um commit inicial de todos os arquivos?")
        print("[1] Apenas atualizar (recomendado se já existe commit)")
        print("[2] Fazer commit inicial de todos os arquivos")
        escolha = input("Escolha 1 ou 2 [1]: ").strip()
        if escolha != '2':
            print("Seguindo para atualização normal do repositório...")
            return True
    print("Deseja fazer o primeiro commit de todos os arquivos? [S/n]")
    resp = input().strip().lower()
    if resp != 'n':
        run_command("git add .", cwd=project_root)
        msg = f"Primeiro commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        run_command(f'git commit -m "{msg}"', cwd=project_root)
        print("✅ Primeiro commit realizado.")
        print("Deseja enviar para o repositório remoto agora? [S/n]")
        resp = input().strip().lower()
        if resp != 'n':
            run_command(f"git push -u origin {branch}", cwd=project_root)
            print("🚀 Push inicial realizado.")
    print("Repositório Git pronto para uso!")
    return True

def move_venv_temporariamente(project_root):
    venv_path = os.path.join(project_root, '.venv')
    temp_path = os.path.join(project_root, '..', 'venv_temp')
    if os.path.exists(venv_path):
        print('🔄 Movendo .venv temporariamente para evitar conflito com o pull...')
        shutil.move(venv_path, temp_path)
        return True, temp_path
    return False, None

def restaura_venv(project_root, temp_path):
    venv_path = os.path.join(project_root, '.venv')
    if os.path.exists(temp_path):
        print('🔄 Restaurando .venv ao projeto...')
        shutil.move(temp_path, venv_path)
        return True
    return False

def adiciona_venv_gitignore(project_root):
    gitignore_path = os.path.join(project_root, '.gitignore')
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write('.venv/\n')
        print('✅ .venv/ adicionado ao .gitignore')
        return
    with open(gitignore_path, 'r+') as f:
        conteudo = f.read()
        if '.venv/' not in conteudo:
            f.write('\n.venv/\n')
            print('✅ .venv/ adicionado ao .gitignore')

def main():
    print("🔄 Iniciando atualização interativa do repositório Git...")
    project_root = get_project_root()
    print(f"📁 Diretório do projeto: {project_root}")
    clean_git_locks(project_root)
    if not ensure_git_repo(project_root):
        return False
    # Verifica se já existe commit
    success, output, error = run_command("git log --oneline", cwd=project_root)
    if not success or not output:
        print("⚠️ Este repositório ainda não possui nenhum commit.")
        print("O que deseja fazer?")
        print("[1] Commit e push de todos os arquivos locais para o GitHub (atualizar remoto com o que está aqui)")
        print("[2] Puxar histórico do repositório remoto (git pull origin <branch>)")
        print("[3] Sair")
        escolha = input("Escolha 1, 2 ou 3 [1]: ").strip()
        if escolha == '3':
            print("Operação cancelada pelo usuário.")
            return False
        if escolha == '1' or escolha == '':
            print("Adicionando todos os arquivos ao controle de versão...")
            run_command("git add .", cwd=project_root)
            msg = input("Digite a mensagem do commit (ou pressione Enter para mensagem padrão): ").strip()
            if not msg:
                msg = f"Atualização do sistema local para o GitHub: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            success, output, error = run_command(f'git commit -m "{msg}"', cwd=project_root)
            if not success and 'nothing to commit' in output + error:
                print("Nenhuma alteração para commitar.")
            elif not success:
                print(f"❌ Erro ao fazer commit: {error}")
                return False
            else:
                print("✅ Commit realizado com sucesso.")
            print("Enviando alterações para o GitHub...")
            success, output, error = run_command("git push origin main", cwd=project_root)
            if not success:
                print(f"❌ Erro ao fazer push: {error}")
                print("Se o erro for de histórico divergente, rode um pull/rebase manualmente.")
                return False
            print("🚀 Push realizado com sucesso! Seu repositório remoto está atualizado.")
            return True
        # O resto do fluxo segue como já está para a opção 2
    # Descobre branch atual
    success, branch, error = run_command("git rev-parse --abbrev-ref HEAD", cwd=project_root)
    if not success:
        print(f"❌ Erro ao obter branch atual: {error}")
        return False
    print(f"🌿 Branch atual: {branch}")
    if not sync_with_remote(project_root, branch):
        print("❌ Falha na sincronização com o repositório remoto.")
        return False
    success, output, error = run_command("git status --porcelain", cwd=project_root)
    if not success:
        print(f"❌ Erro ao verificar status do Git: {error}")
        return False
    if not output.strip():
        print("✅ Nenhuma alteração para enviar.")
        return True
    print("📝 Alterações detectadas:")
    print(output)
    print("Deseja adicionar e commitar essas alterações? [S/n]")
    resp = input().strip().lower()
    if resp == 'n':
        print("❌ Commit cancelado pelo usuário.")
        return False
    print("Digite uma mensagem de commit personalizada (ou pressione Enter para mensagem automática):")
    msg = input().strip()
    if not msg:
        msg = f"Atualização automática: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"📦 Adicionando alterações...")
    success, output, error = run_command("git add .", cwd=project_root)
    if not success:
        if "index.lock" in error:
            print("🔓 Detectado arquivo de lock. Removendo e tentando novamente...")
            clean_git_locks(project_root)
            success, output, error = run_command("git add .", cwd=project_root)
            if not success:
                print(f"❌ Erro ao adicionar alterações: {error}")
                return False
        else:
            print(f"❌ Erro ao adicionar alterações: {error}")
            return False
    print(f"💾 Fazendo commit: {msg}")
    success, output, error = run_command(f'git commit -m "{msg}"', cwd=project_root)
    if not success:
        print(f"❌ Erro ao fazer commit: {error}")
        return False
    print(f"✅ Commit realizado: {output}")
    print("Deseja fazer push para o GitHub agora? [S/n]")
    resp = input().strip().lower()
    if resp == 'n':
        print("⚠️ Push cancelado pelo usuário. Você pode fazer push manualmente depois.")
        return True
    print(f"🚀 Enviando para o GitHub...")
    success, output, error = run_command(f"git push origin {branch}", cwd=project_root)
    if not success:
        if "non-fast-forward" in error or "behind" in error:
            print("⚠️ Repositório local desatualizado. Tentando sincronizar novamente...")
            if sync_with_remote(project_root, branch):
                success, output, error = run_command(f"git push origin {branch}", cwd=project_root)
                if not success:
                    print(f"❌ Erro ao fazer push após sincronização: {error}")
                    return False
            else:
                print("❌ Falha na sincronização.")
                return False
        else:
            print(f"❌ Erro ao fazer push: {error}")
            return False
    print(f"✅ Alterações enviadas para o GitHub na branch {branch}!")
    print(f"📤 Push realizado com sucesso: {output}")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Atualização concluída com sucesso!")
        else:
            print("\n💥 Falha na atualização!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Operação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        sys.exit(1) 