#!/usr/bin/env python3
"""
Configuração automatizada de SSL/TLS para produção
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

class SSLManager:
    def __init__(self):
        self.ssl_dir = Path("nginx/ssl")
        self.ssl_dir.mkdir(parents=True, exist_ok=True)
        
        self.cert_file = self.ssl_dir / "cert.pem"
        self.key_file = self.ssl_dir / "key.pem"
        self.csr_file = self.ssl_dir / "cert.csr"
        
    def log(self, message):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def run_command(self, command, description=""):
        """Executa comando"""
        self.log(f"Executando: {description}")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            self.log(f"✅ {description} - Sucesso")
            return True
        else:
            self.log(f"❌ {description} - Erro: {result.stderr}")
            return False
    
    def generate_self_signed_cert(self, domain="localhost"):
        """Gera certificado auto-assinado para desenvolvimento/teste"""
        self.log("Gerando certificado SSL auto-assinado...")
        
        # Configuração do certificado
        config = f"""[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = BR
ST = SP
L = São Paulo
O = Nossa Grana
OU = IT Department
CN = {domain}

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = {domain}
DNS.2 = localhost
DNS.3 = 127.0.0.1
IP.1 = 127.0.0.1
IP.2 = ::1"""
        
        # Salva configuração
        config_file = self.ssl_dir / "openssl.conf"
        with open(config_file, 'w') as f:
            f.write(config)
        
        # Gera chave privada
        key_cmd = f"openssl genrsa -out {self.key_file} 2048"
        if not self.run_command(key_cmd, "Gerando chave privada"):
            return False
        
        # Gera certificado
        cert_cmd = f"""openssl req -new -x509 -key {self.key_file} \
            -out {self.cert_file} -days 365 \
            -config {config_file}"""
        
        if not self.run_command(cert_cmd, "Gerando certificado"):
            return False
        
        # Remove arquivo de configuração temporário
        config_file.unlink()
        
        self.log("✅ Certificado SSL auto-assinado criado com sucesso!")
        return True
    
    def setup_letsencrypt(self, domain, email):
        """Configura Let's Encrypt (para produção real)"""
        self.log("Configurando Let's Encrypt...")
        
        # Verifica se certbot está instalado
        if not self.run_command("certbot --version", "Verificando Certbot"):
            self.log("Instalando Certbot...")
            
            # Instala certbot (Ubuntu/Debian)
            install_cmd = """apt-get update && \
                apt-get install -y certbot python3-certbot-nginx"""
            
            if not self.run_command(install_cmd, "Instalando Certbot"):
                self.log("❌ Falha ao instalar Certbot")
                return False
        
        # Obtém certificado
        cert_cmd = f"""certbot certonly --standalone \
            --email {email} \
            --agree-tos \
            --no-eff-email \
            -d {domain}"""
        
        if self.run_command(cert_cmd, "Obtendo certificado Let's Encrypt"):
            # Copia certificados para diretório nginx
            le_cert = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
            le_key = f"/etc/letsencrypt/live/{domain}/privkey.pem"
            
            copy_cert = f"cp {le_cert} {self.cert_file}"
            copy_key = f"cp {le_key} {self.key_file}"
            
            if (self.run_command(copy_cert, "Copiando certificado") and
                self.run_command(copy_key, "Copiando chave privada")):
                
                self.log("✅ Let's Encrypt configurado com sucesso!")
                return True
        
        return False
    
    def check_certificate_validity(self):
        """Verifica validade do certificado"""
        if not self.cert_file.exists():
            self.log("❌ Certificado não encontrado")
            return False
        
        # Verifica data de expiração
        cmd = f"openssl x509 -in {self.cert_file} -noout -enddate"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse da data
            end_date_str = result.stdout.strip().replace("notAfter=", "")
            
            try:
                from dateutil import parser
                end_date = parser.parse(end_date_str)
                days_left = (end_date - datetime.now()).days
                
                if days_left > 30:
                    self.log(f"✅ Certificado válido por mais {days_left} dias")
                    return True
                elif days_left > 0:
                    self.log(f"⚠️ Certificado expira em {days_left} dias")
                    return True
                else:
                    self.log("❌ Certificado expirado")
                    return False
                    
            except Exception as e:
                self.log(f"Erro ao verificar data: {e}")
        
        return False
    
    def setup_auto_renewal(self):
        """Configura renovação automática"""
        self.log("Configurando renovação automática...")
        
        # Script de renovação
        renewal_script = """#!/bin/bash
# Renovação automática SSL
certbot renew --quiet --no-self-upgrade

# Reinicia nginx se certificado foi renovado
if [ $? -eq 0 ]; then
    docker-compose -f docker-compose.prod.yml restart nginx
fi"""
        
        script_file = Path("/etc/cron.daily/ssl-renewal")
        
        try:
            with open(script_file, 'w') as f:
                f.write(renewal_script)
            
            # Torna executável
            os.chmod(script_file, 0o755)
            
            self.log("✅ Renovação automática configurada")
            return True
            
        except PermissionError:
            self.log("⚠️ Sem permissão para criar script de renovação")
            self.log("Execute manualmente como root:")
            print(renewal_script)
            return False
    
    def test_ssl_configuration(self):
        """Testa configuração SSL"""
        self.log("Testando configuração SSL...")
        
        # Verifica se arquivos existem
        if not (self.cert_file.exists() and self.key_file.exists()):
            self.log("❌ Arquivos SSL não encontrados")
            return False
        
        # Testa se chave e certificado combinam
        cert_cmd = f"openssl x509 -noout -modulus -in {self.cert_file} | openssl md5"
        key_cmd = f"openssl rsa -noout -modulus -in {self.key_file} | openssl md5"
        
        cert_result = subprocess.run(cert_cmd, shell=True, capture_output=True, text=True)
        key_result = subprocess.run(key_cmd, shell=True, capture_output=True, text=True)
        
        if (cert_result.returncode == 0 and key_result.returncode == 0):
            if cert_result.stdout == key_result.stdout:
                self.log("✅ Certificado e chave privada combinam")
                return True
            else:
                self.log("❌ Certificado e chave privada não combinam")
                return False
        
        self.log("❌ Erro ao verificar certificado")
        return False

def main():
    """Função principal"""
    ssl_manager = SSLManager()
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python ssl_setup.py self-signed [domain]")
        print("  python ssl_setup.py letsencrypt <domain> <email>")
        print("  python ssl_setup.py check")
        print("  python ssl_setup.py renew")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "self-signed":
        domain = sys.argv[2] if len(sys.argv) > 2 else "localhost"
        
        if ssl_manager.generate_self_signed_cert(domain):
            ssl_manager.test_ssl_configuration()
        
    elif command == "letsencrypt":
        if len(sys.argv) < 4:
            print("Uso: python ssl_setup.py letsencrypt <domain> <email>")
            sys.exit(1)
        
        domain = sys.argv[2]
        email = sys.argv[3]
        
        if ssl_manager.setup_letsencrypt(domain, email):
            ssl_manager.setup_auto_renewal()
            ssl_manager.test_ssl_configuration()
    
    elif command == "check":
        ssl_manager.check_certificate_validity()
        ssl_manager.test_ssl_configuration()
    
    elif command == "renew":
        # Para Let's Encrypt
        ssl_manager.run_command("certbot renew", "Renovando certificados")
    
    else:
        print(f"Comando desconhecido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()