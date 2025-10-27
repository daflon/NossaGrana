@echo off
echo ========================================
echo    REINICIANDO APLICACAO NOSSA GRANA
echo ========================================

echo.
echo [1/5] Finalizando processos existentes...

REM Finalizar processos do Django (backend)
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul

REM Finalizar processos do Node.js (frontend)
taskkill /f /im node.exe 2>nul
taskkill /f /im npm.cmd 2>nul

REM Finalizar processos do CMD que podem estar rodando os servidores
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq Administrator: C:\WINDOWS\system32\cmd.exe - python*" /fo table /nh 2^>nul') do taskkill /f /pid %%i 2>nul
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq Administrator: C:\WINDOWS\system32\cmd.exe - npm*" /fo table /nh 2^>nul') do taskkill /f /pid %%i 2>nul

echo Processos finalizados.

echo.
echo [2/5] Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo [3/5] Iniciando Backend (Django)...
cd /d "%~dp0backend"
start "Backend - Django" cmd /k "python manage.py runserver 8000"

echo.
echo [4/5] Iniciando Demo Interface...
cd /d "%~dp0demo"
start "Demo Interface" cmd /k "npm start -- --port 3002"

echo.
echo [5/5] Iniciando Frontend (React)...
cd /d "%~dp0frontend"
start "Frontend - React" cmd /k "npm start"

echo.
echo ========================================
echo    APLICACAO REINICIADA COM SUCESSO!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Demo Interface: http://localhost:3002
echo Frontend: http://localhost:3000
echo.
echo Pressione qualquer tecla para fechar...
pause >nul