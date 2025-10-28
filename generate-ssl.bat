@echo off
REM Script para gerar certificados SSL no Windows - NossaGrana
setlocal enabledelayedexpansion

set SSL_DIR=nginx\ssl
set DOMAIN=localhost
set DAYS=365

echo Gerando certificados SSL para desenvolvimento...
echo Diretorio: %SSL_DIR%
echo Dominio: %DOMAIN%

REM Verificar se OpenSSL está disponível
where openssl >nul 2>nul
if %errorlevel% neq 0 (
    echo OpenSSL nao encontrado!
    echo Instale OpenSSL ou use Git Bash
    pause
    exit /b 1
)

REM Criar diretório SSL
if not exist %SSL_DIR% mkdir %SSL_DIR%

REM Gerar chave privada
echo Gerando chave privada...
openssl genrsa -out %SSL_DIR%\key.pem 2048

REM Criar arquivo de configuração
echo [req] > %SSL_DIR%\openssl.conf
echo distinguished_name = req_distinguished_name >> %SSL_DIR%\openssl.conf
echo req_extensions = v3_req >> %SSL_DIR%\openssl.conf
echo prompt = no >> %SSL_DIR%\openssl.conf
echo. >> %SSL_DIR%\openssl.conf
echo [req_distinguished_name] >> %SSL_DIR%\openssl.conf
echo C = BR >> %SSL_DIR%\openssl.conf
echo ST = SP >> %SSL_DIR%\openssl.conf
echo L = Sao Paulo >> %SSL_DIR%\openssl.conf
echo O = NossaGrana >> %SSL_DIR%\openssl.conf
echo OU = Development >> %SSL_DIR%\openssl.conf
echo CN = %DOMAIN% >> %SSL_DIR%\openssl.conf
echo. >> %SSL_DIR%\openssl.conf
echo [v3_req] >> %SSL_DIR%\openssl.conf
echo keyUsage = keyEncipherment, dataEncipherment >> %SSL_DIR%\openssl.conf
echo extendedKeyUsage = serverAuth >> %SSL_DIR%\openssl.conf
echo subjectAltName = DNS:%DOMAIN%,DNS:localhost,IP:127.0.0.1 >> %SSL_DIR%\openssl.conf

REM Gerar certificado
echo Gerando certificado auto-assinado...
openssl req -new -x509 -key %SSL_DIR%\key.pem -out %SSL_DIR%\cert.pem -days %DAYS% -config %SSL_DIR%\openssl.conf

echo.
echo Certificados SSL gerados com sucesso!
echo Arquivos salvos em: %SSL_DIR%\
echo   Chave privada: key.pem
echo   Certificado: cert.pem
echo.
echo IMPORTANTE:
echo   Certificados auto-assinados para DESENVOLVIMENTO
echo   Adicione excecao no navegador se necessario
echo.
pause