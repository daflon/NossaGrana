#!/usr/bin/env python
"""
Script para inicializar o banco de dados com dados essenciais
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from transactions.models import Category
from transactions.management.commands.create_default_categories import Command as CategoryCommand

def init_database():
    """Inicializa o banco de dados com dados essenciais"""
    
    print("🔄 Aplicando migrações...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("📂 Criando categorias padrão...")
    try:
        category_command = CategoryCommand()
        category_command.handle()
        print("✅ Categorias criadas com sucesso!")
    except Exception as e:
        print(f"⚠️  Erro ao criar categorias: {e}")
    
    print("👤 Criando superusuário de teste...")
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@nossagrana.com',
                password='admin123'
            )
            print("✅ Superusuário criado: admin/admin123")
        else:
            print("ℹ️  Superusuário já existe")
    except Exception as e:
        print(f"⚠️  Erro ao criar superusuário: {e}")
    
    print("🎯 Banco de dados inicializado com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Execute: python manage.py runserver")
    print("2. Acesse: http://localhost:8000/admin")
    print("3. Login: admin / admin123")

if __name__ == '__main__':
    init_database()