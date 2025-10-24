@echo off
echo Configurando ambiente de testes do Nossa Grana...

echo.
echo [1/4] Instalando dependencias do backend...
cd backend
pip install -r requirements.txt

echo.
echo [2/4] Instalando dependencias do frontend...
cd ..\frontend
npm install

echo.
echo [3/4] Instalando dependencias da demo...
cd ..\demo-interface
npm install

echo.
echo [4/4] Configurando banco de dados...
cd ..\backend
python manage.py migrate

cd ..
echo.
echo ✓ Configuracao concluida! Execute 'python run_all_tests.py' para rodar os testes.
pause