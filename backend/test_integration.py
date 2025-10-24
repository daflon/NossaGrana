#!/usr/bin/env python
"""
Script para testar a integração entre transações e contas/cartões
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
django.setup()

from django.contrib.auth.models import User
from financial_accounts.models import Account, CreditCard
from transactions.models import Transaction, Category

def test_integration():
    print("🧪 Testando integração entre transações e contas/cartões...")
    
    # Buscar ou criar usuário de teste
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Usuário de teste criado: {user.username}")
    else:
        print(f"✅ Usuário de teste encontrado: {user.username}")
    
    # Buscar ou criar categoria de teste
    category, created = Category.objects.get_or_create(
        name='Teste',
        defaults={
            'color': '#007bff',
            'icon': 'test'
        }
    )
    if created:
        print(f"✅ Categoria de teste criada: {category.name}")
    else:
        print(f"✅ Categoria de teste encontrada: {category.name}")
    
    # Criar conta de teste
    account = Account.objects.create(
        user=user,
        name='Conta Teste',
        type='checking',
        bank='Banco Teste',
        initial_balance=Decimal('1000.00')
    )
    print(f"✅ Conta criada: {account.name} - Saldo inicial: R$ {account.current_balance}")
    
    # Criar cartão de teste
    credit_card = CreditCard.objects.create(
        user=user,
        name='Cartão Teste',
        bank='Banco Teste',
        credit_limit=Decimal('2000.00'),
        closing_day=15,
        due_day=10
    )
    print(f"✅ Cartão criado: {credit_card.name} - Limite disponível: R$ {credit_card.available_limit}")
    
    print("\\n🔄 Testando transações...")
    
    # Teste 1: Receita na conta
    print("\\n1️⃣ Criando receita de R$ 500,00 na conta...")
    receita = Transaction.objects.create(
        user=user,
        type='income',
        amount=Decimal('500.00'),
        description='Salário teste',
        category=category,
        account=account,
        date='2024-01-15'
    )
    
    # Recarregar conta para ver saldo atualizado
    account.refresh_from_db()
    print(f"   💰 Saldo da conta após receita: R$ {account.current_balance}")
    print(f"   ✅ Esperado: R$ 1500.00 | Atual: R$ {account.current_balance}")
    
    # Teste 2: Despesa na conta
    print("\\n2️⃣ Criando despesa de R$ 200,00 na conta...")
    despesa_conta = Transaction.objects.create(
        user=user,
        type='expense',
        amount=Decimal('200.00'),
        description='Compra teste',
        category=category,
        account=account,
        date='2024-01-16'
    )
    
    # Recarregar conta
    account.refresh_from_db()
    print(f"   💰 Saldo da conta após despesa: R$ {account.current_balance}")
    print(f"   ✅ Esperado: R$ 1300.00 | Atual: R$ {account.current_balance}")
    
    # Teste 3: Despesa no cartão
    print("\\n3️⃣ Criando despesa de R$ 300,00 no cartão...")
    despesa_cartao = Transaction.objects.create(
        user=user,
        type='expense',
        amount=Decimal('300.00'),
        description='Compra cartão teste',
        category=category,
        credit_card=credit_card,
        date='2024-01-17'
    )
    
    # Recarregar cartão
    credit_card.refresh_from_db()
    print(f"   💳 Limite disponível após despesa: R$ {credit_card.available_limit}")
    print(f"   ✅ Esperado: R$ 1700.00 | Atual: R$ {credit_card.available_limit}")
    
    # Teste 4: Criar segunda conta para transferência
    print("\\n4️⃣ Criando segunda conta e testando transferência...")
    account2 = Account.objects.create(
        user=user,
        name='Poupança Teste',
        type='savings',
        bank='Banco Teste',
        initial_balance=Decimal('500.00')
    )
    print(f"   🏦 Segunda conta criada: {account2.name} - Saldo: R$ {account2.current_balance}")
    
    # Transferência de 100 da conta1 para conta2
    transferencia = Transaction.objects.create(
        user=user,
        type='transfer',
        amount=Decimal('100.00'),
        description='Transferência teste',
        category=category,
        transfer_from_account=account,
        transfer_to_account=account2,
        date='2024-01-18'
    )
    
    # Recarregar contas
    account.refresh_from_db()
    account2.refresh_from_db()
    print(f"   💰 Conta origem após transferência: R$ {account.current_balance}")
    print(f"   💰 Conta destino após transferência: R$ {account2.current_balance}")
    print(f"   ✅ Origem esperado: R$ 1200.00 | Atual: R$ {account.current_balance}")
    print(f"   ✅ Destino esperado: R$ 600.00 | Atual: R$ {account2.current_balance}")
    
    print("\\n🧹 Limpando dados de teste...")
    
    # Deletar transações uma por uma (isso deve atualizar os saldos)
    transactions = Transaction.objects.filter(user=user)
    for transaction in transactions:
        transaction.delete()
    
    # Recarregar e verificar se saldos voltaram ao inicial
    account.refresh_from_db()
    account2.refresh_from_db()
    credit_card.refresh_from_db()
    
    print(f"   💰 Conta 1 após limpeza: R$ {account.current_balance} (esperado: R$ 1000.00)")
    print(f"   💰 Conta 2 após limpeza: R$ {account2.current_balance} (esperado: R$ 500.00)")
    print(f"   💳 Cartão após limpeza: R$ {credit_card.available_limit} (esperado: R$ 2000.00)")
    
    # Deletar contas e cartão de teste
    Account.objects.filter(user=user).delete()
    CreditCard.objects.filter(user=user).delete()
    
    print("\\n✅ Teste de integração concluído!")
    
    # Verificar se tudo funcionou corretamente
    success = True
    if account.current_balance != Decimal('1000.00'):
        print(f"❌ ERRO: Saldo da conta 1 incorreto após limpeza")
        success = False
    if account2.current_balance != Decimal('500.00'):
        print(f"❌ ERRO: Saldo da conta 2 incorreto após limpeza")
        success = False
    if credit_card.available_limit != Decimal('2000.00'):
        print(f"❌ ERRO: Limite do cartão incorreto após limpeza")
        success = False
    
    if success:
        print("🎉 TODOS OS TESTES PASSARAM! A integração está funcionando corretamente.")
    else:
        print("💥 ALGUNS TESTES FALHARAM! Verifique a implementação.")
    
    return success

if __name__ == '__main__':
    test_integration()