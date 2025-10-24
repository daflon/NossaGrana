#!/usr/bin/env python
"""
Script para configurar o banco de dados inicial
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
    django.setup()

    print("🚀 Configurando banco de dados do Nossa Grana...")
    
    # Criar migrações
    print("\n📝 Criando migrações...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # Aplicar migrações
    print("\n🔄 Aplicando migrações...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Carregar dados iniciais
    print("\n📊 Carregando dados iniciais...")
    try:
        execute_from_command_line(['manage.py', 'load_initial_data'])
    except Exception as e:
        print(f"⚠️  Aviso: {e}")
    
    print("\n✅ Configuração concluída!")
    print("\n📋 Próximos passos:")
    print("1. Criar um superusuário: python manage.py createsuperuser")
    print("2. Iniciar o servidor: python manage.py runserver")
    print("3. Acessar o admin: http://localhost:8000/admin")
    print("4. Acessar a API: http://localhost:8000/api")