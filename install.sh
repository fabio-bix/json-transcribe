#!/bin/bash

# Script de instalação automática

echo "=== Instalação do Script de Tradução ==="
echo ""

# Verifica se pip3 está instalado
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 já está instalado"
else
    echo "pip3 não encontrado. Tentando instalar..."
    
    # Tenta instalar pip3
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

# Verifica novamente se pip3 está disponível
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 instalado com sucesso"
else
    echo "ERRO: Não foi possível instalar pip3"
    exit 1
fi

# Verifica se python3-venv está instalado e funcional
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if ! python3 -m venv --help &>/dev/null 2>&1; then
    echo "python3-venv não está funcional. Tentando instalar..."
    if command -v sudo &> /dev/null; then
        # Tenta instalar o pacote específico da versão do Python primeiro
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

# Cria ambiente virtual se não existir
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

# Ativa o ambiente virtual e instala dependências
echo ""
echo "Instalando dependências no ambiente virtual..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Instalação concluída com sucesso!"
    echo ""
    echo "Para usar o script, ative o ambiente virtual primeiro:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Depois execute:"
    echo "  python src/script.py en.json pt"
    echo ""
    echo "Ou use o script helper:"
    echo "  ./run.sh en.json pt"
else
    echo ""
    echo "ERRO: Falha ao instalar dependências"
    exit 1
fi

