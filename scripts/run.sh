#!/bin/bash

if [ ! -d "venv" ]; then
    echo "ERRO: Ambiente virtual não encontrado!"
    echo "Execute primeiro: ./install.sh"
    exit 1
fi

source venv/bin/activate
python backend/scripts/script.py "$@"

