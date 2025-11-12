#!/bin/bash

# Script helper para executar o script de tradução OpenAI com o ambiente virtual

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "ERRO: Ambiente virtual não encontrado!"
    echo "Execute primeiro: ./install.sh"
    exit 1
fi

# Verifica se .env existe
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

# Ativa o ambiente virtual e executa o script
source venv/bin/activate
python src/script_openai.py "$@"
