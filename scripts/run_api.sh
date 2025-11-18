#!/bin/bash

if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Execute primeiro: ./install.sh"
    exit 1
fi

source venv/bin/activate

echo "🚀 Iniciando API de tradução..."
echo "📖 Documentação disponível em: http://localhost:8000/docs"
echo "🔗 API disponível em: http://localhost:8000"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/backend"
python backend/api/api.py

