#!/bin/bash

echo "=== Instalação do Script de Tradução ==="
echo ""

if command -v pip3 &> /dev/null; then
    echo "✓ pip3 já está instalado"
else
    echo "pip3 não encontrado. Tentando instalar..."
    
    if command -v sudo &> /dev/null; then
        echo "Instalando pip3 com sudo..."
        sudo apt update
        sudo apt install -y python3-pip
    else
        echo "ERRO: sudo não está disponível."
        echo "Por favor, instale pip3 manualmente:"
        echo "  sudo apt install python3-pip"
        exit 1
    fi
fi

if command -v pip3 &> /dev/null; then
    echo "✓ pip3 instalado com sucesso"
else
    echo "ERRO: Não foi possível instalar pip3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if ! python3 -m venv --help &>/dev/null 2>&1; then
    echo "python3-venv não está funcional. Tentando instalar..."
    if command -v sudo &> /dev/null; then
        echo "Instalando python${PYTHON_VERSION}-venv..."
        sudo apt install -y python${PYTHON_VERSION}-venv 2>/dev/null || \
        sudo apt install -y python3-venv 2>/dev/null || {
            echo "ERRO: Não foi possível instalar python3-venv automaticamente."
            echo "Por favor, instale manualmente:"
            echo "  sudo apt install python${PYTHON_VERSION}-venv"
            exit 1
        }
    else
        echo "ERRO: sudo não está disponível."
        echo "Por favor, instale python3-venv manualmente:"
        echo "  sudo apt install python${PYTHON_VERSION}-venv"
        exit 1
    fi
fi

if [ ! -d "venv" ]; then
    echo ""
    echo "Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao criar ambiente virtual"
        exit 1
    fi
    echo "✓ Ambiente virtual criado"
else
    echo "✓ Ambiente virtual já existe"
fi

echo ""
echo "Instalando dependências no ambiente virtual..."
source venv/bin/activate
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "Instalando dependências do Google Translate..."
    pip install -r requirements.txt
fi

if [ -f "requirements_openai.txt" ]; then
    echo "Instalando dependências da API (OpenAI/FastAPI)..."
    pip install -r requirements_openai.txt
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Instalação concluída com sucesso!"
    echo ""
    echo "Scripts disponíveis:"
    echo "  • Google Translate: ./scripts/run.sh en.json pt"
    echo "  • OpenAI (CLI): ./scripts/run_openai.sh en.json pt"
    echo "  • API REST: ./scripts/run_api.sh"
    echo ""
    echo "Documentação da API: http://localhost:8000/docs"
else
    echo ""
    echo "ERRO: Falha ao instalar dependências"
    exit 1
fi

