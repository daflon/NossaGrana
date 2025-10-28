#!/usr/bin/env python3
"""
Script para gerar certificados SSL para o projeto NossaGrana
Suporta certificados auto-assinados para desenvolvimento e configuração para produção
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class SSLCertificateGenerator:
    def __init__(self, ssl_dir="nginx/ssl", domain="localhost"):
        self.ssl_dir = Path(ssl_dir)
        self.domain = domain
        self.ssl_dir.mkdir(parents=True, exist_ok=True)
        
    def check_openssl(self):
        """Verifica se OpenSSL está instalado"""
        try:
            subprocess.run(["openssl", "version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ERRO] OpenSSL não encontrado. Instale o OpenSSL primeiro.")
            return False
    
    def generate_private_key(self, key_size=2048):
        """Gera chave privada RSA"""
        key_file = self.ssl_dir / "private.key"
        print(f"[INFO] Gerando chave privada RSA de {key_size} bits...")
        
        cmd = [
            "openssl", "genrsa",
            "-out", str(key_file),
            str(key_size)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            os.chmod(key_file, 0o600)
            print(f"[OK] Chave privada gerada: {key_file}")
            return key_file
        except subprocess.CalledProcessError as e:
            print(f"[ERRO] Erro ao gerar chave privada: {e}")
            return None
    
    def generate_self_signed_cert(self, key_file, days=365, san_domains=None):
        """Gera certificado auto-assinado"""
        cert_file = self.ssl_dir / "certificate.crt"
        config_file = self.ssl_dir / "openssl.conf"
        
        self._create_openssl_config(config_file, san_domains)
        
        print(f"[INFO] Gerando certificado auto-assinado válido por {days} dias...")
        
        cmd = [
            "openssl", "req", "-new", "-x509",
            "-key", str(key_file),
            "-out", str(cert_file),
            "-days", str(days),
            "-config", str(config_file)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            os.chmod(cert_file, 0o644)
            print(f"[OK] Certificado gerado: {cert_file}")
            return cert_file
        except subprocess.CalledProcessError as e:
            print(f"[ERRO] Erro ao gerar certificado: {e}")
            return None
    
    def _create_openssl_config(self, config_file, san_domains=None):
        """Cria arquivo de configuração OpenSSL com SAN"""
        if not san_domains:
            san_domains = [self.domain, "localhost", "127.0.0.1"]
        
        san_list = ",".join([f"DNS:{domain}" if not domain.replace('.', '').isdigit() 
                            else f"IP:{domain}" for domain in san_domains])
        
        config_content = f"""[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = BR
ST = SP
L = São Paulo
O = NossaGrana
OU = Development
CN = {self.domain}

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = {san_list}
"""
        
        with open(config_file, 'w') as f:
            f.write(config_content)
    
    def generate_dhparam(self, size=2048):
        """Gera parâmetros Diffie-Hellman"""
        dhparam_file = self.ssl_dir / "dhparam.pem"
        
        print(f"[INFO] Gerando parâmetros Diffie-Hellman de {size} bits...")
        
        cmd = [
            "openssl", "dhparam",
            "-out", str(dhparam_file),
            str(size)
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"[OK] Parâmetros DH gerados: {dhparam_file}")
            return dhparam_file
        except subprocess.CalledProcessError as e:
            print(f"[ERRO] Erro ao gerar parâmetros DH: {e}")
            return None
    
    def create_nginx_ssl_config(self):
        """Cria configuração SSL para Nginx"""
        config_content = f"""# Configuração SSL para Nginx - NossaGrana
ssl_certificate {self.ssl_dir}/certificate.crt;
ssl_certificate_key {self.ssl_dir}/private.key;
ssl_dhparam {self.ssl_dir}/dhparam.pem;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

add_header Strict-Transport-Security "max-age=63072000" always;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;
"""
        
        config_file = self.ssl_dir / "nginx_ssl.conf"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"[INFO] Configuração Nginx criada: {config_file}")
        return config_file
    
    def generate_development_certificates(self, domains=None, key_size=2048, days=365):
        """Gera certificados completos para desenvolvimento"""
        print("[INFO] Iniciando geração de certificados SSL...")
        
        if not self.check_openssl():
            return False
        
        key_file = self.generate_private_key(key_size)
        if not key_file:
            return False
        
        cert_file = self.generate_self_signed_cert(key_file, days, domains)
        if not cert_file:
            return False
        
        self.generate_dhparam()
        self.create_nginx_ssl_config()
        
        print("\n[SUCESSO] Certificados SSL gerados com sucesso!")
        print(f"[INFO] Arquivos em: {self.ssl_dir}")
        print("[AVISO] Certificados auto-assinados para DESENVOLVIMENTO")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Gerador de certificados SSL")
    parser.add_argument("--domain", default="localhost", help="Domínio principal")
    parser.add_argument("--ssl-dir", default="nginx/ssl", help="Diretório SSL")
    parser.add_argument("--key-size", type=int, default=2048, help="Tamanho da chave")
    parser.add_argument("--days", type=int, default=365, help="Validade em dias")
    
    args = parser.parse_args()
    
    generator = SSLCertificateGenerator(args.ssl_dir, args.domain)
    success = generator.generate_development_certificates(
        key_size=args.key_size,
        days=args.days
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()