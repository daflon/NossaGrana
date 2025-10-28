#!/usr/bin/env python3
"""
Script para gerar certificados SSL usando Python puro (sem OpenSSL)
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_ssl_certificates(domain="localhost", ssl_dir="nginx/ssl"):
    """Gera certificados SSL auto-assinados"""
    
    # Criar diretório SSL
    ssl_path = Path(ssl_dir)
    ssl_path.mkdir(parents=True, exist_ok=True)
    
    print(f"[INFO] Gerando certificados SSL para {domain}...")
    
    # Gerar chave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Criar certificado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SP"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "São Paulo"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NossaGrana"),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Salvar chave privada
    key_file = ssl_path / f"{domain}.key"
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Salvar certificado
    cert_file = ssl_path / f"{domain}.crt"
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print(f"[OK] Certificados gerados:")
    print(f"  - Chave privada: {key_file}")
    print(f"  - Certificado: {cert_file}")
    
    return True

if __name__ == "__main__":
    import ipaddress
    generate_ssl_certificates()