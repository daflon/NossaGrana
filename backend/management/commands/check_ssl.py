"""
Comando Django para verificar configurações SSL
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import ssl
import socket
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Verifica configurações SSL do projeto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='localhost',
            help='Host para verificar SSL'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=443,
            help='Porta para verificar SSL'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔒 Verificação de Configurações SSL')
        )
        self.stdout.write('=' * 50)
        
        # Verifica configurações Django
        self.check_django_ssl_settings()
        
        # Verifica certificado se host fornecido
        if options['host'] != 'localhost':
            self.check_ssl_certificate(options['host'], options['port'])

    def check_django_ssl_settings(self):
        """Verifica configurações SSL do Django"""
        self.stdout.write('\n📋 Configurações Django SSL:')
        
        settings_to_check = [
            ('SECURE_SSL_REDIRECT', 'Redirecionamento SSL'),
            ('SECURE_HSTS_SECONDS', 'HSTS Seconds'),
            ('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'HSTS Subdomains'),
            ('SECURE_HSTS_PRELOAD', 'HSTS Preload'),
            ('SESSION_COOKIE_SECURE', 'Session Cookie Secure'),
            ('CSRF_COOKIE_SECURE', 'CSRF Cookie Secure'),
            ('SECURE_BROWSER_XSS_FILTER', 'XSS Filter'),
            ('SECURE_CONTENT_TYPE_NOSNIFF', 'Content Type NoSniff'),
            ('X_FRAME_OPTIONS', 'X-Frame-Options'),
        ]
        
        for setting_name, description in settings_to_check:
            value = getattr(settings, setting_name, 'Não definido')
            status = '✅' if value else '❌'
            self.stdout.write(f'  {status} {description}: {value}')
        
        # Verifica middleware de segurança
        self.stdout.write('\n🛡️  Middleware de Segurança:')
        security_middlewares = [
            'django.middleware.security.SecurityMiddleware',
            'middleware.security.SecurityHeadersMiddleware',
            'middleware.security.SSLRedirectMiddleware',
        ]
        
        for middleware in security_middlewares:
            if middleware in settings.MIDDLEWARE:
                self.stdout.write(f'  ✅ {middleware}')
            else:
                self.stdout.write(f'  ❌ {middleware} (não encontrado)')

    def check_ssl_certificate(self, host, port):
        """Verifica certificado SSL de um host"""
        self.stdout.write(f'\n🔍 Verificando certificado SSL para {host}:{port}')
        
        try:
            # Cria contexto SSL
            context = ssl.create_default_context()
            
            # Conecta e obtém certificado
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    
                    self.stdout.write('  ✅ Conexão SSL estabelecida')
                    self.stdout.write(f"  📄 Assunto: {cert.get('subject', 'N/A')}")
                    self.stdout.write(f"  🏢 Emissor: {cert.get('issuer', 'N/A')}")
                    self.stdout.write(f"  📅 Válido até: {cert.get('notAfter', 'N/A')}")
                    
                    # Verifica SANs
                    sans = []
                    for san in cert.get('subjectAltName', []):
                        sans.append(san[1])
                    
                    if sans:
                        self.stdout.write(f"  🌐 SANs: {', '.join(sans)}")
                    
        except ssl.SSLError as e:
            self.stdout.write(f'  ❌ Erro SSL: {e}')
        except socket.timeout:
            self.stdout.write(f'  ⏰ Timeout ao conectar com {host}:{port}')
        except Exception as e:
            self.stdout.write(f'  ❌ Erro: {e}')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('✅ Verificação concluída!')