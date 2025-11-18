#!/bin/bash

cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
fi

echo "🚀 Iniciando front-end..."
echo "🌐 Disponível em: http://localhost:3000"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

npm run dev
