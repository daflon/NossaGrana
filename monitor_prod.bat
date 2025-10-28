@echo off
REM Script de Monitoramento para Producao - NossaGrana (Windows)
setlocal enabledelayedexpansion

echo ========================================
echo  Monitor da Aplicacao NossaGrana
echo ========================================
echo.

REM Verificar se Docker está rodando
docker --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Docker nao encontrado ou nao esta rodando
    pause
    exit /b 1
)

echo [INFO] Status dos Containers:
echo ----------------------------------------
docker-compose -f docker-compose.prod.yml ps

echo.
echo [INFO] Uso de Recursos:
echo ----------------------------------------
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>nul

echo.
echo [INFO] Volumes:
echo ----------------------------------------
docker volume ls | findstr nossa_grana

echo.
echo [INFO] Testes de Conectividade:
echo ----------------------------------------

REM Teste HTTP
curl -s -o nul -w "%%{http_code}" http://localhost 2>nul | findstr "200 301 302" >nul
if %errorlevel% equ 0 (
    echo [OK] HTTP (porta 80): OK
) else (
    echo [ERRO] HTTP (porta 80): Falha
)

REM Teste HTTPS
curl -k -s -o nul -w "%%{http_code}" https://localhost 2>nul | findstr "200 301 302" >nul
if %errorlevel% equ 0 (
    echo [OK] HTTPS (porta 443): OK
) else (
    echo [AVISO] HTTPS (porta 443): Nao configurado ou falha
)

REM Teste API
curl -s -o nul -w "%%{http_code}" http://localhost/api/health/ 2>nul | findstr "200" >nul
if %errorlevel% equ 0 (
    echo [OK] API Health Check: OK
) else (
    echo [ERRO] API Health Check: Falha
)

echo.
echo [INFO] Logs de Erro Recentes:
echo ----------------------------------------
docker-compose -f docker-compose.prod.yml logs --tail=5 2>nul | findstr /i error

echo.
echo [INFO] Espaco em Disco:
echo ----------------------------------------
for /f "tokens=3,4" %%a in ('dir /-c ^| find "bytes free"') do (
    echo Espaco livre: %%a %%b
)

echo.
echo [INFO] Backup mais recente:
echo ----------------------------------------
if exist "backups\" (
    for /f %%i in ('dir /b /o-d backups\*.tar.gz 2^>nul') do (
        echo Ultimo backup: %%i
        goto :backup_found
    )
    echo Nenhum backup encontrado
    :backup_found
) else (
    echo Diretorio de backup nao existe
)

echo.
echo ========================================
echo  Comandos Uteis:
echo ========================================
echo   Ver logs completos: docker-compose -f docker-compose.prod.yml logs -f
echo   Reiniciar servico: docker-compose -f docker-compose.prod.yml restart [servico]
echo   Backup manual: backup_prod.bat
echo   Deploy: deploy_prod.bat
echo   Parar sistema: docker-compose -f docker-compose.prod.yml down
echo.
pause