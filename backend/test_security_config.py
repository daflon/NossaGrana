"""
Testes de Configuração de Segurança
Verifica configurações críticas de segurança
"""

import os
import django
import re
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
django.setup()

from django.conf import settings


class SecurityConfigurationTests:
    """Testes para verificar configurações de segurança"""
    
    def __init__(self):
        self.vulnerabilities = []
        self.warnings = []
        self.base_dir = Path(__file__).resolve().parent
    
    def test_django_settings(self):
        """Testa configurações críticas do Django"""
        print("\n🔍 Testando Configurações Django...")
        
        # DEBUG em produção
        if settings.DEBUG:
            self.vulnerabilities.append("CRÍTICO: DEBUG=True pode expor informações sensíveis")
        
        # SECRET_KEY
        if hasattr(settings, 'SECRET_KEY'):
            if settings.SECRET_KEY == 'django-insecure-change-me-in-production':
                self.vulnerabilities.append("CRÍTICO: SECRET_KEY padrão não alterada")
            elif len(settings.SECRET_KEY) < 50:
                self.warnings.append("SECRET_KEY muito curta (recomendado: 50+ caracteres)")
        
        # ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS and not settings.DEBUG:
            self.vulnerabilities.append("CRÍTICO: ALLOWED_HOSTS com '*' em produção")
        
        # CORS Settings
        if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and settings.CORS_ALLOW_ALL_ORIGINS:
            if not settings.DEBUG:
                self.vulnerabilities.append("CRÍTICO: CORS_ALLOW_ALL_ORIGINS=True em produção")
        
        # Security Headers
        security_headers = [
            'SECURE_BROWSER_XSS_FILTER',
            'SECURE_CONTENT_TYPE_NOSNIFF',
            'X_FRAME_OPTIONS',
            'SECURE_HSTS_SECONDS'
        ]
        
        for header in security_headers:
            if not hasattr(settings, header) or not getattr(settings, header):
                self.warnings.append(f"Header de segurança não configurado: {header}")
        
        # Session Security
        if not hasattr(settings, 'SESSION_COOKIE_SECURE') or not settings.SESSION_COOKIE_SECURE:
            if not settings.DEBUG:
                self.vulnerabilities.append("SESSION_COOKIE_SECURE=False em produção")
        
        if not hasattr(settings, 'CSRF_COOKIE_SECURE') or not settings.CSRF_COOKIE_SECURE:
            if not settings.DEBUG:
                self.vulnerabilities.append("CSRF_COOKIE_SECURE=False em produção")
    
    def test_database_security(self):
        """Testa configurações de segurança do banco"""
        print("\n🔍 Testando Configurações de Banco...")
        
        db_config = settings.DATABASES.get('default', {})
        
        # SQLite em produção
        if db_config.get('ENGINE') == 'django.db.backends.sqlite3' and not settings.DEBUG:
            self.warnings.append("SQLite não recomendado para produção")
        
        # Configurações de conexão
        if 'OPTIONS' not in db_config:
            self.warnings.append("Opções de banco não configuradas")
        
        # Timeout muito alto
        options = db_config.get('OPTIONS', {})
        if options.get('timeout', 0) > 30:
            self.warnings.append("Timeout de banco muito alto (>30s)")
    
    def test_authentication_security(self):
        """Testa configurações de autenticação"""
        print("\n🔍 Testando Configurações de Autenticação...")
        
        # Password Validators
        validators = settings.AUTH_PASSWORD_VALIDATORS
        if len(validators) < 4:
            self.warnings.append("Poucos validadores de senha configurados")
        
        # JWT Settings
        if hasattr(settings, 'SIMPLE_JWT'):
            jwt_config = settings.SIMPLE_JWT
            
            # Token lifetime muito longo
            access_lifetime = jwt_config.get('ACCESS_TOKEN_LIFETIME')
            if access_lifetime and access_lifetime.total_seconds() > 3600:  # 1 hora
                self.warnings.append("ACCESS_TOKEN_LIFETIME muito longo (>1h)")
            
            # Refresh token muito longo
            refresh_lifetime = jwt_config.get('REFRESH_TOKEN_LIFETIME')
            if refresh_lifetime and refresh_lifetime.total_seconds() > 604800:  # 7 dias
                self.warnings.append("REFRESH_TOKEN_LIFETIME muito longo (>7 dias)")
    
    def test_file_permissions(self):
        """Testa permissões de arquivos críticos"""
        print("\n🔍 Testando Permissões de Arquivos...")
        
        critical_files = [
            self.base_dir / '.env',
            self.base_dir / 'db.sqlite3',
            self.base_dir / 'logs' / 'security.log'
        ]
        
        for file_path in critical_files:
            if file_path.exists():
                # No Windows, verificação básica
                try:
                    stat_info = file_path.stat()
                    # Arquivo muito permissivo (conceito adaptado para Windows)
                    if stat_info.st_size == 0:
                        self.warnings.append(f"Arquivo vazio: {file_path.name}")
                except Exception as e:
                    self.warnings.append(f"Erro ao verificar {file_path.name}: {str(e)}")
    
    def test_environment_variables(self):
        """Testa variáveis de ambiente"""
        print("\n🔍 Testando Variáveis de Ambiente...")
        
        env_file = self.base_dir / '.env'
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Procura por valores padrão perigosos
                dangerous_patterns = [
                    (r'SECRET_KEY\s*=\s*["\']?django-insecure', "SECRET_KEY padrão encontrada"),
                    (r'DEBUG\s*=\s*["\']?True', "DEBUG=True no arquivo .env"),
                    (r'PASSWORD\s*=\s*["\']?(password|123|admin)', "Senha fraca no .env"),
                    (r'API_KEY\s*=\s*["\']?(test|demo|example)', "API_KEY de teste no .env")
                ]
                
                for pattern, message in dangerous_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.vulnerabilities.append(f"CRÍTICO: {message}")
            
            except Exception as e:
                self.warnings.append(f"Erro ao ler .env: {str(e)}")
        else:
            self.warnings.append("Arquivo .env não encontrado")
    
    def test_logging_security(self):
        """Testa configurações de logging"""
        print("\n🔍 Testando Configurações de Logging...")
        
        if hasattr(settings, 'LOGGING'):
            logging_config = settings.LOGGING
            
            # Verifica se logs de segurança estão configurados
            handlers = logging_config.get('handlers', {})
            if 'security_file' not in handlers:
                self.warnings.append("Handler de log de segurança não configurado")
            
            # Verifica loggers
            loggers = logging_config.get('loggers', {})
            if 'financial_security' not in loggers:
                self.warnings.append("Logger de segurança financeira não configurado")
        else:
            self.vulnerabilities.append("CRÍTICO: Configuração de logging não encontrada")
    
    def test_middleware_security(self):
        """Testa middleware de segurança"""
        print("\n🔍 Testando Middleware de Segurança...")
        
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware'
        ]
        
        for middleware in required_middleware:
            if middleware not in settings.MIDDLEWARE:
                self.vulnerabilities.append(f"CRÍTICO: Middleware obrigatório ausente: {middleware}")
        
        # Verifica ordem do middleware
        if 'corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE:
            cors_index = settings.MIDDLEWARE.index('corsheaders.middleware.CorsMiddleware')
            if cors_index != 0:
                self.warnings.append("CorsMiddleware deve ser o primeiro middleware")
    
    def test_third_party_security(self):
        """Testa configurações de bibliotecas terceiras"""
        print("\n🔍 Testando Configurações de Terceiros...")
        
        # DRF Throttling
        if hasattr(settings, 'REST_FRAMEWORK'):
            drf_config = settings.REST_FRAMEWORK
            
            if 'DEFAULT_THROTTLE_CLASSES' not in drf_config:
                self.warnings.append("Rate limiting não configurado no DRF")
            
            if 'DEFAULT_PERMISSION_CLASSES' not in drf_config:
                self.vulnerabilities.append("CRÍTICO: Permissões padrão não configuradas no DRF")
            
            # Verifica se permite acesso anônimo por padrão
            permissions = drf_config.get('DEFAULT_PERMISSION_CLASSES', [])
            if 'rest_framework.permissions.AllowAny' in permissions:
                self.vulnerabilities.append("CRÍTICO: AllowAny como permissão padrão")
    
    def run_all_tests(self):
        """Executa todos os testes de configuração"""
        print("🔧 INICIANDO TESTES DE CONFIGURAÇÃO DE SEGURANÇA")
        print("=" * 60)
        
        self.test_django_settings()
        self.test_database_security()
        self.test_authentication_security()
        self.test_file_permissions()
        self.test_environment_variables()
        self.test_logging_security()
        self.test_middleware_security()
        self.test_third_party_security()
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE CONFIGURAÇÃO DE SEGURANÇA")
        print("=" * 60)
        
        if self.vulnerabilities:
            print(f"❌ VULNERABILIDADES CRÍTICAS: {len(self.vulnerabilities)}")
            for i, vuln in enumerate(self.vulnerabilities, 1):
                print(f"{i:2d}. {vuln}")
        
        if self.warnings:
            print(f"\n⚠️  AVISOS DE SEGURANÇA: {len(self.warnings)}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i:2d}. {warning}")
        
        if not self.vulnerabilities and not self.warnings:
            print("✅ TODAS AS CONFIGURAÇÕES DE SEGURANÇA ESTÃO ADEQUADAS")
        
        # Recomendações
        if self.vulnerabilities or self.warnings:
            print("\n🔧 RECOMENDAÇÕES:")
            print("1. Corrigir vulnerabilidades críticas imediatamente")
            print("2. Revisar configurações de produção")
            print("3. Implementar monitoramento de segurança")
            print("4. Configurar backup seguro")
            print("5. Estabelecer processo de atualização de segurança")
        
        return len(self.vulnerabilities), len(self.warnings)


def run_security_config_tests():
    """Executa os testes de configuração de segurança"""
    tester = SecurityConfigurationTests()
    return tester.run_all_tests()


if __name__ == '__main__':
    vulnerabilities, warnings = run_security_config_tests()
    
    if vulnerabilities > 0:
        print(f"\n🚨 AÇÃO CRÍTICA NECESSÁRIA: {vulnerabilities} vulnerabilidades encontradas!")
        exit(1)
    elif warnings > 0:
        print(f"\n⚠️  ATENÇÃO: {warnings} avisos de segurança encontrados!")
        exit(0)
    else:
        print("\n✅ Configurações de segurança aprovadas!")
        exit(0)