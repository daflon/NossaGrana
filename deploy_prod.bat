@echo off
REM Script de Deploy para Producao - NossaGrana (Windows)
setlocal enabledelayedexpansion

echo ========================================
echo  Deploy da Aplicacao NossaGrana
echo ========================================
echo.

REM Verificar se arquivo .env.prod existe
if not exist ".env.prod" (
    echo [ERRO] Arquivo .env.prod nao encontrado!
    echo Copie .env.prod.example e configure as variaveis de ambiente.
    pause
    exit /b 1
)

REM Verificar Docker
docker --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Docker nao encontrado! Instale o Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Docker Compose nao encontrado!
    pause
    exit /b 1
)

echo [INFO] Docker OK
echo.

REM Fazer backup antes do deploy
echo [1/6] Fazendo backup antes do deploy...
if exist "backups\" (
    call backup_prod.bat
) else (
    echo [AVISO] Pulando backup - diretorio nao existe
)

echo.
echo [2/6] Parando containers existentes...
docker-compose -f docker-compose.prod.yml down

echo.
echo [3/6] Construindo imagens Docker...
docker-compose -f docker-compose.prod.yml build --no-cache

echo.
echo [4/6] Iniciando servicos...
docker-compose -f docker-compose.prod.yml up -d

echo.
echo [5/6] Aguardando inicializacao...
timeout /t 15 /nobreak >nul

echo Executando migracoes...
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

echo Coletando arquivos estaticos...
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

echo Criando superusuario...
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@nossagrana.com', 'admin123')"

echo.
echo [6/6] Verificando status dos containers...
docker-compose -f docker-compose.prod.yml ps

echo.
echo ========================================
echo  Deploy Concluido!
echo ========================================
echo.
echo URLs disponiveis:
echo   App: https://localhost
echo   API: https://localhost/api/
echo   Admin: https://localhost/admin/
echo.
echo Credenciais Admin:
echo   Usuario: admin
echo   Senha: admin123
echo.
echo Comandos uteis:
echo   Ver logs: docker-compose -f docker-compose.prod.yml logs -f
echo   Parar: docker-compose -f docker-compose.prod.yml down
echo   Reiniciar: docker-compose -f docker-compose.prod.yml restart
echo   Monitor: monitor_prod.bat
echo.
pause