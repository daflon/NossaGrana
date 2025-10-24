#!/bin/bash

# Script avançado para gerar certificados SSL - NossaGrana
set -e

SSL_DIR="nginx/ssl"
DOMAIN="localhost"
KEY_SIZE=2048
DAYS=365

echo "🔐 Gerando certificados SSL para desenvolvimento..."
echo "📂 Diretório: $SSL_DIR"
echo "🌐 Domínio: $DOMAIN"

# Verificar se OpenSSL está instalado
if ! command -v openssl &> /dev/null; then
    echo "❌ OpenSSL não encontrado!"
    echo "💡 Instale: sudo apt install openssl (Ubuntu/Debian)"
    exit 1
fi

# Criar diretório SSL
mkdir -p $SSL_DIR

# Gerar chave privada
echo "🔑 Gerando chave privada RSA $KEY_SIZE bits..."
openssl genrsa -out $SSL_DIR/private.key $KEY_SIZE

# Criar configuração OpenSSL com SAN
echo "📝 Criando configuração OpenSSL..."
cat > $SSL_DIR/openssl.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = BR
ST = SP
L = São Paulo
O = NossaGrana
OU = Development
CN = $DOMAIN

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = DNS:$DOMAIN,DNS:localhost,IP:127.0.0.1
EOF

# Gerar certificado auto-assinado
echo "📜 Gerando certificado auto-assinado válido por $DAYS dias..."
openssl req -new -x509 -key $SSL_DIR/private.key -out $SSL_DIR/certificate.crt -days $DAYS -config $SSL_DIR/openssl.conf

# Gerar parâmetros Diffie-Hellman
echo "🔐 Gerando parâmetros Diffie-Hellman..."
echo "⏳ Isso pode demorar alguns minutos..."
openssl dhparam -out $SSL_DIR/dhparam.pem 2048

# Definir permissões corretas
chmod 600 $SSL_DIR/private.key
chmod 644 $SSL_DIR/certificate.crt
chmod 644 $SSL_DIR/dhparam.pem

# Criar configuração Nginx SSL
echo "📝 Criando configuração Nginx SSL..."
cat > $SSL_DIR/nginx_ssl.conf << EOF
# Configuração SSL para Nginx - NossaGrana
ssl_certificate $SSL_DIR/certificate.crt;
ssl_certificate_key $SSL_DIR/private.key;
ssl_dhparam $SSL_DIR/dhparam.pem;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

add_header Strict-Transport-Security "max-age=63072000" always;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;
EOF

echo ""
echo "🎉 Certificados SSL gerados com sucesso!"
echo "📁 Arquivos salvos em: $SSL_DIR/"
echo "   🔑 Chave privada: private.key"
echo "   📜 Certificado: certificate.crt"
echo "   🔐 Parâmetros DH: dhparam.pem"
echo "   ⚙️  Configuração Nginx: nginx_ssl.conf"
echo ""
echo "🔍 Verificando certificado..."
openssl x509 -in $SSL_DIR/certificate.crt -text -noout | grep -E "Subject:|Not Before:|Not After:|DNS:"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   • Certificados auto-assinados para DESENVOLVIMENTO"
echo "   • Para PRODUÇÃO use certificados válidos"
echo "   • Adicione exceção no navegador se necessário"
echo ""
echo "💡 Para produção com Let's Encrypt:"
echo "   1. sudo apt install certbot python3-certbot-nginx"
echo "   2. sudo certbot --nginx -d seudominio.com"
echo "   3. Renovação automática configurada"