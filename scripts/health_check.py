#!/usr/bin/env python3
"""
Health Check Script para monitoramento da aplicação
"""

import os
import sys
import requests
import psycopg2
import redis
import json
from datetime import datetime

class HealthChecker:
    def __init__(self):
        self.results = {}
        self.base_url = os.getenv('BASE_URL', 'http://localhost')
        
    def check_api(self):
        """Verifica se a API está respondendo"""
        try:
            response = requests.get(f"{self.base_url}/api/health/", timeout=10)
            if response.status_code == 200:
                self.results['api'] = {'status': 'healthy', 'response_time': response.elapsed.total_seconds()}
                return True
            else:
                self.results['api'] = {'status': 'unhealthy', 'error': f'HTTP {response.status_code}'}
                return False
        except Exception as e:
            self.results['api'] = {'status': 'unhealthy', 'error': str(e)}
            return False
    
    def check_database(self):
        """Verifica conexão com PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('POSTGRES_DB', 'nossa_grana_prod'),
                user=os.getenv('POSTGRES_USER', 'nossa_grana_user'),
                password=os.getenv('POSTGRES_PASSWORD', ''),
                port=os.getenv('DB_PORT', '5432')
            )
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            cursor.close()
            conn.close()
            
            self.results['database'] = {'status': 'healthy'}
            return True
        except Exception as e:
            self.results['database'] = {'status': 'unhealthy', 'error': str(e)}
            return False
    
    def check_redis(self):
        """Verifica conexão com Redis"""
        try:
            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                db=0
            )
            r.ping()
            
            self.results['redis'] = {'status': 'healthy'}
            return True
        except Exception as e:
            self.results['redis'] = {'status': 'unhealthy', 'error': str(e)}
            return False
    
    def check_disk_space(self):
        """Verifica espaço em disco"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            
            usage_percent = (used / total) * 100
            
            if usage_percent < 80:
                status = 'healthy'
            elif usage_percent < 90:
                status = 'warning'
            else:
                status = 'critical'
            
            self.results['disk'] = {
                'status': status,
                'usage_percent': round(usage_percent, 2),
                'free_gb': round(free / (1024**3), 2),
                'total_gb': round(total / (1024**3), 2)
            }
            
            return status != 'critical'
        except Exception as e:
            self.results['disk'] = {'status': 'unhealthy', 'error': str(e)}
            return False
    
    def run_all_checks(self):
        """Executa todas as verificações"""
        checks = [
            ('API', self.check_api),
            ('Database', self.check_database),
            ('Redis', self.check_redis),
            ('Disk Space', self.check_disk_space),
        ]
        
        all_healthy = True
        
        for name, check_func in checks:
            print(f"Verificando {name}...")
            if not check_func():
                all_healthy = False
        
        return all_healthy
    
    def generate_report(self):
        """Gera relatório de saúde"""
        timestamp = datetime.now().isoformat()
        
        report = {
            'timestamp': timestamp,
            'overall_status': 'healthy' if all(
                result.get('status') == 'healthy' 
                for result in self.results.values()
            ) else 'unhealthy',
            'checks': self.results
        }
        
        return report

def main():
    checker = HealthChecker()
    
    print("🏥 Executando Health Check...")
    print("=" * 40)
    
    all_healthy = checker.run_all_checks()
    report = checker.generate_report()
    
    print("\n📊 Relatório:")
    print(json.dumps(report, indent=2))
    
    if all_healthy:
        print("\n✅ Sistema saudável!")
        sys.exit(0)
    else:
        print("\n❌ Problemas detectados!")
        sys.exit(1)

if __name__ == "__main__":
    main()