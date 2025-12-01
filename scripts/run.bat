@echo off

if not exist "venv" (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute primeiro: scripts\install_windows.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python backend\scripts\script.py %*

pause

