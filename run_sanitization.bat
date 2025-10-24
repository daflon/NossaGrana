@echo off
echo ========================================
echo  Nossa Grana - Sanitizacao para GitHub
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.9+ antes de continuar.
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Executando sanitizacao...
python sanitize_for_github.py

if errorlevel 1 (
    echo.
    echo ERRO: Sanitizacao falhou!
    echo Verifique os logs acima para detalhes.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Sanitizacao Concluida com Sucesso!
echo ========================================
echo.
echo Proximos passos:
echo 1. Revisar arquivos .env.example criados
echo 2. Testar aplicacao apos sanitizacao
echo 3. Verificar se .gitignore esta correto
echo 4. Fazer upload para GitHub
echo.
echo Backup salvo em: backup_pre_sanitization/
echo.
pause