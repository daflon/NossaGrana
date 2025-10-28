#!/usr/bin/env python3
"""
Script de deploy automatizado para produção
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description=""):
    """Executa um comando e verifica se foi bem-sucedido"""
    print(f"\nExecutando: {description}")
    print(f"Executando: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"OK: {description} - Sucesso")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"ERRO: {description} - Erro")
        print(f"Erro: {result.stderr}")
        return False
    
    return True

def check_prerequisites():
    """Verifica se os pré-requisitos estão instalados"""
    print("Verificando pre-requisitos...")
    
    prerequisites = [
        ("docker", "Docker"),
        ("docker-compose", "Docker Compose")
    ]
    
    for cmd, name in prerequisites:
        if not run_command(f"{cmd} --version", f"Verificando {name}"):
            print(f"ERRO: {name} nao esta instalado ou nao esta no PATH")
            return False
    
    return True

def backup_database():
    """Cria backup do banco de dados atual"""
    print("\nCriando backup do banco de dados...")
    
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{timestamp}.sql"
    
    # Se já existe um container rodando, faz backup
    result = subprocess.run("docker-compose ps -q db", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        backup_cmd = f"docker-compose exec -T db pg_dump -U nossa_grana_user nossa_grana_prod > {backup_file}"
        if run_command(backup_cmd, "Criando backup do PostgreSQL"):
            print(f"OK: Backup criado: {backup_file}")
        else:
            print("AVISO: Nao foi possivel criar backup - continuando deploy")
    else:
        print("INFO: Nenhum banco de dados rodando - pulando backup")

def build_and_deploy():
    """Constrói e faz deploy da aplicação"""
    print("\nConstruindo e fazendo deploy...")
    
    steps = [
        ("docker-compose -f docker-compose.prod.yml down", "Parando containers existentes"),
        ("docker-compose -f docker-compose.prod.yml build --no-cache", "Construindo imagens"),
        ("docker-compose -f docker-compose.prod.yml up -d", "Iniciando containers"),
    ]
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            return False
    
    return True

def run_migrations():
    """Executa migrações do banco de dados"""
    print("\nExecutando migracoes...")
    
    # Aguarda o banco estar pronto
    print("Aguardando banco de dados ficar pronto...")
    time.sleep(10)
    
    migration_cmd = "docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate --settings=nossa_grana.settings_prod"
    return run_command(migration_cmd, "Executando migrações")

def collect_static():
    """Coleta arquivos estáticos"""
    print("\nColetando arquivos estaticos...")
    
    static_cmd = "docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput --settings=nossa_grana.settings_prod"
    return run_command(static_cmd, "Coletando arquivos estáticos")

def create_superuser():
    """Cria superusuário se não existir"""
    print("\nVerificando superusuario...")
    
    # Script para criar superuser
    create_user_script = '''
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@nossagrana.com", "admin123")
    print("Superusuario criado: admin/admin123")
else:
    print("Superusuario ja existe")
'''
    
    # Salva script temporário
    with open("create_superuser.py", "w") as f:
        f.write(create_user_script)
    
    # Executa script
    cmd = "docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell --settings=nossa_grana.settings_prod < create_superuser.py"
    result = run_command(cmd, "Criando superusuário")
    
    # Remove script temporário
    os.remove("create_superuser.py")
    
    return result

def health_check():
    """Verifica se a aplicação está funcionando"""
    print("\nVerificando saude da aplicacao...")
    
    import requests
    import time
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost/api/health/", timeout=5)
            if response.status_code == 200:
                print("OK: Aplicacao esta respondendo corretamente")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Tentativa {attempt + 1}/{max_attempts} - Aguardando aplicacao...")
        time.sleep(2)
    
    print("ERRO: Aplicacao nao esta respondendo apos 60 segundos")
    return False

def show_status():
    """Mostra status dos containers"""
    print("\nStatus dos containers:")
    run_command("docker-compose -f docker-compose.prod.yml ps", "Status dos containers")

def main():
    """Função principal do deploy"""
    print("Iniciando deploy de producao do Nossa Grana")
    print("=" * 50)
    
    # Verifica pré-requisitos
    if not check_prerequisites():
        sys.exit(1)
    
    # Confirma deploy
    response = input("\nTem certeza que deseja fazer deploy em producao? (y/N): ")
    if response.lower() != 'y':
        print("Deploy cancelado")
        sys.exit(0)
    
    try:
        # Backup
        backup_database()
        
        # Deploy
        if not build_and_deploy():
            print("ERRO: Falha no deploy")
            sys.exit(1)
        
        # Migrações
        if not run_migrations():
            print("ERRO: Falha nas migracoes")
            sys.exit(1)
        
        # Arquivos estáticos
        if not collect_static():
            print("ERRO: Falha na coleta de arquivos estaticos")
            sys.exit(1)
        
        # Superusuário
        create_superuser()
        
        # Verificação de saúde
        if not health_check():
            print("AVISO: Aplicacao pode nao estar funcionando corretamente")
        
        # Status final
        show_status()
        
        print("\nDeploy concluido com sucesso!")
        print("Aplicacao disponivel em: https://localhost")
        print("Admin disponivel em: https://localhost/admin")
        print("Logs: docker-compose -f docker-compose.prod.yml logs -f")
        
    except KeyboardInterrupt:
        print("\n\nDeploy interrompido pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO durante o deploy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()