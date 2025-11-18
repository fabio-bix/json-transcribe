#!/bin/bash

if [ ! -d "venv" ]; then
    echo "ERRO: Ambiente virtual não encontrado!"
    echo "Execute primeiro: ./install.sh"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "Criando arquivo .env de exemplo..."
    echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
    echo ""
    echo "Por favor, edite o arquivo .env e adicione sua chave OpenAI:"
    echo "  nano .env"
    echo ""
    echo "Ou execute:"
    echo "  echo 'OPENAI_API_KEY=sk-sua-chave' > .env"
    exit 1
fi

source venv/bin/activate
python backend/scripts/script_openai.py "$@"
