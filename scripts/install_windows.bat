@echo off
echo === Instalacao do Script de Traducao (Windows) ===
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.12+ de https://www.python.org/downloads/
    echo Certifique-se de marcar "Add Python to PATH" durante a instalacao
    pause
    exit /b 1
)

echo Python encontrado!
python --version

REM Verificar se Node.js esta instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Node.js nao encontrado!
    echo Por favor, instale Node.js 18+ de https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js encontrado!
node --version

REM Criar ambiente virtual
if not exist "venv" (
    echo.
    echo Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERRO: Falha ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo Ambiente virtual criado com sucesso!
) else (
    echo Ambiente virtual ja existe
)

echo.
echo Instalando dependencias Python...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip

if exist "requirements.txt" (
    echo Instalando dependencias do Google Translate...
    pip install -r requirements.txt
)

if exist "requirements_openai.txt" (
    echo Instalando dependencias da API (OpenAI/FastAPI)...
    pip install -r requirements_openai.txt
)

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

echo.
echo Instalando dependencias do frontend...
cd frontend
if not exist "node_modules" (
    call npm install
) else (
    echo Dependencias do frontend ja instaladas
)
cd ..

echo.
echo ========================================
echo Instalacao concluida com sucesso!
echo.
echo Scripts disponiveis:
echo   - Google Translate: scripts\run.bat en.json pt
echo   - OpenAI (CLI): scripts\run_openai.bat en.json pt
echo   - API REST: scripts\run_api.bat
echo   - Frontend: scripts\run_frontend.bat
echo.
echo Documentacao da API: http://localhost:8000/docs
echo ========================================
pause

