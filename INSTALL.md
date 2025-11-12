# Guia de Instalação

## Opção 1: Instalação Automática (Recomendado)

Execute o script de instalação automática:
```bash
./install.sh
```

Este script irá:
- Instalar pip3 e python3-venv (se necessário)
- Criar um ambiente virtual
- Instalar todas as dependências automaticamente

## Opção 2: Instalação Manual com Ambiente Virtual

### 1. Instalar python3-venv
```bash
sudo apt install python3-venv
```

### 2. Criar ambiente virtual
```bash
python3 -m venv venv
```

### 3. Ativar ambiente virtual
```bash
source venv/bin/activate
```

### 4. Instalar dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Opção 3: Instalação Manual sem Ambiente Virtual (Não Recomendado)

⚠️ **Atenção**: Sistemas modernos (Ubuntu 24.04+) podem bloquear instalações globais.

Se ainda assim quiser tentar:

```bash
# Instalar pip3
sudo apt install python3-pip

# Instalar com flag especial (pode quebrar o sistema)
pip3 install --break-system-packages -r requirements.txt
```

## Após a Instalação

### Usar o script helper (Mais fácil):
```bash
./run.sh en.json pt
```

### Ou ativar o ambiente virtual manualmente:
```bash
source venv/bin/activate
python src/script.py en.json pt
deactivate  # quando terminar
```

## Solução de Problemas

### Erro: "externally-managed-environment"
**Solução**: Use ambiente virtual (Opção 1 ou 2 acima)

### Erro: "pip3 not found"
**Solução**: 
```bash
sudo apt install python3-pip
```

### Erro: "venv module not found"
**Solução**:
```bash
sudo apt install python3-venv
```
