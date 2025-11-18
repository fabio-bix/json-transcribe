# JSON Translator - Frontend

Frontend React + Vite para o sistema de tradução de JSON.

## 🚀 Instalação

```bash
cd frontend
npm install
```

## 🏃 Executar

```bash
npm run dev
```

O frontend estará disponível em: http://localhost:3000

## 📦 Build para Produção

```bash
npm run build
```

Os arquivos serão gerados na pasta `dist/`.

## 🔧 Configuração

A API está configurada para usar `http://localhost:8000` por padrão. Para alterar, crie um arquivo `.env`:

```env
VITE_API_URL=http://localhost:8000
```

## 🎨 Funcionalidades

- ✅ Upload de arquivo JSON com drag & drop
- ✅ Validação do arquivo
- ✅ Seleção de método (OpenAI ou Google Translate)
- ✅ Seleção de modelo (quando OpenAI)
- ✅ Estimativa de custo e tempo
- ✅ Progresso em tempo real com estatísticas
- ✅ Download do resultado traduzido

## 📁 Estrutura

```
frontend/
├── src/
│   ├── components/      # Componentes React
│   │   ├── UploadStep.jsx
│   │   ├── ValidationStep.jsx
│   │   ├── ConfigStep.jsx
│   │   ├── EstimateStep.jsx
│   │   ├── ProgressStep.jsx
│   │   └── ResultStep.jsx
│   ├── services/       # Serviços de API
│   │   └── api.js
│   ├── App.jsx         # Componente principal
│   ├── App.css         # Estilos do App
│   ├── index.css       # Estilos globais
│   └── main.jsx        # Entry point
├── index.html
├── package.json
└── vite.config.js
```

