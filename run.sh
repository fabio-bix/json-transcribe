#!/bin/bash

# Script helper para executar o script de tradução com o ambiente virtual

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "ERRO: Ambiente virtual não encontrado!"
    echo "Execute primeiro: ./install.sh"
    exit 1
fi

# Ativa o ambiente virtual e executa o script
source venv/bin/activate
python src/script.py "$@"

