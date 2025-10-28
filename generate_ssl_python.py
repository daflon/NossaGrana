#!/usr/bin/env python3
"""
Gerador de certificados SSL usando Python puro
"""

import os
import datetime
from pathlib import Path

def install_cryptography():
    """Instala a biblioteca cryptography se necessário"""
    try:
        import cryptography
        return True
    except ImportError:
        print("Instalando biblioteca cryptography...")
        import subprocess
        try:
            subprocess.run(["pip", "install", "cryptography"], check=True)
            return True
        except:
            print("ERRO: Nao foi possivel instalar cryptography")
            return False

def generate_ssl_certificates():
    """Gera certificados SSL usando Python"""
    
    if not install_cryptography():
        return False
    
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import ipaddress
    except ImportError as e:
        print(f"ERRO: Nao foi possivel importar cryptography: {e}")
        return False
    
    # Criar diretório SSL
    ssl_dir = Path("nginx/ssl")
    ssl_dir.mkdir(parents=True, exist_ok=True)
    
    print("Gerando certificados SSL para localhost...")
    
    # Gerar chave privada
    print("1. Gerando chave privada RSA 2048 bits...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Criar certificado
    print("2. Gerando certificado auto-assinado...")
    
    # Definir subject
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SP"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Sao Paulo"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NossaGrana"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Development"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    # Criar certificado
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            data_encipherment=True,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            content_commitment=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    ).add_extension(
        x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
        ]),
        critical=True,
    ).sign(private_key, hashes.SHA256())
    
    # Salvar chave privada
    key_file = ssl_dir / "key.pem"
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Salvar certificado
    cert_file = ssl_dir / "cert.pem"
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print(f"\nCertificados SSL gerados com sucesso!")
    print(f"Arquivos criados em: {ssl_dir}")
    print(f"  - Chave privada: {key_file}")
    print(f"  - Certificado: {cert_file}")
    print(f"\nValidade: 365 dias")
    print(f"Dominios: localhost, 127.0.0.1")
    print(f"\nCertificados prontos para uso com NGINX/Docker!")
    
    return True

if __name__ == "__main__":
    success = generate_ssl_certificates()
    if not success:
        exit(1)