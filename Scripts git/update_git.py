#!/usr/bin/env python3
"""
Script de atalho para atualizar o repositório Git
Execute diretamente: python update_git.py
"""

import sys
import os
import subprocess
from datetime import datetime

def run_command(command, cwd=None):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd or os.getcwd()
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_git_status():
    """Verifica o status atual do Git"""
    print("🔍 Verificando status do repositório...")
    
    success, output, error = run_command("git status --porcelain")
    if not success:
        print(f"❌ Erro ao verificar status: {error}")
        return False
    
    if not output.strip():
        print("✅ Nenhuma alteração pendente.")
        return True
    
    print("📝 Alterações detectadas:")
    for line in output.split('\n'):
        if line.strip():
            status = line[:2].strip()
            file_path = line[3:]
            if status == 'M':
                print(f"   📝 Modificado: {file_path}")
            elif status == 'A':
                print(f"   ➕ Adicionado: {file_path}")
            elif status == 'D':
                print(f"   🗑️ Removido: {file_path}")
            else:
                print(f"   ❓ {status}: {file_path}")
    
    return True

def clean_git_locks():
    """Remove arquivos de lock do Git"""
    lock_files = [
        '.git/index.lock',
        '.git/MERGE_HEAD.lock',
        '.git/refs/heads/main.lock'
    ]
    
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                print(f"🔓 Removido arquivo de lock: {lock_file}")
            except Exception as e:
                print(f"⚠️ Não foi possível remover {lock_file}: {e}")

def main():
    """Função principal"""
    print("🚀 Script de Atualização Git - SGFP")
    print("=" * 50)
    
    # Verifica se estamos em um repositório Git
    if not os.path.exists('.git'):
        print("❌ Não é um repositório Git!")
        print("💡 Execute primeiro: python setup_github.py")
        sys.exit(1)
    
    # Verifica se o script V2 existe
    script_v2_path = os.path.join("Scripts git", "atualiza_git_v2.py")
    if os.path.exists(script_v2_path):
        print("🔄 Usando script de atualização V2...")
        
        # Adiciona o diretório dos scripts ao path
        script_dir = os.path.join(os.path.dirname(__file__), "Scripts git")
        sys.path.insert(0, script_dir)
        
        try:
            import atualiza_git_v2
            print("🚀 Executando script de atualização Git V2...")
            atualiza_git_v2.main()
        except ImportError as e:
            print(f"❌ Erro ao importar script V2: {e}")
            print("📁 Verifique se o arquivo 'Scripts git/atualiza_git_v2.py' existe.")
            sys.exit(1)
        except Exception as e:
            print(f"💥 Erro inesperado: {e}")
            sys.exit(1)
    else:
        print("⚠️ Script V2 não encontrado. Usando método básico...")
        
        # Método básico de atualização
        try:
            # Limpa locks
            clean_git_locks()
            
            # Verifica status
            if not check_git_status():
                sys.exit(1)
            
            # Adiciona alterações
            print("📦 Adicionando alterações...")
            success, output, error = run_command("git add .")
            if not success:
                print(f"❌ Erro ao adicionar alterações: {error}")
                sys.exit(1)
            
            # Commit
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_message = f"🔄 Atualização automática: {timestamp}"
            
            print(f"💾 Fazendo commit: {commit_message}")
            success, output, error = run_command(f'git commit -m "{commit_message}"')
            if not success:
                print(f"❌ Erro ao fazer commit: {error}")
                sys.exit(1)
            
            # Push
            print("🚀 Enviando para o GitHub...")
            success, output, error = run_command("git push origin main")
            if not success:
                print(f"❌ Erro ao fazer push: {error}")
                sys.exit(1)
            
            print("✅ Atualização concluída com sucesso!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Operação cancelada pelo usuário.")
            sys.exit(1)
        except Exception as e:
            print(f"\n💥 Erro inesperado: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main() 