#!/usr/bin/env python3
"""
Script de monitoramento para produção
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

class ProductionMonitor:
    def __init__(self):
        self.base_url = "http://localhost"
        self.api_url = f"{self.base_url}/api"
        self.log_file = Path("logs/monitor.log")
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log(self, message, level="INFO"):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def check_containers(self):
        """Verifica status dos containers"""
        self.log("Verificando status dos containers...")
        
        try:
            result = subprocess.run(
                "docker-compose -f docker-compose.prod.yml ps --format json",
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self.log("Erro ao verificar containers", "ERROR")
                return False
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    containers.append(json.loads(line))
            
            all_healthy = True
            for container in containers:
                name = container.get('Name', 'Unknown')
                state = container.get('State', 'Unknown')
                
                if state == 'running':
                    self.log(f"Container {name}: ✅ {state}")
                else:
                    self.log(f"Container {name}: ❌ {state}", "WARNING")
                    all_healthy = False
            
            return all_healthy
            
        except Exception as e:
            self.log(f"Erro ao verificar containers: {e}", "ERROR")
            return False
    
    def check_api_health(self):
        """Verifica saúde da API"""
        self.log("Verificando saúde da API...")
        
        try:
            response = requests.get(f"{self.api_url}/health/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"API Health: ✅ {data.get('status', 'OK')}")
                return True
            else:
                self.log(f"API Health: ❌ Status {response.status_code}", "WARNING")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Erro ao verificar API: {e}", "ERROR")
            return False
    
    def check_database(self):
        """Verifica conexão com banco de dados"""
        self.log("Verificando banco de dados...")
        
        try:
            cmd = "docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U nossa_grana_user -d nossa_grana_prod"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Database: ✅ Conectado")
                return True
            else:
                self.log("Database: ❌ Não conectado", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Erro ao verificar database: {e}", "ERROR")
            return False
    
    def check_redis(self):
        """Verifica conexão com Redis"""
        self.log("Verificando Redis...")
        
        try:
            cmd = "docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and "PONG" in result.stdout:
                self.log("Redis: ✅ Conectado")
                return True
            else:
                self.log("Redis: ❌ Não conectado", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Erro ao verificar Redis: {e}", "ERROR")
            return False
    
    def check_disk_space(self):
        """Verifica espaço em disco"""
        self.log("Verificando espaço em disco...")
        
        try:
            result = subprocess.run("df -h .", shell=True, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 5:
                    usage = parts[4].replace('%', '')
                    usage_int = int(usage)
                    
                    if usage_int < 80:
                        self.log(f"Disk Space: ✅ {usage}% usado")
                        return True
                    elif usage_int < 90:
                        self.log(f"Disk Space: ⚠️ {usage}% usado", "WARNING")
                        return True
                    else:
                        self.log(f"Disk Space: ❌ {usage}% usado - CRÍTICO", "ERROR")
                        return False
            
            self.log("Não foi possível verificar espaço em disco", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Erro ao verificar espaço em disco: {e}", "ERROR")
            return False
    
    def check_memory_usage(self):
        """Verifica uso de memória dos containers"""
        self.log("Verificando uso de memória...")
        
        try:
            cmd = "docker stats --no-stream --format 'table {{.Name}}\\t{{.MemUsage}}\\t{{.MemPerc}}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Pula cabeçalho
                
                high_memory = []
                for line in lines:
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            name = parts[0]
                            mem_perc = parts[2].replace('%', '')
                            
                            try:
                                mem_perc_float = float(mem_perc)
                                if mem_perc_float > 80:
                                    high_memory.append(f"{name}: {mem_perc}%")
                            except ValueError:
                                pass
                
                if high_memory:
                    self.log(f"Memory: ⚠️ Alto uso: {', '.join(high_memory)}", "WARNING")
                else:
                    self.log("Memory: ✅ Uso normal")
                
                return len(high_memory) == 0
            
            return False
            
        except Exception as e:
            self.log(f"Erro ao verificar memória: {e}", "ERROR")
            return False
    
    def check_logs_for_errors(self):
        """Verifica logs por erros recentes"""
        self.log("Verificando logs por erros...")
        
        try:
            # Verifica logs do Django
            cmd = "docker-compose -f docker-compose.prod.yml logs --tail=100 backend"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            error_keywords = ['ERROR', 'CRITICAL', 'Exception', 'Traceback']
            recent_errors = []
            
            for line in result.stdout.split('\n'):
                if any(keyword in line for keyword in error_keywords):
                    recent_errors.append(line.strip())
            
            if recent_errors:
                self.log(f"Logs: ⚠️ {len(recent_errors)} erros encontrados", "WARNING")
                # Log apenas os últimos 3 erros para não poluir
                for error in recent_errors[-3:]:
                    self.log(f"  {error}", "WARNING")
            else:
                self.log("Logs: ✅ Nenhum erro recente")
            
            return len(recent_errors) == 0
            
        except Exception as e:
            self.log(f"Erro ao verificar logs: {e}", "ERROR")
            return False
    
    def generate_report(self):
        """Gera relatório completo de monitoramento"""
        self.log("=" * 50)
        self.log("RELATÓRIO DE MONITORAMENTO - NOSSA GRANA PRODUÇÃO")
        self.log("=" * 50)
        
        checks = [
            ("Containers", self.check_containers),
            ("API Health", self.check_api_health),
            ("Database", self.check_database),
            ("Redis", self.check_redis),
            ("Disk Space", self.check_disk_space),
            ("Memory Usage", self.check_memory_usage),
            ("Error Logs", self.check_logs_for_errors),
        ]
        
        results = {}
        all_ok = True
        
        for name, check_func in checks:
            try:
                result = check_func()
                results[name] = result
                if not result:
                    all_ok = False
            except Exception as e:
                self.log(f"Erro na verificação {name}: {e}", "ERROR")
                results[name] = False
                all_ok = False
        
        self.log("-" * 50)
        if all_ok:
            self.log("🎉 SISTEMA SAUDÁVEL - Todos os checks passaram")
        else:
            failed_checks = [name for name, result in results.items() if not result]
            self.log(f"⚠️ ATENÇÃO NECESSÁRIA - Falhas em: {', '.join(failed_checks)}", "WARNING")
        
        self.log("=" * 50)
        return all_ok
    
    def continuous_monitoring(self, interval=300):  # 5 minutos
        """Monitoramento contínuo"""
        self.log(f"Iniciando monitoramento contínuo (intervalo: {interval}s)")
        
        try:
            while True:
                self.generate_report()
                self.log(f"Próxima verificação em {interval} segundos...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.log("Monitoramento interrompido pelo usuário")
        except Exception as e:
            self.log(f"Erro no monitoramento contínuo: {e}", "ERROR")

def main():
    """Função principal"""
    monitor = ProductionMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Monitoramento contínuo
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        monitor.continuous_monitoring(interval)
    else:
        # Verificação única
        monitor.generate_report()

if __name__ == "__main__":
    main()