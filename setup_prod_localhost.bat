@echo off
REM Setup completo para produção em localhost - NossaGrana
setlocal enabledelayedexpansion

echo ========================================
echo  Setup Producao Localhost - NossaGrana
echo ========================================
echo.

REM 1. Gerar certificados SSL
echo [1/4] Gerando certificados SSL...
call generate-ssl.bat
if %errorlevel% neq 0 (
    echo Erro ao gerar certificados SSL
    pause
    exit /b 1
)

REM 2. Verificar Docker
echo.
echo [2/4] Verificando Docker...
docker --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker nao encontrado! Instale o Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker Compose nao encontrado!
    pause
    exit /b 1
)

echo Docker OK

REM 3. Parar containers existentes
echo.
echo [3/4] Parando containers existentes...
docker-compose -f docker-compose.prod.yml down 2>nul

REM 4. Iniciar sistema de produção
echo.
echo [4/4] Iniciando sistema de producao...
docker-compose -f docker-compose.prod.yml up -d --build

REM Aguardar inicialização
echo.
echo Aguardando inicializacao dos servicos...
timeout /t 15 /nobreak >nul

REM Executar migrações
echo.
echo Executando migracoes...
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

REM Coletar arquivos estáticos
echo.
echo Coletando arquivos estaticos...
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

REM Criar superusuário
echo.
echo Criando superusuario...
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@localhost', 'admin123')"

REM Verificar status
echo.
echo ========================================
echo  Status dos Containers
echo ========================================
docker-compose -f docker-compose.prod.yml ps

echo.
echo ========================================
echo  SISTEMA PRONTO!
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
echo IMPORTANTE:
echo   - Aceite o certificado auto-assinado no navegador
echo   - Para parar: docker-compose -f docker-compose.prod.yml down
echo   - Para logs: docker-compose -f docker-compose.prod.yml logs -f
echo.
pause