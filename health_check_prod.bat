@echo off
REM Health Check Automatizado para Producao - NossaGrana (Windows)
setlocal enabledelayedexpansion

set LOG_FILE=logs\health_check.log
set ERROR_COUNT=0

REM Criar diretório de logs se não existir
if not exist "logs" mkdir logs

echo ========================================
echo  Health Check - NossaGrana
echo ========================================
echo Data/Hora: %date% %time%
echo.

REM Log da execução
echo [%date% %time%] Iniciando health check >> %LOG_FILE%

REM 1. Verificar containers
echo [1/5] Verificando containers...
for %%c in (nginx backend frontend db redis celery) do (
    docker-compose -f docker-compose.prod.yml ps %%c | findstr "Up" >nul
    if !errorlevel! equ 0 (
        echo [OK] Container %%c: Rodando
        echo [%date% %time%] [OK] Container %%c: Rodando >> %LOG_FILE%
    ) else (
        echo [ERRO] Container %%c: Parado ou com problema
        echo [%date% %time%] [ERRO] Container %%c: Parado >> %LOG_FILE%
        set /a ERROR_COUNT+=1
    )
)

echo.
echo [2/5] Verificando conectividade HTTP...
curl -s -o nul -w "%%{http_code}" --max-time 10 http://localhost 2>nul | findstr "200 301 302" >nul
if %errorlevel% equ 0 (
    echo [OK] HTTP: Respondendo
    echo [%date% %time%] [OK] HTTP: Respondendo >> %LOG_FILE%
) else (
    echo [ERRO] HTTP: Nao responde
    echo [%date% %time%] [ERRO] HTTP: Nao responde >> %LOG_FILE%
    set /a ERROR_COUNT+=1
)

echo.
echo [3/5] Verificando conectividade HTTPS...
curl -k -s -o nul -w "%%{http_code}" --max-time 10 https://localhost 2>nul | findstr "200 301 302" >nul
if %errorlevel% equ 0 (
    echo [OK] HTTPS: Respondendo
    echo [%date% %time%] [OK] HTTPS: Respondendo >> %LOG_FILE%
) else (
    echo [AVISO] HTTPS: Nao responde
    echo [%date% %time%] [AVISO] HTTPS: Nao responde >> %LOG_FILE%
)

echo.
echo [4/5] Verificando API Health...
curl -s -o nul -w "%%{http_code}" --max-time 10 http://localhost/api/health/ 2>nul | findstr "200" >nul
if %errorlevel% equ 0 (
    echo [OK] API Health: OK
    echo [%date% %time%] [OK] API Health: OK >> %LOG_FILE%
) else (
    echo [ERRO] API Health: Falha
    echo [%date% %time%] [ERRO] API Health: Falha >> %LOG_FILE%
    set /a ERROR_COUNT+=1
)

echo.
echo [5/5] Verificando banco de dados...
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py check --database default >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Banco de dados: Conectado
    echo [%date% %time%] [OK] Banco de dados: Conectado >> %LOG_FILE%
) else (
    echo [ERRO] Banco de dados: Problema de conexao
    echo [%date% %time%] [ERRO] Banco de dados: Problema >> %LOG_FILE%
    set /a ERROR_COUNT+=1
)

echo.
echo ========================================
echo  Resultado do Health Check
echo ========================================

if %ERROR_COUNT% equ 0 (
    echo [SUCESSO] Sistema funcionando perfeitamente!
    echo [%date% %time%] [SUCESSO] Health check OK - 0 erros >> %LOG_FILE%
    echo.
    echo Status: SISTEMA SAUDAVEL
) else (
    echo [ALERTA] Encontrados %ERROR_COUNT% problemas!
    echo [%date% %time%] [ALERTA] Health check FALHA - %ERROR_COUNT% erros >> %LOG_FILE%
    echo.
    echo Status: SISTEMA COM PROBLEMAS
    echo.
    echo Acoes recomendadas:
    echo   1. Verificar logs: docker-compose -f docker-compose.prod.yml logs
    echo   2. Reiniciar servicos: docker-compose -f docker-compose.prod.yml restart
    echo   3. Monitor completo: monitor_prod.bat
)

echo.
echo Log salvo em: %LOG_FILE%
echo.

REM Se executado automaticamente, não pausar
if "%1"=="auto" (
    exit /b %ERROR_COUNT%
) else (
    pause
)