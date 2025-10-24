#!/usr/bin/env python3
"""
Quick Security Check - Verificação Rápida de Segurança
Executa verificações essenciais de segurança em menos de 30 segundos
"""

import os
import django
import re
from pathlib import Path
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
django.setup()

from django.conf import settings


class QuickSecurityChecker:
    """Verificador rápido de segurança"""
    
    def __init__(self):
        self.critical_issues = []
        self.warnings = []
    
    def check_critical_settings(self):
        """Verifica configurações críticas"""
        print("🔍 Verificando configurações críticas...")
        
        # DEBUG em produção
        if settings.DEBUG:
            self.critical_issues.append("DEBUG=True (risco de exposição de dados)")
        
        # SECRET_KEY padrão
        if hasattr(settings, 'SECRET_KEY'):
            if 'django-insecure' in settings.SECRET_KEY:
                self.critical_issues.append("SECRET_KEY padrão não alterada")
        
        # ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS and not settings.DEBUG:
            self.critical_issues.append("ALLOWED_HOSTS com '*' em produção")
        
        # Middleware de segurança
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware'
        ]
        
        for middleware in required_middleware:
            if middleware not in settings.MIDDLEWARE:
                self.critical_issues.append(f"Middleware crítico ausente: {middleware}")
    
    def check_environment_file(self):
        """Verifica arquivo .env"""
        print("🔍 Verificando arquivo .env...")
        
        env_file = Path('.env')
        if not env_file.exists():
            self.warnings.append("Arquivo .env não encontrado")
            return
        
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Procura por valores perigosos
            if re.search(r'SECRET_KEY\s*=\s*["\']?django-insecure', content, re.IGNORECASE):
                self.critical_issues.append("SECRET_KEY padrão no .env")
            
            if re.search(r'DEBUG\s*=\s*["\']?True', content, re.IGNORECASE):
                self.warnings.append("DEBUG=True no .env")
            
            if re.search(r'PASSWORD\s*=\s*["\']?(password|123|admin)', content, re.IGNORECASE):
                self.critical_issues.append("Senha fraca no .env")
        
        except Exception as e:
            self.warnings.append(f"Erro ao ler .env: {str(e)}")
    
    def check_database_file(self):
        """Verifica arquivo de banco"""
        print("🔍 Verificando banco de dados...")
        
        db_file = Path('db.sqlite3')
        if db_file.exists():
            try:
                stat_info = db_file.stat()
                if stat_info.st_size == 0:
                    self.warnings.append("Banco de dados vazio")
                elif stat_info.st_size > 100 * 1024 * 1024:  # 100MB
                    self.warnings.append("Banco de dados muito grande (>100MB)")
            except Exception:
                pass
    
    def check_log_files(self):
        """Verifica arquivos de log"""
        print("🔍 Verificando logs de segurança...")
        
        log_dir = Path('logs')
        if log_dir.exists():
            security_log = log_dir / 'security.log'
            if not security_log.exists():
                self.warnings.append("Log de segurança não encontrado")
        else:
            self.warnings.append("Diretório de logs não encontrado")
    
    def check_sensitive_files(self):
        """Verifica arquivos sensíveis"""
        print("🔍 Verificando arquivos sensíveis...")
        
        sensitive_patterns = [
            '*.key',
            '*.pem',
            '*.p12',
            '*.pfx',
            'id_rsa*',
            '.aws/credentials'
        ]
        
        for pattern in sensitive_patterns:
            files = list(Path('.').glob(pattern))
            if files:
                self.warnings.append(f"Arquivos sensíveis encontrados: {pattern}")
    
    def check_python_packages(self):
        """Verifica pacotes Python críticos"""
        print("🔍 Verificando pacotes de segurança...")
        
        try:
            import pkg_resources
            
            # Pacotes de segurança recomendados
            security_packages = [
                'cryptography',
                'django-cors-headers',
                'django-ratelimit'
            ]
            
            installed = [pkg.project_name.lower() for pkg in pkg_resources.working_set]
            
            for package in security_packages:
                if package.lower() not in installed:
                    self.warnings.append(f"Pacote de segurança não instalado: {package}")
        
        except Exception:
            pass
    
    def run_quick_check(self):
        """Executa verificação rápida"""
        print("⚡ VERIFICAÇÃO RÁPIDA DE SEGURANÇA")
        print("=" * 40)
        print(f"🕐 Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Executa verificações
        self.check_critical_settings()
        self.check_environment_file()
        self.check_database_file()
        self.check_log_files()
        self.check_sensitive_files()
        self.check_python_packages()
        
        # Relatório
        print("\n" + "=" * 40)
        print("📊 RESULTADO DA VERIFICAÇÃO RÁPIDA")
        print("=" * 40)
        
        if self.critical_issues:
            print(f"🚨 PROBLEMAS CRÍTICOS: {len(self.critical_issues)}")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"{i:2d}. {issue}")
        
        if self.warnings:
            print(f"\n⚠️ AVISOS: {len(self.warnings)}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i:2d}. {warning}")
        
        if not self.critical_issues and not self.warnings:
            print("✅ NENHUM PROBLEMA ENCONTRADO")
            print("Sistema passou na verificação rápida")
        
        # Status final
        total_issues = len(self.critical_issues) + len(self.warnings)
        
        if len(self.critical_issues) > 0:
            print(f"\n🔴 STATUS: CRÍTICO ({len(self.critical_issues)} problemas críticos)")
            return False
        elif len(self.warnings) > 3:
            print(f"\n🟡 STATUS: ATENÇÃO ({len(self.warnings)} avisos)")
            return True
        else:
            print(f"\n🟢 STATUS: OK")
            return True


def main():
    """Função principal"""
    try:
        checker = QuickSecurityChecker()
        success = checker.run_quick_check()
        
        print(f"\n⏱️ Verificação concluída em poucos segundos")
        print("💡 Para análise completa, execute: python run_security_tests.py")
        
        if success:
            exit(0)
        else:
            exit(1)
            
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()