#!/usr/bin/env python3
"""
Gerenciador SSL/TLS completo para Nossa Grana
Automatiza criação, validação e renovação de certificados SSL
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class SSLManager:
    def __init__(self, project_root=None):
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = Path(__file__).parent.parent
        
        self.ssl_dir = self.project_root / "nginx" / "ssl"
        self.ssl_dir.mkdir(parents=True, exist_ok=True)
        
        self.cert_file = self.ssl_dir / "cert.pem"
        self.key_file = self.ssl_dir / "key.pem"
        self.ca_cert_file = self.ssl_dir / "ca-cert.pem"
        self.ca_key_file = self.ssl_dir / "ca-key.pem"
        
        # Configurações SSL
        self.ssl_config = {
            "key_size": 2048,
            "validity_days": 365,
            "country": "BR",
            "state": "SP",
            "city": "São Paulo",
            "organization": "Nossa Grana",
            "organizational_unit": "IT Department"
        }
    
    def log(self, message, level="INFO"):
        """Log com timestamp e nível"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def generate_ca_certificate(self):
        """Gera certificado de autoridade certificadora (CA)"""
        self.log("Gerando certificado CA...")
        
        # Gera chave privada CA
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.ssl_config["key_size"]
        )
        
        # Cria certificado CA
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, self.ssl_config["country"]),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.ssl_config["state"]),
            x509.NameAttribute(NameOID.LOCALITY_NAME, self.ssl_config["city"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.ssl_config["organization"]),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, self.ssl_config["organizational_unit"]),
            x509.NameAttribute(NameOID.COMMON_NAME, "Nossa Grana CA"),
        ])
        
        ca_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=self.ssl_config["validity_days"] * 2)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.IPAddress("127.0.0.1"),
            ]),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(ca_key, hashes.SHA256())
        
        # Salva chave privada CA
        with open(self.ca_key_file, "wb") as f:
            f.write(ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Salva certificado CA
        with open(self.ca_cert_file, "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
        
        self.log("✅ Certificado CA criado com sucesso")
        return ca_key, ca_cert
    
    def generate_server_certificate(self, domains=None):
        """Gera certificado do servidor"""
        if domains is None:
            domains = ["localhost", "127.0.0.1", "nossa-grana.local"]
        
        self.log(f"Gerando certificado do servidor para: {', '.join(domains)}")
        
        # Carrega ou cria CA
        if self.ca_cert_file.exists() and self.ca_key_file.exists():
            with open(self.ca_key_file, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)
            
            with open(self.ca_cert_file, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())
        else:
            ca_key, ca_cert = self.generate_ca_certificate()
        
        # Gera chave privada do servidor
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.ssl_config["key_size"]
        )
        
        # Cria certificado do servidor
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, self.ssl_config["country"]),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.ssl_config["state"]),
            x509.NameAttribute(NameOID.LOCALITY_NAME, self.ssl_config["city"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.ssl_config["organization"]),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, self.ssl_config["organizational_unit"]),
            x509.NameAttribute(NameOID.COMMON_NAME, domains[0]),
        ])
        
        # Cria lista de SANs
        san_list = []
        for domain in domains:
            try:
                # Tenta como IP
                import ipaddress
                ip = ipaddress.ip_address(domain)
                san_list.append(x509.IPAddress(ip))
            except ValueError:
                # É um nome DNS
                san_list.append(x509.DNSName(domain))
        
        server_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            server_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=self.ssl_config["validity_days"])
        ).add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            ]),
            critical=True,
        ).sign(ca_key, hashes.SHA256())
        
        # Salva chave privada do servidor
        with open(self.key_file, "wb") as f:
            f.write(server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Salva certificado do servidor
        with open(self.cert_file, "wb") as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))
        
        # Define permissões corretas
        os.chmod(self.key_file, 0o600)
        os.chmod(self.cert_file, 0o644)
        
        self.log("✅ Certificado do servidor criado com sucesso")
        return True
    
    def validate_certificates(self):
        """Valida certificados existentes"""
        self.log("Validando certificados...")
        
        if not (self.cert_file.exists() and self.key_file.exists()):
            self.log("❌ Arquivos de certificado não encontrados", "ERROR")
            return False
        
        try:
            # Carrega certificado
            with open(self.cert_file, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            
            # Carrega chave privada
            with open(self.key_file, "rb") as f:
                key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Verifica se chave e certificado combinam
            cert_public_key = cert.public_key()
            key_public_key = key.public_key()
            
            cert_public_numbers = cert_public_key.public_numbers()
            key_public_numbers = key_public_key.public_numbers()
            
            if (cert_public_numbers.n == key_public_numbers.n and 
                cert_public_numbers.e == key_public_numbers.e):
                self.log("✅ Certificado e chave privada combinam")
            else:
                self.log("❌ Certificado e chave privada não combinam", "ERROR")
                return False
            
            # Verifica validade
            now = datetime.utcnow()
            if now < cert.not_valid_before:
                self.log("❌ Certificado ainda não é válido", "ERROR")
                return False
            elif now > cert.not_valid_after:
                self.log("❌ Certificado expirado", "ERROR")
                return False
            else:
                days_left = (cert.not_valid_after - now).days
                if days_left < 30:
                    self.log(f"⚠️ Certificado expira em {days_left} dias", "WARNING")
                else:
                    self.log(f"✅ Certificado válido por mais {days_left} dias")
            
            # Mostra informações do certificado
            subject = cert.subject
            self.log(f"Certificado para: {subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}")
            
            # Mostra SANs
            try:
                san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                sans = [name.value for name in san_ext.value]
                self.log(f"SANs: {', '.join(sans)}")
            except x509.ExtensionNotFound:
                pass
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao validar certificados: {e}", "ERROR")
            return False
    
    def create_ssl_info_file(self):
        """Cria arquivo com informações SSL"""
        ssl_info = {
            "created_at": datetime.now().isoformat(),
            "cert_file": str(self.cert_file),
            "key_file": str(self.key_file),
            "ca_cert_file": str(self.ca_cert_file),
            "validity_days": self.ssl_config["validity_days"],
            "key_size": self.ssl_config["key_size"]
        }
        
        info_file = self.ssl_dir / "ssl_info.json"
        with open(info_file, 'w') as f:
            json.dump(ssl_info, f, indent=2)
        
        self.log(f"Informações SSL salvas em: {info_file}")
    
    def setup_development_ssl(self, domains=None):
        """Configura SSL para desenvolvimento"""
        self.log("=== Configurando SSL para Desenvolvimento ===")
        
        if domains is None:
            domains = ["localhost", "127.0.0.1", "nossa-grana.local"]
        
        # Gera certificados
        if self.generate_server_certificate(domains):
            self.create_ssl_info_file()
            
            # Valida certificados
            if self.validate_certificates():
                self.log("✅ SSL configurado com sucesso para desenvolvimento!")
                self.log("Para usar HTTPS localmente:")
                self.log("1. Importe o CA certificate no seu navegador:")
                self.log(f"   {self.ca_cert_file}")
                self.log("2. Acesse: https://localhost")
                return True
        
        return False
    
    def check_ssl_requirements(self):
        """Verifica requisitos SSL"""
        self.log("Verificando requisitos SSL...")
        
        # Verifica se diretório SSL existe
        if not self.ssl_dir.exists():
            self.log("❌ Diretório SSL não existe")
            return False
        
        # Verifica permissões
        if not os.access(self.ssl_dir, os.W_OK):
            self.log("❌ Sem permissão de escrita no diretório SSL")
            return False
        
        self.log("✅ Requisitos SSL atendidos")
        return True
    
    def cleanup_old_certificates(self):
        """Remove certificados antigos"""
        self.log("Limpando certificados antigos...")
        
        files_to_remove = [
            self.cert_file,
            self.key_file,
            self.ca_cert_file,
            self.ca_key_file,
            self.ssl_dir / "ssl_info.json"
        ]
        
        for file_path in files_to_remove:
            if file_path.exists():
                file_path.unlink()
                self.log(f"Removido: {file_path}")
        
        self.log("✅ Limpeza concluída")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python ssl_manager.py setup [domains...]")
        print("  python ssl_manager.py validate")
        print("  python ssl_manager.py cleanup")
        print("  python ssl_manager.py info")
        sys.exit(1)
    
    ssl_manager = SSLManager()
    command = sys.argv[1]
    
    if command == "setup":
        domains = sys.argv[2:] if len(sys.argv) > 2 else None
        
        if ssl_manager.check_ssl_requirements():
            ssl_manager.setup_development_ssl(domains)
    
    elif command == "validate":
        ssl_manager.validate_certificates()
    
    elif command == "cleanup":
        ssl_manager.cleanup_old_certificates()
    
    elif command == "info":
        info_file = ssl_manager.ssl_dir / "ssl_info.json"
        if info_file.exists():
            with open(info_file) as f:
                info = json.load(f)
            print(json.dumps(info, indent=2))
        else:
            print("Arquivo de informações SSL não encontrado")
    
    else:
        print(f"Comando desconhecido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()