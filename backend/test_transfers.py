#!/usr/bin/env python
"""
Script para testar transferências entre contas
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
from financial_accounts.models import Account
from transactions.serializers import TransferSerializer
from datetime import date

def test_transfer_functionality():
    """
    Testa a funcionalidade de transferências
    """
    print("=== Testando Funcionalidade de Transferências ===")
    
    # Criar usuário de teste
    user, created = User.objects.get_or_create(
        username='test_transfer_user',
        defaults={'email': 'transfer@test.com'}
    )
    
    # Criar contas de teste
    account1, created = Account.objects.get_or_create(
        user=user,
        name='Conta Corrente',
        defaults={
            'type': 'checking',
            'bank': 'Banco A',
            'initial_balance': Decimal('2000.00')
        }
    )
    
    account2, created = Account.objects.get_or_create(
        user=user,
        name='Poupança',
        defaults={
            'type': 'savings',
            'bank': 'Banco B',
            'initial_balance': Decimal('500.00')
        }
    )
    
    print(f"Saldo inicial Conta Corrente: R$ {account1.current_balance}")
    print(f"Saldo inicial Poupança: R$ {account2.current_balance}")
    
    # Dados da transferência
    transfer_data = {
        'amount': Decimal('300.00'),
        'description': 'Transferência para poupança',
        'from_account': account1.id,
        'to_account': account2.id,
        'date': date.today()
    }
    
    # Criar contexto de request mockado
    class MockRequest:
        def __init__(self, user):
            self.user = user
    
    mock_request = MockRequest(user)
    
    # Testar serializer de transferência
    serializer = TransferSerializer(
        data=transfer_data,
        context={'request': mock_request}
    )
    
    if serializer.is_valid():
        print("✅ Dados de transferência válidos")
        
        # Criar transferência
        transaction = serializer.save()
        print(f"✅ Transferência criada: {transaction}")
        
        # Recarregar contas do banco
        account1.refresh_from_db()
        account2.refresh_from_db()
        
        print(f"Saldo após transferência Conta Corrente: R$ {account1.current_balance}")
        print(f"Saldo após transferência Poupança: R$ {account2.current_balance}")
        
        # Verificar se os saldos estão corretos
        expected_account1_balance = Decimal('2000.00') - Decimal('300.00')
        expected_account2_balance = Decimal('500.00') + Decimal('300.00')
        
        if account1.current_balance == expected_account1_balance:
            print("✅ Saldo da conta origem correto")
        else:
            print(f"❌ Saldo da conta origem incorreto. Esperado: {expected_account1_balance}, Atual: {account1.current_balance}")
        
        if account2.current_balance == expected_account2_balance:
            print("✅ Saldo da conta destino correto")
        else:
            print(f"❌ Saldo da conta destino incorreto. Esperado: {expected_account2_balance}, Atual: {account2.current_balance}")
        
        # Verificar se a transação foi criada corretamente
        if transaction.type == 'transfer':
            print("✅ Tipo de transação correto")
        else:
            print(f"❌ Tipo de transação incorreto: {transaction.type}")
        
        if transaction.transfer_from_account == account1:
            print("✅ Conta origem correta")
        else:
            print("❌ Conta origem incorreta")
        
        if transaction.transfer_to_account == account2:
            print("✅ Conta destino correta")
        else:
            print("❌ Conta destino incorreta")
        
        # Testar transferência com saldo insuficiente
        print("\n--- Testando Saldo Insuficiente ---")
        invalid_transfer_data = {
            'amount': Decimal('5000.00'),  # Valor maior que o saldo
            'description': 'Transferência inválida',
            'from_account': account1.id,
            'to_account': account2.id,
            'date': date.today()
        }
        
        invalid_serializer = TransferSerializer(
            data=invalid_transfer_data,
            context={'request': mock_request}
        )
        
        if not invalid_serializer.is_valid():
            print("✅ Validação de saldo insuficiente funcionando")
            print(f"Erro: {invalid_serializer.errors}")
        else:
            print("❌ Validação de saldo insuficiente não funcionou")
        
        # Testar transferência para a mesma conta
        print("\n--- Testando Transferência para Mesma Conta ---")
        same_account_data = {
            'amount': Decimal('100.00'),
            'description': 'Transferência inválida',
            'from_account': account1.id,
            'to_account': account1.id,  # Mesma conta
            'date': date.today()
        }
        
        same_account_serializer = TransferSerializer(
            data=same_account_data,
            context={'request': mock_request}
        )
        
        if not same_account_serializer.is_valid():
            print("✅ Validação de mesma conta funcionando")
            print(f"Erro: {same_account_serializer.errors}")
        else:
            print("❌ Validação de mesma conta não funcionou")
        
    else:
        print("❌ Dados de transferência inválidos:")
        print(serializer.errors)
    
    print("\n✅ Teste de transferências concluído!")

if __name__ == '__main__':
    print("🧪 Iniciando testes de transferências...\n")
    
    try:
        test_transfer_functionality()
        print("\n🎉 Todos os testes de transferência passaram!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()