#!/usr/bin/env python
"""
Testes Simplificados - Nossa Grana (compatível com Windows)
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
from rest_framework.test import APIClient
from transactions.models import Transaction, Category
from financial_accounts.models import Account, CreditCard

def test_system():
    """Teste simplificado do sistema"""
    print("INICIANDO TESTES SIMPLIFICADOS")
    print("=" * 50)
    
    client = APIClient()
    
    # Criar usuário
    user, created = User.objects.get_or_create(
        username='test_simple',
        defaults={'email': 'test@test.com'}
    )
    if created:
        user.set_password('test123')
        user.save()
    client.force_authenticate(user=user)
    
    # Teste 1: Criar conta
    print("Teste 1: Criando conta...")
    account_data = {
        'name': 'Conta Teste',
        'type': 'checking',
        'bank': 'Banco Teste',
        'initial_balance': '1000.00',
        'is_active': True
    }
    response = client.post('/api/financial/accounts/', account_data)
    assert response.status_code == 201, f"Erro ao criar conta: {response.status_code}"
    account_id = response.json()['id']
    print("OK - Conta criada")
    
    # Teste 2: Criar cartão
    print("Teste 2: Criando cartão...")
    card_data = {
        'name': 'Cartão Teste',
        'bank': 'Banco Teste',
        'credit_limit': '2000.00',
        'closing_day': 15,
        'due_day': 25  # 10 dias após o fechamento
    }
    response = client.post('/api/financial/credit-cards/', card_data)
    if response.status_code != 201:
        print(f"Erro detalhado: {response.json()}")
    assert response.status_code == 201, f"Erro ao criar cartão: {response.status_code}"
    card_id = response.json()['id']
    print("OK - Cartão criado")
    
    # Teste 3: Criar transação
    print("Teste 3: Criando transação...")
    category = Category.objects.first()
    transaction_data = {
        'type': 'income',
        'amount': '500.00',
        'description': 'Teste receita',
        'category': category.id,
        'account': account_id,
        'date': '2024-01-01'
    }
    response = client.post('/api/transactions/transactions/', transaction_data)
    assert response.status_code == 201, f"Erro ao criar transação: {response.status_code}"
    print("OK - Transação criada")
    
    # Teste 4: Verificar saldo
    print("Teste 4: Verificando saldo...")
    response = client.get(f'/api/financial/accounts/{account_id}/')
    account_data = response.json()
    expected_balance = Decimal('1500.00')  # 1000 + 500
    actual_balance = Decimal(str(account_data['current_balance']))
    assert actual_balance == expected_balance, f"Saldo incorreto: {actual_balance} != {expected_balance}"
    print("OK - Saldo correto")
    
    # Teste 5: Transferência
    print("Teste 5: Testando transferência...")
    # Criar segunda conta
    account2_data = {
        'name': 'Conta Destino',
        'type': 'savings',
        'bank': 'Banco Teste',
        'initial_balance': '0.00',
        'is_active': True
    }
    response = client.post('/api/financial/accounts/', account2_data)
    account2_id = response.json()['id']
    
    # Fazer transferência
    transfer_data = {
        'from_account': account_id,
        'to_account': account2_id,
        'amount': '200.00',
        'description': 'Transferência teste',
        'date': '2024-01-01'
    }
    response = client.post('/api/transactions/transactions/transfer/', transfer_data)
    if response.status_code != 201:
        print(f"Erro na transferência: {response.json()}")
    assert response.status_code == 201, f"Erro na transferência: {response.status_code}"
    print("OK - Transferência realizada")
    
    # Limpar dados
    Transaction.objects.filter(user=user).delete()
    Account.objects.filter(user=user).delete()
    CreditCard.objects.filter(user=user).delete()
    user.delete()
    
    print("=" * 50)
    print("TODOS OS TESTES PASSARAM!")
    print("Sistema funcionando corretamente")
    return True

if __name__ == '__main__':
    try:
        success = test_system()
        if success:
            print("Sistema pronto!")
            exit(0)
    except Exception as e:
        print(f"ERRO: {e}")
        exit(1)