# 🎨 Frontend - JSON Translator

Frontend React + Vite para o sistema de tradução de JSON.

## 🚀 Início Rápido

### Pré-requisitos

- Node.js 18+ e npm instalados
- API rodando em http://localhost:8000

### Instalação e Execução

```bash
# Instalar dependências e executar
./run_frontend.sh
```

Ou manualmente:

```bash
cd frontend
npm install
npm run dev
```

O frontend estará disponível em: **http://localhost:3000**

## 📋 Funcionalidades

### ✅ 1. Upload de JSON
- Drag & drop de arquivos
- Validação automática
- Feedback visual

### ✅ 2. Validação
- Exibe informações do arquivo
- Total de entradas
- Strings para traduzir

### ✅ 3. Configuração
- Seleção de método (OpenAI ou Google Translate)
- Seleção de modelo (quando OpenAI)
- Idioma de destino
- Parâmetros de batch

### ✅ 4. Estimativa
- Custo estimado em USD
- Tempo estimado
- Detalhes da estimativa

### ✅ 5. Progresso em Tempo Real
- Barra de progresso animada
- Estatísticas em tempo real:
  - Strings traduzidas
  - Batches processados
  - Tempo restante (ETA)
  - Custo atual
  - Tokens utilizados

### ✅ 6. Resultado
- Download do JSON traduzido
- Estatísticas finais
- Opção de nova tradução

## 🎨 Design

- **Tema escuro moderno** com gradientes
- **Animações suaves** e feedback visual
- **Responsivo** para mobile e desktop
- **Indicadores de progresso** visuais
- **Cores semânticas** (sucesso, erro, aviso)

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

### Proxy

O Vite está configurado para fazer proxy das requisições `/api` para `http://localhost:8000`.

## 📁 Estrutura

```
frontend/
├── src/
│   ├── components/          # Componentes React
│   │   ├── UploadStep.jsx   # Step 1: Upload
│   │   ├── ValidationStep.jsx # Step 2: Validação
│   │   ├── ConfigStep.jsx   # Step 3: Configuração
│   │   ├── EstimateStep.jsx # Step 4: Estimativa
│   │   ├── ProgressStep.jsx # Step 5: Progresso
│   │   └── ResultStep.jsx   # Step 6: Resultado
│   ├── services/
│   │   └── api.js           # Serviços de API
│   ├── App.jsx              # Componente principal
│   ├── App.css              # Estilos do App
│   ├── index.css            # Estilos globais
│   └── main.jsx             # Entry point
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 🛠️ Scripts Disponíveis

```bash
npm run dev      # Desenvolvimento (hot reload)
npm run build    # Build para produção
npm run preview  # Preview do build
```

## 🎯 Fluxo de Uso

1. **Upload**: Arraste ou selecione um arquivo JSON
2. **Validação**: Veja as informações do arquivo
3. **Configuração**: Escolha método, modelo e idioma
4. **Estimativa**: Revise custo e tempo estimados
5. **Tradução**: Acompanhe o progresso em tempo real
6. **Resultado**: Baixe o arquivo traduzido

## 🐛 Troubleshooting

### Erro de conexão com API

Certifique-se de que a API está rodando:
```bash
./run_api.sh
```

### Porta 3000 já em uso

Altere a porta no `vite.config.js`:
```js
server: {
  port: 3001,
}
```

### Erro de CORS

A API já está configurada para aceitar requisições de qualquer origem. Se ainda houver problemas, verifique o CORS no `backend/api/api.py`.

## 📝 Notas

- O frontend faz polling do status a cada 2 segundos durante a tradução
- Os jobs são armazenados em memória na API (perdidos ao reiniciar)
- Para produção, considere usar WebSockets para atualizações em tempo real

