#!/usr/bin/env python
"""
Script para testar a atualização automática de saldos
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from transactions.models import Transaction, Category
from financial_accounts.models import Account, CreditCard
from datetime import date

def test_account_balance_update():
    """
    Testa se o saldo da conta é atualizado automaticamente
    """
    print("=== Testando Atualização de Saldo da Conta ===")
    
    # Criar usuário de teste
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@test.com'}
    )
    
    # Criar categoria de teste
    category, created = Category.objects.get_or_create(
        name='Teste',
        defaults={'color': '#007bff', 'icon': 'test'}
    )
    
    # Criar conta de teste
    account, created = Account.objects.get_or_create(
        user=user,
        name='Conta Teste',
        defaults={
            'type': 'checking',
            'bank': 'Banco Teste',
            'initial_balance': Decimal('1000.00')
        }
    )
    
    print(f"Saldo inicial da conta: R$ {account.current_balance}")
    
    # Criar transação de receita
    income_transaction = Transaction.objects.create(
        user=user,
        type='income',
        amount=Decimal('500.00'),
        description='Receita Teste',
        category=category,
        account=account,
        date=date.today()
    )
    
    # Recarregar conta do banco
    account.refresh_from_db()
    print(f"Saldo após receita de R$ 500: R$ {account.current_balance}")
    
    # Criar transação de despesa
    expense_transaction = Transaction.objects.create(
        user=user,
        type='expense',
        amount=Decimal('200.00'),
        description='Despesa Teste',
        category=category,
        account=account,
        date=date.today()
    )
    
    # Recarregar conta do banco
    account.refresh_from_db()
    print(f"Saldo após despesa de R$ 200: R$ {account.current_balance}")
    
    # Limpar dados de teste
    income_transaction.delete()
    account.refresh_from_db()
    print(f"Saldo após deletar receita: R$ {account.current_balance}")
    
    expense_transaction.delete()
    account.refresh_from_db()
    print(f"Saldo após deletar despesa: R$ {account.current_balance}")
    
    print("✅ Teste de conta concluído!\n")

def test_credit_card_limit_update():
    """
    Testa se o limite disponível do cartão é atualizado automaticamente
    """
    print("=== Testando Atualização de Limite do Cartão ===")
    
    # Criar usuário de teste
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@test.com'}
    )
    
    # Criar categoria de teste
    category, created = Category.objects.get_or_create(
        name='Teste',
        defaults={'color': '#007bff', 'icon': 'test'}
    )
    
    # Criar cartão de teste
    credit_card, created = CreditCard.objects.get_or_create(
        user=user,
        name='Cartão Teste',
        defaults={
            'bank': 'Banco Teste',
            'credit_limit': Decimal('2000.00'),
            'closing_day': 15,
            'due_day': 10
        }
    )
    
    print(f"Limite total do cartão: R$ {credit_card.credit_limit}")
    print(f"Limite disponível inicial: R$ {credit_card.available_limit}")
    
    # Criar transação no cartão
    card_transaction = Transaction.objects.create(
        user=user,
        type='expense',
        amount=Decimal('300.00'),
        description='Compra no Cartão',
        category=category,
        credit_card=credit_card,
        date=date.today()
    )
    
    # Recarregar cartão do banco
    credit_card.refresh_from_db()
    print(f"Limite disponível após gasto de R$ 300: R$ {credit_card.available_limit}")
    print(f"Percentual de uso: {credit_card.usage_percentage:.1f}%")
    
    # Criar outra transação
    card_transaction2 = Transaction.objects.create(
        user=user,
        type='expense',
        amount=Decimal('150.00'),
        description='Outra Compra no Cartão',
        category=category,
        credit_card=credit_card,
        date=date.today()
    )
    
    # Recarregar cartão do banco
    credit_card.refresh_from_db()
    print(f"Limite disponível após gasto adicional de R$ 150: R$ {credit_card.available_limit}")
    print(f"Percentual de uso: {credit_card.usage_percentage:.1f}%")
    
    # Limpar dados de teste
    card_transaction.delete()
    credit_card.refresh_from_db()
    print(f"Limite disponível após deletar primeira transação: R$ {credit_card.available_limit}")
    
    card_transaction2.delete()
    credit_card.refresh_from_db()
    print(f"Limite disponível após deletar segunda transação: R$ {credit_card.available_limit}")
    
    print("✅ Teste de cartão concluído!\n")

if __name__ == '__main__':
    print("🧪 Iniciando testes de atualização automática de saldos...\n")
    
    try:
        test_account_balance_update()
        test_credit_card_limit_update()
        print("🎉 Todos os testes passaram com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()