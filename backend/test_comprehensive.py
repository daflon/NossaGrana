#!/usr/bin/env python
"""
Testes Abrangentes - Nossa Grana
Cobertura completa das funcionalidades implementadas
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from transactions.models import Transaction, Category
from financial_accounts.models import Account, CreditCard
from transactions.serializers import TransferSerializer

class ComprehensiveTestSuite:
    """
    Suite completa de testes para o sistema Nossa Grana
    """
    
    def __init__(self):
        self.client = APIClient()
        self.user = None
        self.accounts = []
        self.credit_cards = []
        self.categories = []
        self.transactions = []
        
    def setup_test_data(self):
        """
        Configurar dados de teste
        """
        print("🔧 Configurando dados de teste...")
        
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='test_user_comprehensive',
            email='test@nossagrana.com',
            password='testpass123'
        )
        
        # Autenticar cliente
        self.client.force_authenticate(user=self.user)
        
        # Criar ou obter categorias
        categories_data = [
            ('Alimentação', '#FF6B6B', 'food'),
            ('Transporte', '#4ECDC4', 'transport'),
            ('Salário', '#45B7D1', 'salary'),
            ('Transferência', '#6c757d', 'transfer')
        ]
        
        self.categories = []
        for name, color, icon in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'color': color, 'icon': icon}
            )
            self.categories.append(category)
        
        # Criar contas
        self.accounts = [
            Account.objects.create(
                user=self.user,
                name='Conta Corrente Principal',
                type='checking',
                bank='Banco do Brasil',
                initial_balance=Decimal('5000.00')
            ),
            Account.objects.create(
                user=self.user,
                name='Poupança',
                type='savings',
                bank='Itaú',
                initial_balance=Decimal('10000.00')
            ),
            Account.objects.create(
                user=self.user,
                name='Dinheiro',
                type='cash',
                bank='',
                initial_balance=Decimal('500.00')
            )
        ]
        
        # Criar cartões de crédito
        self.credit_cards = [
            CreditCard.objects.create(
                user=self.user,
                name='Cartão Visa Gold',
                bank='Banco do Brasil',
                credit_limit=Decimal('8000.00'),
                closing_day=15,
                due_day=10
            ),
            CreditCard.objects.create(
                user=self.user,
                name='Cartão Mastercard',
                bank='Itaú',
                credit_limit=Decimal('5000.00'),
                closing_day=20,
                due_day=15
            )
        ]
        
        print("✅ Dados de teste configurados com sucesso!")
    
    def test_account_management(self):
        """
        Testar gerenciamento de contas
        """
        print("\n📊 Testando Gerenciamento de Contas...")
        
        # Teste 1: Listar contas
        response = self.client.get('/api/financial/accounts/')
        assert response.status_code == 200, f"Erro ao listar contas: {response.status_code}"
        accounts_data = response.json()
        assert len(accounts_data) >= 3, f"Esperado pelo menos 3 contas, encontrado {len(accounts_data)}"
        print("✅ Listagem de contas funcionando")
        
        # Teste 2: Criar nova conta
        new_account_data = {
            'name': 'Conta Investimento',
            'type': 'investment',
            'bank': 'XP Investimentos',
            'initial_balance': '15000.00'
        }
        response = self.client.post('/api/financial/accounts/', new_account_data)
        assert response.status_code == 201, f"Erro ao criar conta: {response.status_code}"
        print("✅ Criação de conta funcionando")
        
        # Teste 3: Atualizar saldo automaticamente
        account = self.accounts[0]
        initial_balance = account.current_balance
        
        # Criar transação de receita
        transaction_data = {
            'type': 'income',
            'amount': '1000.00',
            'description': 'Teste de receita',
            'category': self.categories[2].id,  # Salário
            'account': account.id,
            'date': date.today().isoformat()
        }
        response = self.client.post('/api/transactions/transactions/', transaction_data)
        assert response.status_code == 201, f"Erro ao criar transação: {response.status_code}"
        
        # Verificar se saldo foi atualizado
        account.refresh_from_db()
        expected_balance = initial_balance + Decimal('1000.00')
        assert account.current_balance == expected_balance, f"Saldo não atualizado. Esperado: {expected_balance}, Atual: {account.current_balance}"
        print("✅ Atualização automática de saldo funcionando")
        
        # Teste 4: Relatório de conta
        response = self.client.get(f'/api/financial/accounts/{account.id}/report/')
        assert response.status_code == 200, f"Erro ao gerar relatório: {response.status_code}"
        report_data = response.json()
        assert 'totals' in report_data, "Relatório deve conter totais"
        assert 'monthly_evolution' in report_data, "Relatório deve conter evolução mensal"
        print("✅ Relatório de conta funcionando")
    
    def test_credit_card_management(self):
        """
        Testar gerenciamento de cartões de crédito
        """
        print("\n💳 Testando Gerenciamento de Cartões...")
        
        # Teste 1: Listar cartões
        response = self.client.get('/api/financial/credit-cards/')
        assert response.status_code == 200, f"Erro ao listar cartões: {response.status_code}"
        cards_data = response.json()
        assert len(cards_data) >= 2, f"Esperado pelo menos 2 cartões, encontrado {len(cards_data)}"
        print("✅ Listagem de cartões funcionando")
        
        # Teste 2: Criar transação no cartão
        card = self.credit_cards[0]
        initial_limit = card.available_limit
        
        transaction_data = {
            'type': 'expense',
            'amount': '500.00',
            'description': 'Compra no cartão',
            'category': self.categories[0].id,  # Alimentação
            'credit_card': card.id,
            'date': date.today().isoformat()
        }
        response = self.client.post('/api/transactions/transactions/', transaction_data)
        assert response.status_code == 201, f"Erro ao criar transação no cartão: {response.status_code}"
        
        # Verificar se limite foi atualizado
        card.refresh_from_db()
        expected_limit = initial_limit - Decimal('500.00')
        assert card.available_limit == expected_limit, f"Limite não atualizado. Esperado: {expected_limit}, Atual: {card.available_limit}"
        print("✅ Atualização automática de limite funcionando")
        
        # Teste 3: Relatório de cartão
        response = self.client.get(f'/api/financial/credit-cards/{card.id}/report/')
        assert response.status_code == 200, f"Erro ao gerar relatório do cartão: {response.status_code}"
        report_data = response.json()
        assert 'totals' in report_data, "Relatório deve conter totais"
        assert 'limit_info' in report_data, "Relatório deve conter informações de limite"
        print("✅ Relatório de cartão funcionando")
    
    def test_transfers(self):
        """
        Testar sistema de transferências
        """
        print("\n🔄 Testando Sistema de Transferências...")
        
        account1 = self.accounts[0]  # Conta Corrente
        account2 = self.accounts[1]  # Poupança
        
        # Saldos iniciais
        initial_balance1 = account1.current_balance
        initial_balance2 = account2.current_balance
        
        # Teste 1: Transferência válida
        transfer_data = {
            'from_account': account1.id,
            'to_account': account2.id,
            'amount': '1000.00',
            'description': 'Transferência para poupança',
            'date': date.today().isoformat()
        }
        
        response = self.client.post('/api/transactions/transactions/transfer/', transfer_data)
        assert response.status_code == 201, f"Erro na transferência: {response.status_code}"
        print("✅ Transferência criada com sucesso")
        
        # Verificar saldos atualizados
        account1.refresh_from_db()
        account2.refresh_from_db()
        
        expected_balance1 = initial_balance1 - Decimal('1000.00')
        expected_balance2 = initial_balance2 + Decimal('1000.00')
        
        assert account1.current_balance == expected_balance1, f"Saldo conta origem incorreto. Esperado: {expected_balance1}, Atual: {account1.current_balance}"
        assert account2.current_balance == expected_balance2, f"Saldo conta destino incorreto. Esperado: {expected_balance2}, Atual: {account2.current_balance}"
        print("✅ Saldos atualizados corretamente")
        
        # Teste 2: Transferência com saldo insuficiente
        invalid_transfer_data = {
            'from_account': account1.id,
            'to_account': account2.id,
            'amount': '50000.00',  # Valor maior que o saldo
            'description': 'Transferência inválida',
            'date': date.today().isoformat()
        }
        
        response = self.client.post('/api/transactions/transactions/transfer/', invalid_transfer_data)
        assert response.status_code == 400, f"Deveria falhar com saldo insuficiente: {response.status_code}"
        print("✅ Validação de saldo insuficiente funcionando")
        
        # Teste 3: Transferência para mesma conta
        same_account_data = {
            'from_account': account1.id,
            'to_account': account1.id,
            'amount': '100.00',
            'description': 'Transferência inválida',
            'date': date.today().isoformat()
        }
        
        response = self.client.post('/api/transactions/transactions/transfer/', same_account_data)
        assert response.status_code == 400, f"Deveria falhar com mesma conta: {response.status_code}"
        print("✅ Validação de mesma conta funcionando")
    
    def test_transaction_management(self):
        """
        Testar gerenciamento de transações
        """
        print("\n💰 Testando Gerenciamento de Transações...")
        
        # Teste 1: Criar transação de receita
        income_data = {
            'type': 'income',
            'amount': '3000.00',
            'description': 'Salário mensal',
            'category': self.categories[2].id,
            'account': self.accounts[0].id,
            'date': date.today().isoformat()
        }
        
        response = self.client.post('/api/transactions/transactions/', income_data)
        assert response.status_code == 201, f"Erro ao criar receita: {response.status_code}"
        print("✅ Criação de receita funcionando")
        
        # Teste 2: Criar transação de despesa
        expense_data = {
            'type': 'expense',
            'amount': '150.00',
            'description': 'Supermercado',
            'category': self.categories[0].id,
            'account': self.accounts[0].id,
            'date': date.today().isoformat()
        }
        
        response = self.client.post('/api/transactions/transactions/', expense_data)
        assert response.status_code == 201, f"Erro ao criar despesa: {response.status_code}"
        print("✅ Criação de despesa funcionando")
        
        # Teste 3: Listar transações
        response = self.client.get('/api/transactions/transactions/')
        assert response.status_code == 200, f"Erro ao listar transações: {response.status_code}"
        transactions_data = response.json()
        assert 'results' in transactions_data, "Resposta deve conter 'results'"
        assert len(transactions_data['results']) > 0, "Deve haver transações listadas"
        print("✅ Listagem de transações funcionando")
        
        # Teste 4: Resumo de transações
        response = self.client.get('/api/transactions/transactions/summary/')
        assert response.status_code == 200, f"Erro ao obter resumo: {response.status_code}"
        summary_data = response.json()
        assert 'total_income' in summary_data, "Resumo deve conter total de receitas"
        assert 'total_expense' in summary_data, "Resumo deve conter total de despesas"
        print("✅ Resumo de transações funcionando")
    
    def test_reports(self):
        """
        Testar sistema de relatórios
        """
        print("\n📈 Testando Sistema de Relatórios...")
        
        # Teste 1: Relatório geral
        response = self.client.get('/api/reports/summary/')
        assert response.status_code == 200, f"Erro no relatório geral: {response.status_code}"
        print("✅ Relatório geral funcionando")
        
        # Teste 2: Breakdown por categoria
        response = self.client.get('/api/reports/category-breakdown/?type=expense')
        assert response.status_code == 200, f"Erro no breakdown por categoria: {response.status_code}"
        print("✅ Breakdown por categoria funcionando")
        
        # Teste 3: Tendência mensal
        response = self.client.get('/api/reports/monthly-trend/?months=6')
        assert response.status_code == 200, f"Erro na tendência mensal: {response.status_code}"
        print("✅ Tendência mensal funcionando")
    
    def test_data_integrity(self):
        """
        Testar integridade dos dados
        """
        print("\n🔍 Testando Integridade dos Dados...")
        
        # Teste 1: Consistência de saldos
        for account in self.accounts:
            account.refresh_from_db()
            
            # Calcular saldo manualmente
            income_total = Transaction.objects.filter(
                account=account, type='income'
            ).aggregate(total=django.db.models.Sum('amount'))['total'] or Decimal('0')
            
            expense_total = Transaction.objects.filter(
                account=account, type='expense'
            ).aggregate(total=django.db.models.Sum('amount'))['total'] or Decimal('0')
            
            transfers_in = Transaction.objects.filter(
                transfer_to_account=account, type='transfer'
            ).aggregate(total=django.db.models.Sum('amount'))['total'] or Decimal('0')
            
            transfers_out = Transaction.objects.filter(
                transfer_from_account=account, type='transfer'
            ).aggregate(total=django.db.models.Sum('amount'))['total'] or Decimal('0')
            
            expected_balance = (
                account.initial_balance + 
                income_total - 
                expense_total + 
                transfers_in - 
                transfers_out
            )
            
            assert account.current_balance == expected_balance, f"Saldo inconsistente na conta {account.name}. Esperado: {expected_balance}, Atual: {account.current_balance}"
        
        print("✅ Consistência de saldos das contas verificada")
        
        # Teste 2: Consistência de limites dos cartões
        for card in self.credit_cards:
            card.refresh_from_db()
            
            used_limit = Transaction.objects.filter(
                credit_card=card, type='expense'
            ).aggregate(total=django.db.models.Sum('amount'))['total'] or Decimal('0')
            
            expected_available = card.credit_limit - used_limit
            
            assert card.available_limit == expected_available, f"Limite inconsistente no cartão {card.name}. Esperado: {expected_available}, Atual: {card.available_limit}"
        
        print("✅ Consistência de limites dos cartões verificada")
    
    def run_all_tests(self):
        """
        Executar todos os testes
        """
        print("INICIANDO SUITE COMPLETA DE TESTES - NOSSA GRANA")
        print("=" * 60)
        
        try:
            self.setup_test_data()
            self.test_account_management()
            self.test_credit_card_management()
            self.test_transfers()
            self.test_transaction_management()
            self.test_reports()
            self.test_data_integrity()
            
            print("\n" + "=" * 60)
            print("TODOS OS TESTES PASSARAM COM SUCESSO!")
            print("Sistema Nossa Grana totalmente funcional")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ TESTE FALHOU: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Limpeza (opcional)
            if self.user:
                # Remover dados de teste
                Transaction.objects.filter(user=self.user).delete()
                Account.objects.filter(user=self.user).delete()
                CreditCard.objects.filter(user=self.user).delete()
                self.user.delete()
                print("🧹 Dados de teste limpos")

if __name__ == '__main__':
    # Importar dependências do Django
    import django.db.models
    
    # Executar suite de testes
    test_suite = ComprehensiveTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\nSistema pronto para producao!")
        exit(0)
    else:
        print("\n⚠️ Corrija os erros antes de prosseguir")
        exit(1)