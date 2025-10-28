@echo off
REM Quick start para produção - NossaGrana
echo Iniciando NossaGrana em modo producao...

REM Verificar se já foi configurado
if not exist "nginx\ssl\cert.pem" (
    echo Primeira execucao - executando setup completo...
    call setup_prod_localhost.bat
) else (
    echo Iniciando sistema existente...
    docker-compose -f docker-compose.prod.yml up -d
    echo.
    echo Sistema iniciado!
    echo App: https://localhost
    echo Admin: https://localhost/admin (admin/admin123)
)

pause