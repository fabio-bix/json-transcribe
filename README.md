# JSON Translator

Sistema completo para tradução de arquivos JSON usando OpenAI ou Google Translate.

## 📁 Estrutura do Projeto

```
translate_script/
├── backend/                 # Backend Python
│   ├── api/                 # API REST (FastAPI)
│   │   └── api.py
│   ├── core/                # Lógica core de tradução
│   │   └── translator_service.py
│   └── scripts/             # Scripts CLI
│       ├── script.py        # Google Translate
│       └── script_openai.py # OpenAI
├── frontend/                # Frontend React + Vite
│   └── src/
│       ├── components/      # Componentes React
│       ├── services/        # Serviços API
│       ├── styles/          # Estilos CSS
│       ├── utils/           # Utilitários
│       └── constants/       # Constantes
├── scripts/                 # Scripts shell
│   ├── run_api.sh
│   ├── run_frontend.sh
│   ├── run_openai.sh
│   └── run.sh
├── docs/                    # Documentação
│   ├── README.md
│   ├── README_API.md
│   ├── README_FRONTEND.md
│   ├── README_OPENAI.md
│   ├── INSTALL.md
│   └── QUICK_START.md
├── output/                  # Arquivos traduzidos
├── venv/                    # Ambiente virtual Python
└── requirements*.txt        # Dependências Python
```

## 🚀 Início Rápido

### Instalação

```bash
./install.sh
```

### Executar API

```bash
./scripts/run_api.sh
```

### Executar Frontend

```bash
./scripts/run_frontend.sh
```

### Executar Scripts CLI

```bash
# OpenAI
./scripts/run_openai.sh en.json pt

# Google Translate
./scripts/run.sh en.json pt
```

## 📚 Documentação

Consulte a pasta `docs/` para documentação detalhada:
- `docs/QUICK_START.md` - Guia rápido
- `docs/INSTALL.md` - Instalação detalhada
- `docs/README_API.md` - Documentação da API
- `docs/README_FRONTEND.md` - Documentação do Frontend
- `docs/README_OPENAI.md` - Documentação do script OpenAI

## 🌍 Idiomas Suportados

Espanhol, Português, Francês, Alemão, Italiano, Holandês, Polonês, Sueco, Dinamarquês, Norueguês, Finlandês, Tcheco, Húngaro, Romeno, Croata, Sérvio (Latinizado), Turco, Indonésio, Filipino (Tagalog), Malaio

## 📝 Licença

Este projeto é de uso interno.

