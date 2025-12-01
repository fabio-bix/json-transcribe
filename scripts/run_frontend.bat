@echo off

cd frontend

if not exist "node_modules" (
    echo Instalando dependencias...
    call npm install
)

echo Iniciando front-end...
echo Disponivel em: http://localhost:3000
echo.
echo Pressione Ctrl+C para parar
echo.

call npm run dev

pause

