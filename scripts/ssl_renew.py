#!/usr/bin/env python3
"""
Script para renovação automática de certificados SSL
"""

import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ssl_renewal.log'),
        logging.StreamHandler()
    ]
)

class SSLRenewer:
    def __init__(self):
        self.ssl_dir = Path("nginx/ssl")
        self.cert_file = self.ssl_dir / "cert.pem"
        self.key_file = self.ssl_dir / "key.pem"
        self.domain = os.getenv('DOMAIN', 'localhost')
        
    def check_certificate_expiry(self):
        """Verifica se o certificado está próximo do vencimento"""
        if not self.cert_file.exists():
            logging.warning("Certificado não encontrado")
            return True
        
        try:
            # Verificar data de expiração
            result = subprocess.run([
                'openssl', 'x509', '-in', str(self.cert_file), 
                '-noout', '-enddate'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.error("Erro ao verificar certificado")
                return True
            
            # Extrair data de expiração
            end_date_str = result.stdout.strip().split('=')[1]
            end_date = datetime.strptime(end_date_str, '%b %d %H:%M:%S %Y %Z')
            
            # Verificar se expira em menos de 30 dias
            days_until_expiry = (end_date - datetime.now()).days
            
            logging.info(f"Certificado expira em {days_until_expiry} dias")
            
            return days_until_expiry <= 30
            
        except Exception as e:
            logging.error(f"Erro ao verificar expiração: {e}")
            return True
    
    def renew_letsencrypt(self):
        """Renova certificado Let's Encrypt"""
        try:
            logging.info("Renovando certificado Let's Encrypt...")
            
            result = subprocess.run([
                'certbot', 'renew', '--nginx', '--quiet'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("Certificado renovado com sucesso")
                return True
            else:
                logging.error(f"Erro na renovação: {result.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"Erro ao renovar certificado: {e}")
            return False
    
    def generate_self_signed(self):
        """Gera certificado auto-assinado para desenvolvimento"""
        try:
            logging.info("Gerando certificado auto-assinado...")
            
            # Criar diretório se não existir
            self.ssl_dir.mkdir(exist_ok=True)
            
            # Gerar chave privada
            subprocess.run([
                'openssl', 'genrsa', '-out', str(self.key_file), '2048'
            ], check=True)
            
            # Gerar certificado
            subprocess.run([
                'openssl', 'req', '-new', '-x509',
                '-key', str(self.key_file),
                '-out', str(self.cert_file),
                '-days', '365',
                '-subj', f'/C=BR/ST=SP/L=São Paulo/O=NossaGrana/CN={self.domain}'
            ], check=True)
            
            # Definir permissões
            os.chmod(self.key_file, 0o600)
            os.chmod(self.cert_file, 0o644)
            
            logging.info("Certificado auto-assinado gerado com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao gerar certificado: {e}")
            return False
    
    def restart_nginx(self):
        """Reinicia Nginx para aplicar novos certificados"""
        try:
            logging.info("Reiniciando Nginx...")
            
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.prod.yml',
                'restart', 'nginx'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("Nginx reiniciado com sucesso")
                return True
            else:
                logging.error(f"Erro ao reiniciar Nginx: {result.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"Erro ao reiniciar Nginx: {e}")
            return False
    
    def run_renewal(self):
        """Executa processo de renovação"""
        logging.info("Iniciando processo de renovação SSL")
        
        # Verificar se precisa renovar
        if not self.check_certificate_expiry():
            logging.info("Certificado ainda válido, não precisa renovar")
            return True
        
        # Tentar renovar Let's Encrypt primeiro
        if self.renew_letsencrypt():
            self.restart_nginx()
            return True
        
        # Se falhar, gerar auto-assinado para desenvolvimento
        logging.warning("Falha na renovação Let's Encrypt, gerando auto-assinado")
        if self.generate_self_signed():
            self.restart_nginx()
            return True
        
        logging.error("Falha em todos os métodos de renovação")
        return False

def main():
    # Criar diretório de logs
    Path("logs").mkdir(exist_ok=True)
    
    renewer = SSLRenewer()
    
    if renewer.run_renewal():
        logging.info("Renovação SSL concluída com sucesso")
        sys.exit(0)
    else:
        logging.error("Falha na renovação SSL")
        sys.exit(1)

if __name__ == "__main__":
    main()