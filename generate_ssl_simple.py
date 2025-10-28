#!/usr/bin/env python3
"""
Script simplificado para gerar certificados SSL
"""

import os
import subprocess
from pathlib import Path

def generate_ssl_certificates():
    """Gera certificados SSL para localhost"""
    
    # Criar diretório SSL
    ssl_dir = Path("nginx/ssl")
    ssl_dir.mkdir(parents=True, exist_ok=True)
    
    print("Gerando certificados SSL para localhost...")
    
    # Verificar se OpenSSL está disponível
    try:
        subprocess.run(["openssl", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERRO: OpenSSL nao encontrado. Instalando via chocolatey...")
        try:
            subprocess.run(["choco", "install", "openssl", "-y"], check=True)
        except:
            print("ERRO: Nao foi possivel instalar OpenSSL automaticamente.")
            print("Instale manualmente: https://slproweb.com/products/Win32OpenSSL.html")
            return False
    
    # Gerar chave privada
    print("1. Gerando chave privada...")
    key_file = ssl_dir / "key.pem"
    cmd_key = ["openssl", "genrsa", "-out", str(key_file), "2048"]
    
    try:
        subprocess.run(cmd_key, check=True, capture_output=True)
        print(f"   Chave criada: {key_file}")
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao gerar chave: {e}")
        return False
    
    # Criar arquivo de configuração
    config_file = ssl_dir / "openssl.conf"
    config_content = """[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = BR
ST = SP
L = Sao Paulo
O = NossaGrana
OU = Development
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1
"""
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    # Gerar certificado
    print("2. Gerando certificado...")
    cert_file = ssl_dir / "cert.pem"
    cmd_cert = [
        "openssl", "req", "-new", "-x509",
        "-key", str(key_file),
        "-out", str(cert_file),
        "-days", "365",
        "-config", str(config_file)
    ]
    
    try:
        subprocess.run(cmd_cert, check=True, capture_output=True)
        print(f"   Certificado criado: {cert_file}")
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao gerar certificado: {e}")
        return False
    
    # Definir permissões (Windows)
    try:
        os.chmod(key_file, 0o600)
        os.chmod(cert_file, 0o644)
    except:
        pass  # Permissões no Windows são diferentes
    
    print("\nCertificados SSL gerados com sucesso!")
    print(f"Arquivos criados em: {ssl_dir}")
    print(f"  - Chave privada: {key_file}")
    print(f"  - Certificado: {cert_file}")
    print("\nCertificados prontos para uso com NGINX/Docker!")
    
    return True

if __name__ == "__main__":
    success = generate_ssl_certificates()
    if not success:
        exit(1)