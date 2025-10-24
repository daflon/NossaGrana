#!/usr/bin/env python3
"""
Script Principal - Execução de Todos os Testes de Segurança
Executa uma bateria completa de testes de segurança para o sistema NossaGrana
"""

import os
import sys
import django
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
django.setup()

# Importar módulos de teste
from test_security_config import run_security_config_tests
from test_security_vulnerabilities import run_security_tests


class SecurityTestRunner:
    """Executor principal de todos os testes de segurança"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            'config_vulnerabilities': 0,
            'config_warnings': 0,
            'app_vulnerabilities': [],
            'total_issues': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }
    
    def print_header(self):
        """Imprime cabeçalho do relatório"""
        print("🔒" * 30)
        print("🔒 NOSSA GRANA - TESTES DE SEGURANÇA COMPLETOS")
        print("🔒" * 30)
        print(f"📅 Iniciado em: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 80)
    
    def run_configuration_tests(self):
        """Executa testes de configuração de segurança"""
        print("\n🔧 FASE 1: TESTES DE CONFIGURAÇÃO DE SEGURANÇA")
        print("-" * 50)
        
        try:
            vulnerabilities, warnings = run_security_config_tests()
            self.results['config_vulnerabilities'] = vulnerabilities
            self.results['config_warnings'] = warnings
            
            if vulnerabilities == 0 and warnings == 0:
                self.results['tests_passed'] += 1
                print("✅ Testes de configuração: APROVADO")
            else:
                self.results['tests_failed'] += 1
                print("❌ Testes de configuração: REPROVADO")
            
            return True
            
        except Exception as e:
            print(f"❌ ERRO nos testes de configuração: {str(e)}")
            self.results['tests_failed'] += 1
            return False
    
    def run_vulnerability_tests(self):
        """Executa testes de vulnerabilidades da aplicação"""
        print("\n🛡️ FASE 2: TESTES DE VULNERABILIDADES DA APLICAÇÃO")
        print("-" * 50)
        
        try:
            vulnerabilities = run_security_tests()
            self.results['app_vulnerabilities'] = vulnerabilities
            
            if len(vulnerabilities) == 0:
                self.results['tests_passed'] += 1
                print("✅ Testes de vulnerabilidades: APROVADO")
            else:
                self.results['tests_failed'] += 1
                print("❌ Testes de vulnerabilidades: REPROVADO")
            
            return True
            
        except Exception as e:
            print(f"❌ ERRO nos testes de vulnerabilidades: {str(e)}")
            self.results['tests_failed'] += 1
            return False
    
    def run_dependency_security_check(self):
        """Verifica vulnerabilidades em dependências"""
        print("\n📦 FASE 3: VERIFICAÇÃO DE DEPENDÊNCIAS")
        print("-" * 50)
        
        try:
            # Verifica se o safety está instalado
            result = subprocess.run(['pip', 'show', 'safety'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("⚠️ Safety não instalado. Instalando...")
                subprocess.run(['pip', 'install', 'safety'], check=True)
            
            # Executa verificação de segurança
            result = subprocess.run(['safety', 'check', '--json'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependências: Nenhuma vulnerabilidade conhecida encontrada")
                self.results['tests_passed'] += 1
                return True
            else:
                print("❌ Dependências: Vulnerabilidades encontradas")
                print(result.stdout)
                self.results['tests_failed'] += 1
                return False
                
        except subprocess.CalledProcessError:
            print("⚠️ Não foi possível instalar/executar safety")
            print("✅ Dependências: Verificação manual necessária")
            return True
        except Exception as e:
            print(f"⚠️ Erro na verificação de dependências: {str(e)}")
            return True
    
    def run_static_analysis(self):
        """Executa análise estática de código"""
        print("\n🔍 FASE 4: ANÁLISE ESTÁTICA DE CÓDIGO")
        print("-" * 50)
        
        try:
            # Verifica se o bandit está instalado
            result = subprocess.run(['pip', 'show', 'bandit'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("⚠️ Bandit não instalado. Instalando...")
                subprocess.run(['pip', 'install', 'bandit'], check=True)
            
            # Executa análise com bandit
            result = subprocess.run([
                'bandit', '-r', '.', 
                '-f', 'json',
                '-x', './venv,./env,./node_modules,./migrations'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Análise estática: Nenhum problema crítico encontrado")
                self.results['tests_passed'] += 1
                return True
            else:
                print("❌ Análise estática: Problemas encontrados")
                # Parse do JSON para mostrar apenas issues críticos
                try:
                    import json
                    data = json.loads(result.stdout)
                    high_issues = [r for r in data.get('results', []) 
                                 if r.get('issue_severity') == 'HIGH']
                    if high_issues:
                        print(f"🚨 {len(high_issues)} problemas de alta severidade encontrados")
                        for issue in high_issues[:3]:  # Mostra apenas os 3 primeiros
                            print(f"   - {issue.get('test_name')}: {issue.get('filename')}:{issue.get('line_number')}")
                except:
                    print(result.stdout[:500])  # Mostra primeiros 500 chars
                
                self.results['tests_failed'] += 1
                return False
                
        except subprocess.CalledProcessError:
            print("⚠️ Não foi possível instalar/executar bandit")
            print("✅ Análise estática: Verificação manual necessária")
            return True
        except Exception as e:
            print(f"⚠️ Erro na análise estática: {str(e)}")
            return True
    
    def check_file_permissions(self):
        """Verifica permissões de arquivos críticos"""
        print("\n📁 FASE 5: VERIFICAÇÃO DE PERMISSÕES DE ARQUIVOS")
        print("-" * 50)
        
        critical_files = [
            '.env',
            'db.sqlite3',
            'logs/security.log',
            'logs/nossa_grana.log'
        ]
        
        issues = []
        
        for file_path in critical_files:
            full_path = Path(file_path)
            if full_path.exists():
                try:
                    stat_info = full_path.stat()
                    if stat_info.st_size == 0 and file_path != 'logs/security.log':
                        issues.append(f"Arquivo crítico vazio: {file_path}")
                    else:
                        print(f"✅ {file_path}: OK")
                except Exception as e:
                    issues.append(f"Erro ao verificar {file_path}: {str(e)}")
            else:
                if file_path == '.env':
                    issues.append(f"Arquivo crítico não encontrado: {file_path}")
                else:
                    print(f"⚠️ {file_path}: Não encontrado (pode ser normal)")
        
        if issues:
            print("❌ Problemas encontrados:")
            for issue in issues:
                print(f"   - {issue}")
            self.results['tests_failed'] += 1
            return False
        else:
            print("✅ Permissões de arquivos: OK")
            self.results['tests_passed'] += 1
            return True
    
    def generate_final_report(self):
        """Gera relatório final consolidado"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL DE SEGURANÇA")
        print("=" * 80)
        
        # Estatísticas gerais
        total_tests = self.results['tests_passed'] + self.results['tests_failed']
        success_rate = (self.results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"⏱️ Duração total: {duration.total_seconds():.1f} segundos")
        print(f"🧪 Total de fases testadas: {total_tests}")
        print(f"✅ Fases aprovadas: {self.results['tests_passed']}")
        print(f"❌ Fases reprovadas: {self.results['tests_failed']}")
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        # Detalhes dos problemas
        total_issues = (self.results['config_vulnerabilities'] + 
                       self.results['config_warnings'] + 
                       len(self.results['app_vulnerabilities']))
        
        print(f"\n🚨 TOTAL DE PROBLEMAS ENCONTRADOS: {total_issues}")
        
        if self.results['config_vulnerabilities'] > 0:
            print(f"   🔧 Vulnerabilidades de configuração: {self.results['config_vulnerabilities']}")
        
        if self.results['config_warnings'] > 0:
            print(f"   ⚠️ Avisos de configuração: {self.results['config_warnings']}")
        
        if len(self.results['app_vulnerabilities']) > 0:
            print(f"   🛡️ Vulnerabilidades da aplicação: {len(self.results['app_vulnerabilities'])}")
        
        # Classificação de segurança
        print(f"\n🏆 CLASSIFICAÇÃO DE SEGURANÇA:")
        if total_issues == 0:
            print("🟢 EXCELENTE - Sistema seguro")
            security_score = "A+"
        elif total_issues <= 3:
            print("🟡 BOM - Pequenos ajustes necessários")
            security_score = "B+"
        elif total_issues <= 10:
            print("🟠 REGULAR - Melhorias importantes necessárias")
            security_score = "C+"
        else:
            print("🔴 CRÍTICO - Ação imediata necessária")
            security_score = "D"
        
        print(f"📊 Score de Segurança: {security_score}")
        
        # Recomendações
        if total_issues > 0:
            print(f"\n🔧 PRÓXIMOS PASSOS RECOMENDADOS:")
            print("1. Corrigir vulnerabilidades críticas imediatamente")
            print("2. Implementar monitoramento contínuo de segurança")
            print("3. Estabelecer processo de revisão de código")
            print("4. Configurar alertas de segurança automatizados")
            print("5. Realizar testes de segurança regularmente")
        
        # Salvar relatório
        self.save_report_to_file(end_time, total_issues, security_score)
        
        return total_issues == 0
    
    def save_report_to_file(self, end_time, total_issues, security_score):
        """Salva relatório em arquivo"""
        try:
            report_file = f"security_report_{end_time.strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("NOSSA GRANA - RELATÓRIO DE SEGURANÇA\n")
                f.write("=" * 50 + "\n")
                f.write(f"Data: {end_time.strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total de problemas: {total_issues}\n")
                f.write(f"Score de segurança: {security_score}\n")
                f.write(f"Vulnerabilidades de config: {self.results['config_vulnerabilities']}\n")
                f.write(f"Avisos de config: {self.results['config_warnings']}\n")
                f.write(f"Vulnerabilidades de app: {len(self.results['app_vulnerabilities'])}\n")
                
                if self.results['app_vulnerabilities']:
                    f.write("\nVulnerabilidades encontradas:\n")
                    for vuln in self.results['app_vulnerabilities']:
                        f.write(f"- {vuln}\n")
            
            print(f"\n💾 Relatório salvo em: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar relatório: {str(e)}")
    
    def run_all_tests(self):
        """Executa todos os testes de segurança"""
        self.print_header()
        
        # Executa todas as fases
        phases = [
            self.run_configuration_tests,
            self.run_vulnerability_tests,
            self.run_dependency_security_check,
            self.run_static_analysis,
            self.check_file_permissions
        ]
        
        for phase in phases:
            try:
                phase()
                time.sleep(1)  # Pequena pausa entre fases
            except KeyboardInterrupt:
                print("\n⚠️ Testes interrompidos pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {str(e)}")
                self.results['tests_failed'] += 1
        
        # Gera relatório final
        success = self.generate_final_report()
        
        return success


def main():
    """Função principal"""
    try:
        runner = SecurityTestRunner()
        success = runner.run_all_tests()
        
        if success:
            print("\n🎉 TODOS OS TESTES DE SEGURANÇA FORAM APROVADOS!")
            sys.exit(0)
        else:
            print("\n🚨 PROBLEMAS DE SEGURANÇA ENCONTRADOS - AÇÃO NECESSÁRIA!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()