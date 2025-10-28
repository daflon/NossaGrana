@echo off
REM Script de Backup para Producao - NossaGrana (Windows)
setlocal enabledelayedexpansion

set BACKUP_DIR=backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo ========================================
echo  Backup da Aplicacao NossaGrana
echo ========================================
echo.
echo Data/Hora: %date% %time%
echo Diretorio: %BACKUP_DIR%
echo.

REM Criar diretório de backup se não existir
if not exist %BACKUP_DIR% (
    echo Criando diretorio de backup...
    mkdir %BACKUP_DIR%
)

REM Verificar se containers estão rodando
docker-compose -f docker-compose.prod.yml ps | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo [AVISO] Containers nao estao rodando
    echo Iniciando containers para backup...
    docker-compose -f docker-compose.prod.yml up -d db
    timeout /t 10 /nobreak >nul
)

echo [1/4] Fazendo backup do banco de dados...
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U nossa_grana_user nossa_grana_prod > %BACKUP_DIR%\db-backup-%TIMESTAMP%.sql
if %errorlevel% equ 0 (
    echo [OK] Backup do banco concluido
) else (
    echo [ERRO] Falha no backup do banco
)

echo.
echo [2/4] Fazendo backup dos arquivos estaticos...
if exist "backend\staticfiles" (
    powershell -command "Compress-Archive -Path 'backend\staticfiles' -DestinationPath '%BACKUP_DIR%\static-backup-%TIMESTAMP%.zip' -Force"
    echo [OK] Backup dos arquivos estaticos concluido
) else (
    echo [AVISO] Diretorio de arquivos estaticos nao encontrado
)

echo.
echo [3/4] Fazendo backup dos arquivos de media...
if exist "backend\media" (
    powershell -command "Compress-Archive -Path 'backend\media' -DestinationPath '%BACKUP_DIR%\media-backup-%TIMESTAMP%.zip' -Force"
    echo [OK] Backup dos arquivos de media concluido
) else (
    echo [AVISO] Diretorio de media nao encontrado
)

echo.
echo [4/4] Fazendo backup das configuracoes...
powershell -command "Compress-Archive -Path '.env.prod','docker-compose.prod.yml','nginx' -DestinationPath '%BACKUP_DIR%\config-backup-%TIMESTAMP%.zip' -Force"
echo [OK] Backup das configuracoes concluido

echo.
echo ========================================
echo  Backup Concluido!
echo ========================================
echo.
echo Arquivos criados:
dir /b %BACKUP_DIR%\*%TIMESTAMP%*

echo.
echo Limpando backups antigos (mantendo ultimos 5)...
for /f "skip=5 delims=" %%i in ('dir /b /o-d %BACKUP_DIR%\*.sql 2^>nul') do (
    del "%BACKUP_DIR%\%%i" 2>nul
    echo Removido: %%i
)

for /f "skip=5 delims=" %%i in ('dir /b /o-d %BACKUP_DIR%\*.zip 2^>nul') do (
    del "%BACKUP_DIR%\%%i" 2>nul
    echo Removido: %%i
)

echo.
echo [INFO] Backup concluido com sucesso!
echo [INFO] Arquivos salvos em: %BACKUP_DIR%\
echo.
pause