@echo off
echo ========================================
echo    PARANDO APLICACAO NOSSA GRANA
echo ========================================

echo.
echo Finalizando processos...

REM Finalizar processos do Django (backend)
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul

REM Finalizar processos do Node.js (frontend)
taskkill /f /im node.exe 2>nul
taskkill /f /im npm.cmd 2>nul

echo.
echo ========================================
echo    APLICACAO PARADA COM SUCESSO!
echo ========================================
echo.
echo Servicos finalizados:
echo - Backend Django (porta 8000)
echo - Demo Interface (porta 3002) 
echo - Frontend React (porta 3000)
echo.
pause