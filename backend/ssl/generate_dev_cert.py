#!/usr/bin/env python3
"""
Script para gerar certificados SSL auto-assinados para desenvolvimento local
"""

import os
import subprocess
from pathlib import Path


def generate_ssl_certificate():
    """
    Gera certificado SSL auto-assinado para desenvolvimento
    """
    ssl_dir = Path(__file__).parent
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = ssl_dir / 'localhost.crt'
    key_file = ssl_dir / 'localhost.key'
    
    # Configuração do certificado
    config_content = """
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = BR
ST = SP
L = São Paulo
O = Nossa Grana Dev
OU = Development
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
DNS.3 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
"""
    
    config_file = ssl_dir / 'cert.conf'
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    try:
        # Gera a chave privada
        subprocess.run([
            'openssl', 'genrsa', '-out', str(key_file), '2048'
        ], check=True)
        
        # Gera o certificado
        subprocess.run([
            'openssl', 'req', '-new', '-x509', '-key', str(key_file),
            '-out', str(cert_file), '-days', '365',
            '-config', str(config_file)
        ], check=True)
        
        print(f"✅ Certificado SSL gerado com sucesso!")
        print(f"📄 Certificado: {cert_file}")
        print(f"🔑 Chave privada: {key_file}")
        print(f"\n🚀 Para usar HTTPS em desenvolvimento:")
        print(f"   1. Defina USE_HTTPS=True no seu .env")
        print(f"   2. Execute: python manage.py runserver_plus --cert-file {cert_file} --key-file {key_file}")
        print(f"   3. Acesse: https://localhost:8000")
        
        # Remove arquivo de configuração temporário
        config_file.unlink()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar certificado: {e}")
        print("💡 Certifique-se de ter o OpenSSL instalado")
    except FileNotFoundError:
        print("❌ OpenSSL não encontrado")
        print("💡 Instale o OpenSSL:")
        print("   - Windows: https://slproweb.com/products/Win32OpenSSL.html")
        print("   - macOS: brew install openssl")
        print("   - Linux: sudo apt-get install openssl")


if __name__ == '__main__':
    generate_ssl_certificate()