# 🌍 JSON Translator

Sistema completo para tradução de arquivos JSON usando OpenAI ou Google Translate, com interface web moderna.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Instalação](#instalação)
- [Uso](#uso)
  - [Interface Web (Recomendado)](#interface-web-recomendado)
  - [CLI (Linha de Comando)](#cli-linha-de-comando)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Documentação](#documentação)

## 🎯 Visão Geral

Este projeto oferece três formas de traduzir arquivos JSON:

1. **🌐 Interface Web** - Frontend React + Vite com experiência visual completa
2. **🔌 API REST** - Endpoints REST para integração e automação
3. **💻 CLI** - Scripts de linha de comando para uso direto

### Funcionalidades

- ✅ Tradução usando OpenAI (IA) ou Google Translate
- ✅ Preservação de placeholders (`{{name}}`, `{count}`, `%s`, etc.)
- ✅ Cache local para evitar retraduções
- ✅ Processamento em batch otimizado
- ✅ Tradução paralela para maior velocidade
- ✅ Estimativa de custo e tempo
- ✅ Progresso em tempo real
- ✅ Interface web moderna e responsiva

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+ (para backend/API)
- Node.js 18+ e npm (para frontend)
- Chave da API OpenAI (para tradução via IA)

### Instalação Completa

```bash
# 1. Instalar dependências do backend
./install.sh

# 2. Configurar API key da OpenAI
# Crie um arquivo .env na raiz do projeto:
echo "OPENAI_API_KEY=sua_chave_aqui" > .env

# 3. Instalar dependências do frontend
cd frontend
npm install
cd ..
```

## 📖 Uso

### Interface Web (Recomendado)

A forma mais fácil e visual de usar o sistema:

#### 1. Iniciar a API (Backend)

Em um terminal:

```bash
./run_api.sh
```

A API estará disponível em: http://localhost:8000

#### 2. Iniciar o Frontend

Em outro terminal:

```bash
./run_frontend.sh
```

O frontend estará disponível em: http://localhost:3000

#### 3. Usar a Interface

1. Acesse http://localhost:3000 no navegador
2. Faça upload do arquivo JSON (drag & drop ou clique)
3. Revise as informações de validação
4. Configure:
   - Método: OpenAI ou Google Translate
   - Modelo (se OpenAI)
   - Idioma de destino
   - Parâmetros de batch
5. Veja a estimativa de custo e tempo
6. Inicie a tradução
7. Acompanhe o progresso em tempo real
8. Baixe o resultado traduzido

### CLI (Linha de Comando)

Para uso direto via terminal:

#### Tradução com OpenAI

```bash
# Tradução básica
./run_openai.sh en.json pt

# Com opções avançadas
./run_openai.sh en.json pt --batch 100 --parallel 3 --model gpt-4o-mini

# Modo dry-run (apenas estimativa)
./run_openai.sh en.json pt --dry
```

#### Tradução com Google Translate

```bash
# Tradução básica
./run.sh en.json pt

# Especificar arquivo de saída
./run.sh en.json pt pt.json
```

### API REST

Para integração e automação:

```bash
# Iniciar API
./run_api.sh

# Documentação interativa
# Acesse: http://localhost:8000/docs
```

Veja [README_API.md](README_API.md) para documentação completa da API.

## 📁 Estrutura do Projeto

```
translate_script/
├── frontend/              # Frontend React + Vite
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── services/     # Serviços de API
│   │   └── App.jsx        # App principal
│   ├── package.json
│   └── vite.config.js
│
├── backend/               # Backend (API e Scripts CLI)
│   ├── api.py            # API REST (FastAPI)
│   ├── translator_service.py  # Serviço de tradução
│   ├── script_openai.py  # Script CLI OpenAI
│   └── script.py         # Script CLI Google Translate
│
├── output/               # Arquivos traduzidos (gerados)
├── venv/                 # Ambiente virtual Python
│
├── .env                  # Variáveis de ambiente (criar)
├── .gitignore
│
├── install.sh            # Instalação automática
├── run_api.sh           # Executar API
├── run_frontend.sh      # Executar frontend
├── run_openai.sh        # Executar CLI OpenAI
├── run.sh               # Executar CLI Google Translate
│
├── requirements.txt     # Dependências Google Translate
├── requirements_openai.txt  # Dependências OpenAI/API
│
└── README.md           # Este arquivo
```

## 📚 Documentação

- **[README_API.md](README_API.md)** - Documentação completa da API REST
- **[README_OPENAI.md](README_OPENAI.md)** - Guia do script OpenAI CLI
- **[README_FRONTEND.md](README_FRONTEND.md)** - Documentação do frontend
- **[QUICK_START.md](QUICK_START.md)** - Guia rápido de início
- **[INSTALL.md](INSTALL.md)** - Guia detalhado de instalação

## 🎨 Interface Web - Funcionalidades

### 1. Upload
- Drag & drop de arquivos
- Validação automática
- Feedback visual

### 2. Validação
- Informações do arquivo
- Total de entradas
- Strings para traduzir

### 3. Configuração
- Seleção de método (OpenAI/Google)
- Seleção de modelo
- Idioma de destino
- Parâmetros de batch

### 4. Estimativa
- Custo em USD
- Tempo estimado
- Detalhes completos

### 5. Progresso
- Barra de progresso animada
- Estatísticas em tempo real:
  - Strings traduzidas
  - Batches processados
  - ETA (tempo restante)
  - Custo atual
  - Tokens utilizados

### 6. Resultado
- Download do JSON traduzido
- Estatísticas finais
- Opção de nova tradução

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
OPENAI_API_KEY=sk-sua_chave_aqui
```

### Portas

- **API**: http://localhost:8000
- **Frontend**: http://localhost:3000

Para alterar, edite:
- API: `backend/api/api.py` (linha final)
- Frontend: `frontend/vite.config.js`

## 🚦 Início Rápido

```bash
# 1. Instalar tudo
./install.sh
cd frontend && npm install && cd ..

# 2. Configurar API key
echo "OPENAI_API_KEY=sua_chave" > .env

# 3. Rodar API (terminal 1)
./run_api.sh

# 4. Rodar Frontend (terminal 2)
./run_frontend.sh

# 5. Acessar interface
# http://localhost:3000
```

## 🐛 Troubleshooting

### API não inicia

- Verifique se a porta 8000 está livre: `lsof -i :8000`
- Verifique se o `.env` existe e tem a `OPENAI_API_KEY`

### Frontend não conecta à API

- Certifique-se de que a API está rodando
- Verifique o proxy no `vite.config.js`

### Erro de módulos Python

- Execute `./install.sh` novamente
- Ative o venv: `source venv/bin/activate`

### Erro de módulos Node

- Execute `cd frontend && npm install`

## 📝 Notas

- Os jobs de tradução são armazenados em memória (perdidos ao reiniciar a API)
- O cache de traduções é persistente (arquivos `.translate_cache_*.json`)
- Para produção, considere usar banco de dados para jobs e WebSockets para atualizações em tempo real

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto é de código aberto e está disponível para uso livre.
