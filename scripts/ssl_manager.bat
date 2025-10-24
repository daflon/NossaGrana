@echo off
REM Script Windows para gerenciar certificados SSL - NossaGrana

setlocal enabledelayedexpansion

set SSL_DIR=nginx\ssl
set DOMAIN=localhost
set OPENSSL_CONF=openssl.cnf

echo 🔐 Gerenciador de Certificados SSL - NossaGrana
echo.

REM Verificar se OpenSSL está instalado
where openssl >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ OpenSSL não encontrado!
    echo 💡 Instale o OpenSSL:
    echo    - Chocolatey: choco install openssl
    echo    - Manual: https://slproweb.com/products/Win32OpenSSL.html
    pause
    exit /b 1
)

REM Criar diretório SSL
if not exist "%SSL_DIR%" mkdir "%SSL_DIR%"

echo 🔑 Gerando chave privada RSA 2048 bits...
openssl genrsa -out "%SSL_DIR%\private.key" 2048
if %errorlevel% neq 0 (
    echo ❌ Erro ao gerar chave privada
    pause
    exit /b 1
)

echo 📝 Criando configuração OpenSSL...
(
echo [req]
echo distinguished_name = req_distinguished_name
echo req_extensions = v3_req
echo prompt = no
echo.
echo [req_distinguished_name]
echo C = BR
echo ST = SP
echo L = São Paulo
echo O = NossaGrana
echo OU = Development
echo CN = %DOMAIN%
echo.
echo [v3_req]
echo keyUsage = keyEncipherment, dataEncipherment
echo extendedKeyUsage = serverAuth
echo subjectAltName = DNS:%DOMAIN%,DNS:localhost,IP:127.0.0.1
) > "%SSL_DIR%\%OPENSSL_CONF%"

echo 📜 Gerando certificado auto-assinado válido por 365 dias...
openssl req -new -x509 -key "%SSL_DIR%\private.key" -out "%SSL_DIR%\certificate.crt" -days 365 -config "%SSL_DIR%\%OPENSSL_CONF%"
if %errorlevel% neq 0 (
    echo ❌ Erro ao gerar certificado
    pause
    exit /b 1
)

echo 🔐 Gerando parâmetros Diffie-Hellman...
echo ⏳ Isso pode demorar alguns minutos...
openssl dhparam -out "%SSL_DIR%\dhparam.pem" 2048
if %errorlevel% neq 0 (
    echo ❌ Erro ao gerar parâmetros DH
    pause
    exit /b 1
)

echo 📝 Criando configuração Nginx SSL...
(
echo # Configuração SSL para Nginx - NossaGrana
echo ssl_certificate %SSL_DIR%/certificate.crt;
echo ssl_certificate_key %SSL_DIR%/private.key;
echo ssl_dhparam %SSL_DIR%/dhparam.pem;
echo.
echo ssl_protocols TLSv1.2 TLSv1.3;
echo ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
echo ssl_prefer_server_ciphers off;
echo.
echo add_header Strict-Transport-Security "max-age=63072000" always;
echo ssl_session_timeout 1d;
echo ssl_session_cache shared:SSL:50m;
echo ssl_session_tickets off;
) > "%SSL_DIR%\nginx_ssl.conf"

echo.
echo 🎉 Certificados SSL gerados com sucesso!
echo 📂 Arquivos salvos em: %SSL_DIR%\
echo    🔑 Chave privada: private.key
echo    📜 Certificado: certificate.crt
echo    🔐 Parâmetros DH: dhparam.pem
echo    ⚙️  Configuração Nginx: nginx_ssl.conf
echo.
echo ⚠️  IMPORTANTE:
echo    • Certificados auto-assinados para DESENVOLVIMENTO
echo    • Para PRODUÇÃO use certificados válidos
echo    • Adicione exceção no navegador se necessário
echo.

REM Verificar certificado
echo 🔍 Informações do certificado:
openssl x509 -in "%SSL_DIR%\certificate.crt" -text -noout | findstr "Subject:\|Not Before:\|Not After:\|DNS:"

echo.
echo 💡 Para produção com Let's Encrypt:
echo    1. Instale certbot
echo    2. certbot --nginx -d seudominio.com
echo    3. Configuração automática de renovação
echo.

pause