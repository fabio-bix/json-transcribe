@echo off

if not exist "venv" (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute primeiro: scripts\install_windows.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Iniciando API de traducao...
echo Documentacao disponivel em: http://localhost:8000/docs
echo API disponivel em: http://localhost:8000
echo.
echo Pressione Ctrl+C para parar
echo.

set PYTHONPATH=%PYTHONPATH%;%CD%\backend
python backend\api\api.py

pause

