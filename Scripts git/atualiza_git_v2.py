#!/usr/bin/env python3
"""
Script Python V2 para atualizar o repositório Git automaticamente
Versão melhorada com mensagens de commit personalizadas e tratamento robusto de erros
Execute: python atualiza_git_v2.py
"""

import subprocess
import sys
import os
import re
from datetime import datetime
from typing import Tuple, List, Optional

class GitUpdater:
    def __init__(self):
        self.project_root = self.get_project_root()
        self.branch = None
        self.changes_detected = []
        
    def run_command(self, command: str, cwd: Optional[str] = None) -> Tuple[bool, str, str]:
        """Executa um comando e retorna (sucesso, stdout, stderr)"""
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

    def get_project_root(self) -> str:
        """Obtém o diretório raiz do projeto"""
        current_dir = os.getcwd()
        while current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, '.git')):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        return os.getcwd()

    def clean_git_locks(self) -> None:
        """Remove arquivos de lock do Git se existirem"""
        lock_files = [
            os.path.join(self.project_root, '.git', 'index.lock'),
            os.path.join(self.project_root, '.git', 'MERGE_HEAD.lock'),
            os.path.join(self.project_root, '.git', 'refs', 'heads', 'main.lock')
        ]
        
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                    print(f"🔓 Removido arquivo de lock: {os.path.basename(lock_file)}")
                except Exception as e:
                    print(f"⚠️ Não foi possível remover {os.path.basename(lock_file)}: {e}")

    def analyze_changes(self) -> List[str]:
        """Analisa as alterações e retorna uma lista de mudanças"""
        success, output, error = self.run_command("git status --porcelain")
        if not success:
            return []
        
        changes = []
        for line in output.split('\n'):
            if line.strip():
                status = line[:2].strip()
                file_path = line[3:]
                
                if status == 'M':
                    changes.append(f"📝 Modificado: {file_path}")
                elif status == 'A':
                    changes.append(f"➕ Adicionado: {file_path}")
                elif status == 'D':
                    changes.append(f"🗑️ Removido: {file_path}")
                elif status == 'R':
                    changes.append(f"🔄 Renomeado: {file_path}")
                else:
                    changes.append(f"❓ {status}: {file_path}")
        
        return changes

    def generate_commit_message(self) -> str:
        """Gera uma mensagem de commit personalizada baseada nas alterações"""
        if not self.changes_detected:
            return f"🔄 Atualização automática: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Analisa os tipos de alterações
        modified_files = []
        added_files = []
        removed_files = []
        
        for change in self.changes_detected:
            if "Modificado:" in change:
                modified_files.append(change.split("Modificado: ")[1])
            elif "Adicionado:" in change:
                added_files.append(change.split("Adicionado: ")[1])
            elif "Removido:" in change:
                removed_files.append(change.split("Removido: ")[1])
        
        # Gera mensagem baseada no tipo de alteração
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if len(modified_files) > 0 and len(added_files) == 0 and len(removed_files) == 0:
            # Apenas modificações
            if len(modified_files) == 1:
                return f"🔧 Atualização: {modified_files[0]} - {timestamp}"
            else:
                return f"🔧 Atualizações em {len(modified_files)} arquivos - {timestamp}"
        
        elif len(added_files) > 0:
            # Novos arquivos
            if len(added_files) == 1:
                return f"✨ Novo arquivo: {added_files[0]} - {timestamp}"
            else:
                return f"✨ {len(added_files)} novos arquivos adicionados - {timestamp}"
        
        elif len(removed_files) > 0:
            # Arquivos removidos
            if len(removed_files) == 1:
                return f"🗑️ Removido: {removed_files[0]} - {timestamp}"
            else:
                return f"🗑️ {len(removed_files)} arquivos removidos - {timestamp}"
        
        else:
            # Múltiplos tipos de alteração
            total_changes = len(self.changes_detected)
            return f"🔄 {total_changes} alterações realizadas - {timestamp}"

    def handle_merge_conflicts(self) -> bool:
        """Trata conflitos de merge automaticamente"""
        print("⚠️ Detectados conflitos de merge. Tentando resolver...")
        
        success, output, error = self.run_command("git status --porcelain")
        if not success:
            print(f"❌ Erro ao verificar status: {error}")
            return False
        
        if "UU" in output:
            print("🔧 Detectados arquivos com conflitos. Tentando resolver...")
            
            # Para arquivos de log, sobrescreve automaticamente
            if "logs/sgfp.log" in output:
                print("📝 Detectado arquivo de log com conflito. Sobrescrevendo...")
                success, output, error = self.run_command("git checkout --ours logs/sgfp.log")
                if success:
                    success, output, error = self.run_command("git add logs/sgfp.log")
                    if success:
                        print("✅ Conflito no arquivo de log resolvido.")
                    else:
                        print(f"❌ Erro ao adicionar arquivo de log: {error}")
                        return False
                else:
                    print(f"❌ Erro ao resolver conflito no log: {error}")
                    return False
            
            # Finaliza o merge
            success, output, error = self.run_command("git commit --no-edit")
            if success:
                print("✅ Merge concluído com sucesso.")
                return True
            else:
                print(f"❌ Erro ao finalizar merge: {error}")
                return False
        
        return True

    def sync_with_remote(self) -> bool:
        """Sincroniza com o repositório remoto"""
        print("🔄 Sincronizando com o repositório remoto...")
        
        self.clean_git_locks()
        
        # Verifica alterações locais
        success, output, error = self.run_command("git status --porcelain")
        if not success:
            print(f"❌ Erro ao verificar status: {error}")
            return False
        
        if output.strip():
            print("📝 Há alterações locais. Fazendo commit antes do pull...")
            
            # Adiciona alterações
            success, output, error = self.run_command("git add .")
            if not success:
                if "index.lock" in error:
                    print("🔓 Detectado arquivo de lock. Removendo e tentando novamente...")
                    self.clean_git_locks()
                    success, output, error = self.run_command("git add .")
                    if not success:
                        print(f"❌ Erro ao adicionar alterações: {error}")
                        return False
                else:
                    print(f"❌ Erro ao adicionar alterações: {error}")
                    return False
            
            # Commit com mensagem personalizada
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_message = f"🔄 Sincronização local: {timestamp}"
            
            success, output, error = self.run_command(f'git commit -m "{commit_message}"')
            if not success:
                print(f"❌ Erro ao fazer commit: {error}")
                return False
        
        # Pull das alterações remotas
        print("⬇️ Baixando alterações do repositório remoto...")
        success, output, error = self.run_command(f"git pull origin {self.branch}")
        
        if not success:
            if "conflict" in error.lower() or "merge" in error.lower():
                print("⚠️ Detectados conflitos durante o pull.")
                return self.handle_merge_conflicts()
            else:
                print(f"❌ Erro no pull: {error}")
                return False
        
        print("✅ Sincronização concluída com sucesso.")
        return True

    def update_repository(self) -> bool:
        """Função principal para atualizar o repositório"""
        print("🚀 Iniciando atualização do repositório Git...")
        print(f"📁 Diretório do projeto: {self.project_root}")
        
        # Limpa locks no início
        self.clean_git_locks()
        
        # Obtém branch atual
        success, self.branch, error = self.run_command("git rev-parse --abbrev-ref HEAD")
        if not success:
            print(f"❌ Erro ao obter branch atual: {error}")
            return False
        
        print(f"🌿 Branch atual: {self.branch}")
        
        # Sincroniza com remoto
        if not self.sync_with_remote():
            print("❌ Falha na sincronização com o repositório remoto.")
            return False
        
        # Verifica alterações após pull
        success, output, error = self.run_command("git status --porcelain")
        if not success:
            print(f"❌ Erro ao verificar status do Git: {error}")
            return False
        
        if not output.strip():
            print("✅ Nenhuma alteração para enviar.")
            return True
        
        # Analisa alterações
        self.changes_detected = self.analyze_changes()
        print("📝 Alterações detectadas:")
        for change in self.changes_detected:
            print(f"   {change}")
        
        # Adiciona alterações
        print("📦 Adicionando alterações...")
        success, output, error = self.run_command("git add .")
        if not success:
            if "index.lock" in error:
                print("🔓 Detectado arquivo de lock. Removendo e tentando novamente...")
                self.clean_git_locks()
                success, output, error = self.run_command("git add .")
                if not success:
                    print(f"❌ Erro ao adicionar alterações: {error}")
                    return False
            else:
                print(f"❌ Erro ao adicionar alterações: {error}")
                return False
        
        # Gera mensagem de commit personalizada
        commit_message = self.generate_commit_message()
        print(f"💾 Fazendo commit: {commit_message}")
        
        success, output, error = self.run_command(f'git commit -m "{commit_message}"')
        if not success:
            print(f"❌ Erro ao fazer commit: {error}")
            return False
        
        print(f"✅ Commit realizado: {output}")
        
        # Push para o GitHub
        print(f"🚀 Enviando para o GitHub...")
        success, output, error = self.run_command(f"git push origin {self.branch}")
        if not success:
            if "non-fast-forward" in error or "behind" in error:
                print("⚠️ Repositório local desatualizado. Tentando sincronizar novamente...")
                if self.sync_with_remote():
                    success, output, error = self.run_command(f"git push origin {self.branch}")
                    if not success:
                        print(f"❌ Erro ao fazer push após sincronização: {error}")
                        return False
                else:
                    print("❌ Falha na sincronização.")
                    return False
            else:
                print(f"❌ Erro ao fazer push: {error}")
                return False
        
        print(f"✅ Alterações enviadas para o GitHub na branch {self.branch}!")
        print(f"📤 Push realizado com sucesso: {output}")
        
        return True

def main():
    """Função principal"""
    try:
        updater = GitUpdater()
        success = updater.update_repository()
        
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

if __name__ == "__main__":
    main() 