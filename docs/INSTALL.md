# Guia de Instalação Completo

Guia detalhado para instalar e configurar o JSON Translator.

## 📋 Pré-requisitos

- **Python 3.12+**
- **Node.js 18+** e **npm**
- **Chave API da OpenAI** (opcional, apenas para método OpenAI)
- **Sistema operacional**: Linux, macOS ou WSL (Windows)

## 🚀 Instalação Automática (Recomendado)

### Passo 1: Instalar Python venv

```bash
sudo apt install python3.12-venv
```

### Passo 2: Executar script de instalação

```bash
./install.sh
```

Este script irá automaticamente:
- ✅ Criar ambiente virtual Python
- ✅ Instalar dependências Python
- ✅ Instalar dependências do frontend (Node.js)
- ✅ Configurar o projeto

## 🔧 Instalação Manual

### Backend (Python)

#### 1. Criar ambiente virtual

```bash
python3.12 -m venv venv
```

#### 2. Ativar ambiente virtual

```bash
source venv/bin/activate
```

#### 3. Instalar dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Se usar OpenAI:
```bash
pip install -r requirements_openai.txt
```

#### 4. Configurar variáveis de ambiente

Crie arquivo `.env` na raiz do projeto:

```bash
OPENAI_API_KEY=sk-sua-chave-aqui
```

**Nota**: A chave é necessária apenas para usar o método OpenAI. Google Translate não requer chave.

### Frontend (Node.js)

#### 1. Navegar para pasta frontend

```bash
cd frontend
```

#### 2. Instalar dependências

```bash
npm install
```

#### 3. Voltar para raiz

```bash
cd ..
```

## ✅ Verificar Instalação

### Verificar Backend

```bash
source venv/bin/activate
python -c "import fastapi; print('FastAPI OK')"
python -c "import openai; print('OpenAI OK')"
python -c "from deep_translator import GoogleTranslator; print('Google Translate OK')"
```

### Verificar Frontend

```bash
cd frontend
npm list react
cd ..
```

## 🏃 Rodar o Sistema

### Opção 1: Scripts Helper (Recomendado)

**Backend:**
```bash
./scripts/run_api.sh
```

**Frontend:**
```bash
./scripts/run_frontend.sh
```

### Opção 2: Manual

**Backend:**
```bash
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/backend"
python backend/api/api.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## 📁 Estrutura Após Instalação

```
translate_script/
├── venv/                    # Ambiente virtual Python
│   ├── bin/
│   └── lib/
├── frontend/
│   ├── node_modules/        # Dependências Node.js
│   └── package-lock.json
├── .env                     # Variáveis de ambiente (você cria)
└── output/                  # Arquivos traduzidos (criado automaticamente)
```

## 🔐 Configuração de Segurança

### Arquivo .env

⚠️ **IMPORTANTE**: Nunca commite o arquivo `.env` no Git!

Crie um arquivo `.gitignore` se não existir:
```
.env
venv/
__pycache__/
*.pyc
node_modules/
```

### Chave OpenAI

1. Obtenha sua chave em: https://platform.openai.com/api-keys
2. Crie arquivo `.env` na raiz:
   ```
   OPENAI_API_KEY=sk-sua-chave-aqui
   ```
3. Mantenha a chave segura e privada

## 🐛 Solução de Problemas

### Erro: "externally-managed-environment"

**Causa**: Python moderno bloqueia instalações globais.

**Solução**: Use ambiente virtual:
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "python3.12-venv not found"

**Solução**: Instale o pacote:
```bash
sudo apt update
sudo apt install python3.12-venv
```

### Erro: "OPENAI_API_KEY não encontrada"

**Solução**: 
1. Crie arquivo `.env` na raiz
2. Adicione: `OPENAI_API_KEY=sk-sua-chave`
3. Ou use apenas Google Translate (não requer chave)

### Erro: "npm not found"

**Solução**: Instale Node.js:
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Ou use nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

### Erro: "Module not found" no Python

**Solução**: 
1. Ative o ambiente virtual: `source venv/bin/activate`
2. Reinstale dependências: `pip install -r requirements.txt`

### Erro: "Port 8000 already in use"

**Solução**: 
1. Encontre o processo: `lsof -i :8000`
2. Mate o processo: `kill -9 <PID>`
3. Ou mude a porta no `api.py`

### Erro: "Port 3000 already in use"

**Solução**: 
1. Encontre o processo: `lsof -i :3000`
2. Mate o processo: `kill -9 <PID>`
3. Ou mude a porta no `vite.config.js`

## 🔄 Atualização

### Atualizar Dependências Python

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Atualizar Dependências Frontend

```bash
cd frontend
npm update
cd ..
```

## 📝 Próximos Passos

Após instalação bem-sucedida:

1. ✅ Configure `.env` com sua chave OpenAI (opcional)
2. ✅ Inicie o backend: `./scripts/run_api.sh`
3. ✅ Inicie o frontend: `./scripts/run_frontend.sh`
4. ✅ Acesse: http://localhost:3000
5. ✅ Leia: [QUICK_START.md](QUICK_START.md)

## 🆘 Ainda com Problemas?

1. Verifique os logs do backend
2. Verifique os logs do frontend (console do navegador)
3. Consulte a documentação da API: http://localhost:8000/docs
4. Verifique se todas as portas estão livres
5. Verifique permissões de escrita na pasta `output/`

---

**Instalação concluída?** Veja [QUICK_START.md](QUICK_START.md) para começar a usar!
