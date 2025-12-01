@echo off

if not exist "venv" (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute primeiro: scripts\install_windows.bat
    pause
    exit /b 1
)

if not exist ".env" (
    echo Arquivo .env nao encontrado!
    echo Criando arquivo .env de exemplo...
    echo OPENAI_API_KEY=sk-your-api-key-here > .env
    echo.
    echo Por favor, edite o arquivo .env e adicione sua chave OpenAI:
    echo   notepad .env
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python backend\scripts\script_openai.py %*

pause

