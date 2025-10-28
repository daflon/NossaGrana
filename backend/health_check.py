#!/usr/bin/env python3
"""
Health Check Script para Nossa Grana
Verifica se todos os serviços estão funcionando corretamente
"""

import os
import sys
import django
import requests
import psycopg2
import redis
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
django.setup()

from django.db import connection
from django.core.cache import cache
from django.conf import settings

class HealthChecker:
    def __init__(self):
        self.results = {}
        self.overall_status = True

    def check_database(self):
        """Verifica conexão com o banco de dados"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] == 1:
                    self.results['database'] = {'status': 'OK', 'message': 'Conexão com banco funcionando'}
                else:
                    raise Exception("Query retornou resultado inesperado")
        except Exception as e:
            self.results['database'] = {'status': 'ERROR', 'message': f'Erro no banco: {str(e)}'}
            self.overall_status = False

    def check_cache(self):
        """Verifica sistema de cache"""
        try:
            test_key = 'health_check_test'
            test_value = f'test_{datetime.now().timestamp()}'
            
            cache.set(test_key, test_value, 30)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                cache.delete(test_key)
                self.results['cache'] = {'status': 'OK', 'message': 'Cache funcionando'}
            else:
                raise Exception("Valor do cache não confere")
        except Exception as e:
            self.results['cache'] = {'status': 'ERROR', 'message': f'Erro no cache: {str(e)}'}
            self.overall_status = False

    def check_redis(self):
        """Verifica conexão com Redis"""
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            r = redis.from_url(redis_url)
            r.ping()
            self.results['redis'] = {'status': 'OK', 'message': 'Redis funcionando'}
        except Exception as e:
            self.results['redis'] = {'status': 'ERROR', 'message': f'Erro no Redis: {str(e)}'}
            self.overall_status = False

    def check_api_endpoints(self):
        """Verifica endpoints principais da API"""
        base_url = 'http://localhost:8000'
        endpoints = [
            '/api/health/',
            '/api/accounts/profile/',
            '/api/transactions/',
        ]
        
        api_results = {}
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code in [200, 401]:  # 401 é OK para endpoints protegidos
                    api_results[endpoint] = 'OK'
                else:
                    api_results[endpoint] = f'HTTP {response.status_code}'
                    self.overall_status = False
            except Exception as e:
                api_results[endpoint] = f'ERROR: {str(e)}'
                self.overall_status = False
        
        self.results['api_endpoints'] = {
            'status': 'OK' if all(status == 'OK' for status in api_results.values()) else 'ERROR',
            'endpoints': api_results
        }

    def check_disk_space(self):
        """Verifica espaço em disco"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_percent = (free / total) * 100
            
            if free_percent > 10:
                status = 'OK'
                message = f'Espaço livre: {free_percent:.1f}%'
            elif free_percent > 5:
                status = 'WARNING'
                message = f'Pouco espaço livre: {free_percent:.1f}%'
            else:
                status = 'ERROR'
                message = f'Espaço crítico: {free_percent:.1f}%'
                self.overall_status = False
            
            self.results['disk_space'] = {'status': status, 'message': message}
        except Exception as e:
            self.results['disk_space'] = {'status': 'ERROR', 'message': f'Erro ao verificar disco: {str(e)}'}

    def run_all_checks(self):
        """Executa todos os health checks"""
        print("🏥 Executando Health Checks...")
        print("=" * 50)
        
        checks = [
            ('Database', self.check_database),
            ('Cache', self.check_cache),
            ('Redis', self.check_redis),
            ('API Endpoints', self.check_api_endpoints),
            ('Disk Space', self.check_disk_space),
        ]
        
        for name, check_func in checks:
            print(f"Verificando {name}...", end=' ')
            try:
                check_func()
                result = self.results.get(name.lower().replace(' ', '_'), {})
                status = result.get('status', 'UNKNOWN')
                if status == 'OK':
                    print("✅")
                elif status == 'WARNING':
                    print("⚠️")
                else:
                    print("❌")
            except Exception as e:
                print(f"❌ Erro: {str(e)}")
                self.overall_status = False
        
        print("\n" + "=" * 50)
        print("📊 Resultados Detalhados:")
        print("=" * 50)
        
        for check_name, result in self.results.items():
            status_icon = "✅" if result['status'] == 'OK' else "⚠️" if result['status'] == 'WARNING' else "❌"
            print(f"{status_icon} {check_name.replace('_', ' ').title()}: {result['message']}")
            
            if 'endpoints' in result:
                for endpoint, status in result['endpoints'].items():
                    endpoint_icon = "✅" if status == 'OK' else "❌"
                    print(f"   {endpoint_icon} {endpoint}: {status}")
        
        print("\n" + "=" * 50)
        if self.overall_status:
            print("🎉 Todos os serviços estão funcionando corretamente!")
            return 0
        else:
            print("⚠️  Alguns serviços apresentam problemas!")
            return 1

def main():
    """Função principal"""
    checker = HealthChecker()
    return checker.run_all_checks()

if __name__ == '__main__':
    sys.exit(main())