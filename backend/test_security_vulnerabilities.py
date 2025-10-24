"""
Testes de Segurança - Vulnerabilidades Básicas
Identifica e testa vulnerabilidades críticas de segurança
"""

import os
import django
import unittest
import json
import re
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.db import connection
from unittest.mock import patch, MagicMock

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
django.setup()

from transactions.models import Transaction
from financial_accounts.models import Account
from accounts.models import UserProfile


class SecurityVulnerabilityTests(TestCase):
    """Testes para identificar vulnerabilidades básicas de segurança"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Test Account',
            type='checking',
            initial_balance=1000.00
        )
    
    def test_sql_injection_vulnerabilities(self):
        """Testa vulnerabilidades de SQL Injection"""
        print("\n🔍 Testando SQL Injection...")
        
        # Payloads de SQL Injection comuns
        sql_payloads = [
            "'; DROP TABLE transactions; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM auth_user --",
            "'; DELETE FROM financial_accounts; --",
            "' OR 1=1 --",
            "admin'--",
            "admin'/*",
            "' OR 'x'='x",
            "'; INSERT INTO transactions VALUES (1,1,1000,'hack'); --"
        ]
        
        vulnerabilities_found = []
        
        for payload in sql_payloads:
            try:
                # Teste em parâmetros de busca
                response = self.client.get('/api/transactions/', {
                    'search': payload,
                    'description': payload
                })
                
                # Verifica se houve erro de SQL ou comportamento suspeito
                if response.status_code == 500:
                    vulnerabilities_found.append(f"SQL Injection possível em search: {payload}")
                
                # Teste em dados POST
                response = self.client.post('/api/transactions/', {
                    'description': payload,
                    'amount': '100.00',
                    'account': self.account.id
                })
                
                if response.status_code == 500:
                    vulnerabilities_found.append(f"SQL Injection possível em POST: {payload}")
                    
            except Exception as e:
                if "syntax error" in str(e).lower() or "sql" in str(e).lower():
                    vulnerabilities_found.append(f"SQL Error com payload: {payload}")
        
        if vulnerabilities_found:
            print(f"❌ VULNERABILIDADES SQL INJECTION ENCONTRADAS:")
            for vuln in vulnerabilities_found:
                print(f"   - {vuln}")
        else:
            print("✅ Nenhuma vulnerabilidade SQL Injection óbvia encontrada")
        
        return vulnerabilities_found
    
    def test_xss_vulnerabilities(self):
        """Testa vulnerabilidades de Cross-Site Scripting (XSS)"""
        print("\n🔍 Testando XSS...")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<<SCRIPT>alert('XSS')</SCRIPT>"
        ]
        
        vulnerabilities_found = []
        
        for payload in xss_payloads:
            try:
                # Teste em descrição de transação
                response = self.client.post('/api/transactions/', {
                    'description': payload,
                    'amount': '100.00',
                    'account': self.account.id
                })
                
                if response.status_code == 201:
                    # Verifica se o payload foi armazenado sem sanitização
                    transaction = Transaction.objects.filter(description=payload).first()
                    if transaction:
                        vulnerabilities_found.append(f"XSS Stored possível: {payload}")
                
                # Teste em parâmetros GET
                response = self.client.get('/api/transactions/', {'search': payload})
                if payload in response.content.decode():
                    vulnerabilities_found.append(f"XSS Reflected possível: {payload}")
                    
            except Exception as e:
                pass
        
        if vulnerabilities_found:
            print(f"❌ VULNERABILIDADES XSS ENCONTRADAS:")
            for vuln in vulnerabilities_found:
                print(f"   - {vuln}")
        else:
            print("✅ Nenhuma vulnerabilidade XSS óbvia encontrada")
        
        return vulnerabilities_found
    
    def test_authentication_bypass(self):
        """Testa tentativas de bypass de autenticação"""
        print("\n🔍 Testando Bypass de Autenticação...")
        
        vulnerabilities_found = []
        
        # Teste de acesso sem autenticação
        protected_endpoints = [
            '/api/transactions/',
            '/api/accounts/',
            '/api/budgets/',
            '/api/goals/',
            '/api/reports/'
        ]
        
        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)
            if response.status_code == 200:
                vulnerabilities_found.append(f"Endpoint desprotegido: {endpoint}")
        
        # Teste de manipulação de headers
        headers_tests = [
            {'HTTP_X_FORWARDED_FOR': '127.0.0.1'},
            {'HTTP_X_REAL_IP': '127.0.0.1'},
            {'HTTP_X_FORWARDED_USER': 'admin'},
            {'HTTP_AUTHORIZATION': 'Bearer fake_token'},
            {'HTTP_X_USER_ID': '1'}
        ]
        
        for headers in headers_tests:
            response = self.client.get('/api/transactions/', **headers)
            if response.status_code == 200:
                vulnerabilities_found.append(f"Possível bypass via headers: {headers}")
        
        if vulnerabilities_found:
            print(f"❌ VULNERABILIDADES DE AUTENTICAÇÃO ENCONTRADAS:")
            for vuln in vulnerabilities_found:
                print(f"   - {vuln}")
        else:
            print("✅ Nenhuma vulnerabilidade de autenticação óbvia encontrada")
        
        return vulnerabilities_found
    
    def test_authorization_flaws(self):
        """Testa falhas de autorização (IDOR)"""
        print("\n🔍 Testando Falhas de Autorização...")
        
        # Criar outro usuário
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='otherpass123'
        )
        other_account = Account.objects.create(
            user=other_user,
            name='Other Account',
            type='checking',
            initial_balance=500.00
        )
        
        # Login como primeiro usuário
        self.client.login(username='testuser', password='testpass123')
        
        vulnerabilities_found = []
        
        # Teste IDOR - tentar acessar recursos de outro usuário
        idor_tests = [
            f'/api/accounts/{other_account.id}/',
            f'/api/transactions/?account={other_account.id}',
        ]
        
        for endpoint in idor_tests:
            response = self.client.get(endpoint)
            if response.status_code == 200:
                vulnerabilities_found.append(f"IDOR possível: {endpoint}")
        
        # Teste de modificação de recursos de outro usuário
        response = self.client.put(f'/api/accounts/{other_account.id}/', {
            'name': 'Hacked Account',
            'balance': '999999.99'
        }, content_type='application/json')
        
        if response.status_code in [200, 204]:
            vulnerabilities_found.append("IDOR: Modificação de conta de outro usuário")
        
        if vulnerabilities_found:
            print(f"❌ VULNERABILIDADES DE AUTORIZAÇÃO ENCONTRADAS:")
            for vuln in vulnerabilities_found:
                print(f"   - {vuln}")
        else:
            print("✅ Nenhuma vulnerabilidade de autorização óbvia encontrada")
        
        return vulnerabilities_found
    
    def test_sensitive_data_exposure(self):
        """Testa exposição de dados sensíveis"""
        print("\n🔍 Testando Exposição de Dados Sensíveis...")
        
        vulnerabilities_found = []
        
        # Teste de informações em responses
        response = self.client.get('/api/accounts/')
        if response.status_code == 200:
            content = response.content.decode()
            
            # Procura por dados sensíveis que não deveriam estar expostos
            sensitive_patterns = [
                r'password',
                r'secret',
                r'token',
                r'key',
                r'hash',
                r'salt',
                r'csrf',
                r'session'
            ]
            
            for pattern in sensitive_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities_found.append(f"Possível exposição de dados sensíveis: {pattern}")
        
        # Teste de debug information
        if settings.DEBUG:
            vulnerabilities_found.append("DEBUG=True em produção (exposição de informações)")
        
        # Teste de stack traces
        response = self.client.get('/api/nonexistent/')
        if response.status_code == 500 and 'Traceback' in response.content.decode():
            vulnerabilities_found.append("Stack traces expostos em erros 500")
        
        if vulnerabilities_found:
            print(f"❌ EXPOSIÇÃO DE DADOS SENSÍVEIS ENCONTRADA:")
            for vuln in vulnerabilities_found:
                print(f"   - {vuln}")
        else:
            print("✅ Nenhuma exposição óbvia de dados sensíveis encontrada")
        
        return vulnerabilities_found
    
    def test_csrf_protection(self):
        """Testa proteção contra CSRF"""
        print("\n🔍 Testando Proteção CSRF...")
        
        vulnerabilities_found = []
        
        # Teste POST sem CSRF token
        response = self.client.post('/api/transactions/', {
            'description': 'Test Transaction',
            'amount': '100.00',
            'account': self.account.id
        })
        
        # Se a requisição passou sem CSRF token, há vulnerabilidade
        if response.status_code in [200, 201]:
            vulnerabilities_found.append("CSRF: POST aceito sem token CSRF")
        
        # Teste com CSRF token inválido
        self.client.cookies['csrftoken'] = 'invalid_token'
        response = self.client.post('/api/transactions/', {
            'description': 'Test Transaction',
            'amount': '100.00',
            'account': self.account.id,
            'csrfmiddlewaretoken': 'invalid_token'
        })
        
        if response.status_code in [200, 201]:
            vulnerabilities_found.append("CSRF: POST aceito com token inválido")
        
        if vulnerabilities_found:
            print(f"❌ VULNERABILIDADES CSRF ENCONTRADAS:")
            for vuln in vulnerabilities_found:
                print(f"   - {vuln}")
        else:
            print("✅ Proteção CSRF funcionando corretamente")
        
        return vulnerabilities_found
    
    def test_rate_limiting(self):
        """Testa rate limiting"""
        print("\n🔍 Testando Rate Limiting...")
        
        vulnerabilities_found = []
        
        # Teste de múltiplas requisições rápidas
        responses = []
        for i in range(50):  # 50 requisições rápidas
            response = self.client.get('/api/transactions/')
            responses.append(response.status_code)
        
        # Se todas as requisições passaram, pode não haver rate limiting
        if all(status == 200 for status in responses):
            vulnerabilities_found.append("Rate Limiting: Muitas requisições aceitas sem limitação")
        
        # Teste de login brute force
        login_attempts = []
        for i in range(20):
            response = self.client.post('/api/auth/login/', {
                'username': 'admin',
                'password': f'wrong_password_{i}'
            })
            login_attempts.append(response.status_code)
        
        if not any(status == 429 for status in login_attempts):
            vulnerabilities_found.append("Rate Limiting: Login brute force não limitado")
        
        if vulnerabilities_found:
            print(f"❌ PROBLEMAS DE RATE LIMITING ENCONTRADOS:")
            for vuln in vulnerabilities_found:
                print(f"   - {vuln}")
        else:
            print("✅ Rate limiting funcionando adequadamente")
        
        return vulnerabilities_found
    
    def test_input_validation(self):
        """Testa validação de entrada"""
        print("\n🔍 Testando Validação de Entrada...")
        
        vulnerabilities_found = []
        
        # Teste de valores extremos
        extreme_values = [
            {'amount': '999999999999999999999.99'},  # Valor muito alto
            {'amount': '-999999999.99'},  # Valor negativo
            {'amount': 'abc'},  # Não numérico
            {'description': 'A' * 10000},  # String muito longa
            {'description': ''},  # String vazia
            {'account': '999999'},  # ID inexistente
            {'account': 'abc'},  # ID não numérico
        ]
        
        for test_data in extreme_values:
            response = self.client.post('/api/transactions/', {
                'description': test_data.get('description', 'Test'),
                'amount': test_data.get('amount', '100.00'),
                'account': test_data.get('account', self.account.id)
            })
            
            # Se dados inválidos foram aceitos
            if response.status_code in [200, 201]:
                vulnerabilities_found.append(f"Validação falhou para: {test_data}")
        
        if vulnerabilities_found:
            print(f"❌ PROBLEMAS DE VALIDAÇÃO ENCONTRADOS:")
            for vuln in vulnerabilities_found:
                print(f"   - {vuln}")
        else:
            print("✅ Validação de entrada funcionando corretamente")
        
        return vulnerabilities_found
    
    def run_all_security_tests(self):
        """Executa todos os testes de segurança"""
        print("🔒 INICIANDO TESTES DE SEGURANÇA - VULNERABILIDADES BÁSICAS")
        print("=" * 60)
        
        all_vulnerabilities = []
        
        # Executa todos os testes
        all_vulnerabilities.extend(self.test_sql_injection_vulnerabilities())
        all_vulnerabilities.extend(self.test_xss_vulnerabilities())
        all_vulnerabilities.extend(self.test_authentication_bypass())
        all_vulnerabilities.extend(self.test_authorization_flaws())
        all_vulnerabilities.extend(self.test_sensitive_data_exposure())
        all_vulnerabilities.extend(self.test_csrf_protection())
        all_vulnerabilities.extend(self.test_rate_limiting())
        all_vulnerabilities.extend(self.test_input_validation())
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DE SEGURANÇA")
        print("=" * 60)
        
        if all_vulnerabilities:
            print(f"❌ TOTAL DE VULNERABILIDADES ENCONTRADAS: {len(all_vulnerabilities)}")
            print("\n🚨 VULNERABILIDADES CRÍTICAS:")
            for i, vuln in enumerate(all_vulnerabilities, 1):
                print(f"{i:2d}. {vuln}")
            
            print("\n🔧 RECOMENDAÇÕES IMEDIATAS:")
            print("1. Implementar sanitização adequada de inputs")
            print("2. Configurar rate limiting robusto")
            print("3. Revisar controles de autorização")
            print("4. Implementar validação rigorosa de dados")
            print("5. Configurar headers de segurança")
            print("6. Desabilitar DEBUG em produção")
            
        else:
            print("✅ NENHUMA VULNERABILIDADE CRÍTICA ENCONTRADA")
            print("Sistema passou nos testes básicos de segurança")
        
        return all_vulnerabilities


def run_security_tests():
    """Função para executar os testes de segurança"""
    import django
    from django.test.utils import get_runner
    from django.conf import settings
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Executa apenas os testes de segurança
    test_suite = unittest.TestLoader().loadTestsFromTestCase(SecurityVulnerabilityTests)
    
    # Cria uma instância do teste para executar manualmente
    security_test = SecurityVulnerabilityTests()
    security_test.setUp()
    
    return security_test.run_all_security_tests()


if __name__ == '__main__':
    vulnerabilities = run_security_tests()
    
    if vulnerabilities:
        print(f"\n🚨 AÇÃO NECESSÁRIA: {len(vulnerabilities)} vulnerabilidades encontradas!")
        exit(1)
    else:
        print("\n✅ Testes de segurança concluídos com sucesso!")
        exit(0)