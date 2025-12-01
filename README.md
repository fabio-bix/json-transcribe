# JSON Translator

Sistema completo para tradução de arquivos JSON mantendo a estrutura e chaves originais, traduzindo apenas os valores de texto do inglês para outros idiomas.

## 🎯 Finalidade

O **JSON Translator** foi desenvolvido para traduzir arquivos JSON que contêm textos em inglês para outros idiomas, **preservando todas as chaves** e estrutura do arquivo original. Apenas os **valores de texto** são traduzidos, mantendo a integridade estrutural do JSON.

### Casos de Uso

- Tradução de arquivos de localização (i18n)
- Tradução de configurações JSON com textos
- Migração de conteúdo para múltiplos idiomas
- Preparação de arquivos para aplicações multilíngue

## 📋 Características

- ✅ **Preserva chaves**: Todas as chaves do JSON permanecem inalteradas
- ✅ **Traduz apenas valores**: Apenas strings de texto são traduzidas
- ✅ **Dois métodos de tradução**: OpenAI (IA) ou Google Translate (gratuito)
- ✅ **Interface web moderna**: Frontend React com UI intuitiva
- ✅ **API REST completa**: Backend FastAPI para integração
- ✅ **Cache inteligente**: Evita retraduzir strings já traduzidas
- ✅ **Processamento em lote**: Traduz múltiplas strings simultaneamente
- ✅ **Estimativa de custo e tempo**: Antes de iniciar a tradução
- ✅ **Progresso em tempo real**: Acompanhe o progresso da tradução
- ✅ **Múltiplos idiomas**: Suporta 20+ idiomas

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
│   ├── run_api.sh          # Inicia API
│   ├── run_frontend.sh      # Inicia Frontend
│   ├── run_openai.sh        # Script CLI OpenAI
│   └── run.sh               # Script CLI Google Translate
├── docs/                    # Documentação detalhada
├── output/                  # Arquivos traduzidos salvos aqui
├── venv/                    # Ambiente virtual Python
└── requirements*.txt        # Dependências Python
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.12+
- Node.js 18+ e npm
- Chave API da OpenAI (para método OpenAI)

---

## 🪟 Instalação no Windows

### Passo 1: Instalar Python

1. Baixe Python 3.12+ de [python.org/downloads](https://www.python.org/downloads/)
2. Durante a instalação, **marque a opção "Add Python to PATH"**
3. Verifique a instalação abrindo o **Prompt de Comando** ou **PowerShell** e execute:
   ```cmd
   python --version
   ```

### Passo 2: Instalar Node.js

1. Baixe Node.js 18+ de [nodejs.org](https://nodejs.org/)
2. Execute o instalador e siga as instruções
3. Verifique a instalação:
   ```cmd
   node --version
   npm --version
   ```

### Passo 3: Executar script de instalação

Abra o **Prompt de Comando** ou **PowerShell** na pasta do projeto e execute:

```cmd
scripts\install_windows.bat
```

Este script irá:
- Verificar se Python e Node.js estão instalados
- Criar ambiente virtual Python
- Instalar dependências Python
- Instalar dependências do frontend
- Configurar o projeto

### Passo 4: Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (ou edite se já existir):

**Opção 1: Usando Notepad**
```cmd
notepad .env
```

**Opção 2: Usando PowerShell**
```powershell
echo OPENAI_API_KEY=sk-sua-chave-aqui > .env
```

Adicione no arquivo:
```
OPENAI_API_KEY=sk-sua-chave-aqui
```

**Nota**: A chave OpenAI é necessária apenas se você usar o método OpenAI. O Google Translate não requer chave.

---

## 🐧 Instalação no Linux/Mac

### Passo 1: Instalar Python venv

```bash
sudo apt install python3.12-venv
```

### Passo 2: Executar script de instalação

```bash
./install.sh
```

Este script irá:
- Criar ambiente virtual Python
- Instalar dependências Python
- Instalar dependências do frontend
- Configurar o projeto

### Passo 3: Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
echo "OPENAI_API_KEY=sk-sua-chave-aqui" > .env
```

**Nota**: A chave OpenAI é necessária apenas se você usar o método OpenAI. O Google Translate não requer chave.

## 🏃 Como Rodar

### Opção 1: Interface Web (Recomendado)

#### 🪟 Windows

**Terminal 1 - Backend (API)**

Abra um **Prompt de Comando** ou **PowerShell** e execute:

```cmd
scripts\run_api.bat
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

**Terminal 2 - Frontend**

Abra outro **Prompt de Comando** ou **PowerShell** e execute:

```cmd
scripts\run_frontend.bat
```

O frontend estará disponível em:
- **Interface**: http://localhost:3000

#### 🐧 Linux/Mac

**Terminal 1 - Backend (API)**

```bash
./scripts/run_api.sh
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

**Terminal 2 - Frontend**

```bash
./scripts/run_frontend.sh
```

O frontend estará disponível em:
- **Interface**: http://localhost:3000

### Opção 2: Scripts CLI

#### 🪟 Windows

**Google Translate (Gratuito)**

```cmd
scripts\run.bat en.json pt
```

**OpenAI (Requer chave API)**

```cmd
scripts\run_openai.bat en.json pt
```

#### 🐧 Linux/Mac

**Google Translate (Gratuito)**

```bash
./scripts/run.sh en.json pt
```

**OpenAI (Requer chave API)**

```bash
./scripts/run_openai.sh en.json pt
```

## 📖 Como Usar - Interface Web

### Passo 1: Upload do Arquivo

1. Acesse http://localhost:3000
2. Clique em "Nova Tradução"
3. Faça upload do arquivo JSON (formato `.json`)
4. Aguarde a validação do arquivo

### Passo 2: Validação

O sistema irá:
- Validar a estrutura JSON
- Contar total de entradas
- Contar strings para traduzir
- Exibir informações do arquivo

### Passo 3: Configuração

Configure os parâmetros:

- **Método de Tradução**:
  - 🤖 **OpenAI (IA)**: Mais rápido, melhor qualidade, requer chave API (pago)
  - 🌐 **Google Translate**: Gratuito, mais lento, boa qualidade

- **Modelo OpenAI** (apenas se método OpenAI):
  - Escolha entre modelos disponíveis (gpt-4o-mini, gpt-4o, etc.)
  - Veja preços por modelo

- **Idioma de Destino**:
  - Selecione o idioma para traduzir (pt, es, fr, de, etc.)
  - Tradução sempre a partir do inglês

- **Tamanho do Batch**:
  - Quantidade de strings por lote (máximo: 250, recomendado: 100-200)
  - Valores maiores = menos requisições, mas mais tempo por lote

- **Batches Paralelos**:
  - Quantos lotes processar simultaneamente (máximo: 10, recomendado: 3-5)
  - Mais paralelos = mais rápido, mas mais carga no sistema

### Passo 4: Estimativa

O sistema calculará e exibirá:
- **Strings para Traduzir**: Total de strings a traduzir
- **Batches Estimados**: Quantos lotes serão processados
- **Custo Estimado**: Custo em USD (apenas OpenAI)
- **Tempo Estimado**: Tempo aproximado de processamento
- **Detalhes**: Tokens, modelo, configurações

### Passo 5: Iniciar Tradução

1. Revise a estimativa
2. Clique em "Iniciar Tradução"
3. Acompanhe o progresso em tempo real:
   - Progresso percentual
   - Strings traduzidas
   - Strings em cache
   - Custo atual (OpenAI)
   - Tempo decorrido
   - ETA (tempo estimado restante)

### Passo 6: Resultado

Após conclusão:
- Visualize o arquivo traduzido
- Baixe o arquivo traduzido
- Veja estatísticas finais:
  - Total traduzido
  - Total em cache
  - Custo final (OpenAI)
  - Tempo total

## 📄 Formato de Arquivo Esperado

### Estrutura JSON Válida

O sistema aceita qualquer JSON válido com estrutura aninhada:

```json
{
  "chave1": "Texto em inglês",
  "chave2": {
    "subchave1": "Outro texto",
    "subchave2": ["Item 1", "Item 2"]
  },
  "chave3": [
    {
      "item": "Texto do item"
    }
  ]
}
```

### Exemplo Real

```json
{
  "Metadata": {
    "title": "Social Protection",
    "description": "The knowledge-sharing platform on social protection"
  },
  "Header": {
    "languagePickPlaceHolder": "Select a language",
    "english": "English",
    "spanish": "Spanish"
  },
  "CookieBanner": {
    "title": "Your privacy matters",
    "description": "We use cookies to enhance your browsing experience"
  }
}
```

### O que é Traduzido

✅ **Traduzido**:
- Valores de string não vazios
- Strings em arrays
- Strings em objetos aninhados

❌ **NÃO Traduzido**:
- Chaves do JSON
- Números
- Booleanos (true/false)
- Null
- Strings vazias
- Strings que já estão no cache

### Limitações

- Arquivo deve ser JSON válido
- Tamanho máximo recomendado: 10MB
- Strings muito longas (>5000 caracteres) podem ser divididas

## 📤 Resultados e Saída

### Localização dos Arquivos

Os arquivos traduzidos são salvos em:
```
output/translated_[hash]_[idioma].json
```

Exemplo:
```
output/translated_00f98c9b_pt.json
output/translated_0918369a_es.json
```

### Estrutura do Arquivo Traduzido

O arquivo traduzido mantém **exatamente a mesma estrutura** do original:

**Original (en.json)**:
```json
{
  "Header": {
    "title": "Welcome",
    "subtitle": "Hello world"
  }
}
```

**Traduzido para Português (pt.json)**:
```json
{
  "Header": {
    "title": "Bem-vindo",
    "subtitle": "Olá mundo"
  }
}
```

**Nota**: As chaves `Header`, `title`, `subtitle` permanecem inalteradas!

### Cache

O sistema mantém cache de traduções:
- Strings já traduzidas não são retraduzidas
- Melhora performance em execuções subsequentes
- Reduz custos (OpenAI) e tempo de processamento

## ⚡ Benchmarks e Performance

### OpenAI (gpt-4o-mini)

**Configuração de teste**:
- Arquivo: 3,649 strings
- Batch Size: 100
- Paralelos: 3
- Modelo: gpt-4o-mini

**Resultados**:
- ⏱️ **Tempo**: ~37-60 segundos
- 💰 **Custo**: ~$0.02-0.03 USD
- 📊 **Velocidade**: ~60-100 strings/segundo
- 🎯 **Qualidade**: Excelente

**Fatores que afetam performance**:
- Tamanho do batch (maior = menos requisições, mas mais tempo por lote)
- Paralelismo (mais paralelos = mais rápido, mas mais carga)
- Tamanho das strings (strings maiores = mais tokens = mais custo)

### Google Translate

**Configuração de teste**:
- Arquivo: 3,649 strings
- Paralelos: 2 (limitado por rate limits)

**Resultados**:
- ⏱️ **Tempo**: ~48-60 minutos (0.8s por string)
- 💰 **Custo**: $0.00 (gratuito)
- 📊 **Velocidade**: ~1-2 strings/segundo
- 🎯 **Qualidade**: Boa

**Fatores que afetam performance**:
- Rate limits do Google Translate
- Paralelismo limitado (máximo 2)
- Delay entre requisições (0.1s)

### Comparação

| Método | Velocidade | Custo | Qualidade | Melhor Para |
|--------|-----------|-------|-----------|-------------|
| OpenAI | ⚡⚡⚡ Muito Rápido | 💰 Pago | ⭐⭐⭐ Excelente | Produção, grandes volumes |
| Google Translate | 🐌 Lento | 🆓 Gratuito | ⭐⭐ Boa | Testes, pequenos volumes |

### Otimizações

1. **Use cache**: Strings já traduzidas são reutilizadas
2. **Ajuste batch size**: 100-200 é ideal para maioria dos casos
3. **Paralelismo**: 3-5 paralelos é o sweet spot
4. **Escolha o método certo**: OpenAI para velocidade, Google para economia

## 🏗️ Arquitetura

### Backend

- **Framework**: FastAPI (Python)
- **Processamento**: Assíncrono (asyncio)
- **Tradução OpenAI**: OpenAI API
- **Tradução Google**: deep-translator (Google Translate)
- **Cache**: Em memória (durante execução)

### Frontend

- **Framework**: React 18
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Styling**: CSS Modules

### Fluxo de Tradução

```
1. Upload JSON → Validação
2. Configuração → Método, Idioma, Parâmetros
3. Estimativa → Custo, Tempo, Tokens
4. Processamento → Tradução em lotes paralelos
5. Resultado → JSON traduzido preservando estrutura
```

## 🌍 Idiomas Suportados

O sistema suporta tradução do inglês para:

- 🇵🇹 Português (pt)
- 🇪🇸 Espanhol (es)
- 🇫🇷 Francês (fr)
- 🇩🇪 Alemão (de)
- 🇮🇹 Italiano (it)
- 🇳🇱 Holandês (nl)
- 🇵🇱 Polonês (pl)
- 🇸🇪 Sueco (sv)
- 🇩🇰 Dinamarquês (da)
- 🇳🇴 Norueguês (no)
- 🇫🇮 Finlandês (fi)
- 🇨🇿 Tcheco (cs)
- 🇭🇺 Húngaro (hu)
- 🇷🇴 Romeno (ro)
- 🇭🇷 Croata (hr)
- 🇷🇸 Sérvio (sr)
- 🇹🇷 Turco (tr)
- 🇮🇩 Indonésio (id)
- 🇵🇭 Filipino/Tagalog (tl)
- 🇲🇾 Malaio (ms)

## 🔧 Troubleshooting

### 🪟 Windows

#### Erro: "Python não é reconhecido como comando"

**Solução**: 
1. Reinstale Python marcando "Add Python to PATH"
2. Ou adicione manualmente Python ao PATH:
   - Abra "Variáveis de Ambiente" no Painel de Controle
   - Adicione `C:\Python312` (ou versão instalada) ao PATH
   - Reinicie o terminal

#### Erro: "Node não é reconhecido como comando"

**Solução**: 
1. Reinstale Node.js
2. Ou adicione manualmente ao PATH:
   - Normalmente em `C:\Program Files\nodejs\`
   - Reinicie o terminal

#### Erro ao executar scripts .bat

**Solução**: 
- Certifique-se de executar no **Prompt de Comando** ou **PowerShell**
- Navegue até a pasta do projeto antes de executar:
  ```cmd
  cd C:\caminho\para\translate_script
  scripts\install_windows.bat
  ```

#### Erro: "venv\Scripts\activate.bat não encontrado"

**Solução**: 
- Execute o script de instalação novamente:
  ```cmd
  scripts\install_windows.bat
  ```

#### Firewall bloqueando conexões

**Solução**: 
- Permita Python e Node.js através do Firewall do Windows
- Ou desative temporariamente o firewall para testes

### 🐧 Linux/Mac

#### Erro: "permission denied" ao executar scripts

**Solução**: 
```bash
chmod +x install.sh
chmod +x scripts/*.sh
```

### Geral

#### Erro: "OPENAI_API_KEY não encontrada"

**Solução**: Crie um arquivo `.env` na raiz com sua chave:

**Windows:**
```cmd
notepad .env
```

**Linux/Mac:**
```bash
echo "OPENAI_API_KEY=sk-sua-chave-aqui" > .env
```

#### Erro: "JSON inválido"

**Solução**: Verifique se o arquivo é um JSON válido. Use um validador JSON online.

#### Erro: "Tamanho do batch deve estar entre 1 e 250"

**Solução**: Ajuste o tamanho do batch para um valor entre 1 e 250.

#### Tradução muito lenta (Google Translate)

**Causa**: Google Translate tem rate limits e é naturalmente mais lento.

**Solução**: 
- Use OpenAI para maior velocidade
- Reduza paralelismo para 1-2
- Aguarde o processamento (é normal ser lento)

#### Erro de conexão com API

**Solução**:
- Verifique se o backend está rodando (http://localhost:8000)
- Verifique se há firewall bloqueando
- Verifique logs do backend

#### Arquivo não aparece na lista

**Solução**:
- Verifique a pasta `output/`
- Recarregue a página
- Verifique permissões de escrita na pasta `output/`

## 📚 Documentação Completa

Consulte a pasta `docs/` para documentação detalhada:

### 📖 Guias Essenciais
- **[QUICK_START.md](docs/QUICK_START.md)** - Guia rápido para começar em minutos
- **[INSTALL.md](docs/INSTALL.md)** - Instalação completa passo a passo
- **[FILE_FORMAT.md](docs/FILE_FORMAT.md)** - Formato de arquivo e exemplos práticos
- **[BENCHMARKS.md](docs/BENCHMARKS.md)** - Benchmarks, performance e otimizações

### 🔧 Documentação Técnica
- **[README_API.md](docs/README_API.md)** - Documentação completa da API REST
- **[README_FRONTEND.md](docs/README_FRONTEND.md)** - Documentação do frontend React
- **[README_OPENAI.md](docs/README_OPENAI.md)** - Detalhes do script OpenAI CLI

## 🔐 Segurança

- ⚠️ **Nunca commite** o arquivo `.env` com sua chave API
- ⚠️ Mantenha sua chave OpenAI segura
- ⚠️ O Google Translate não requer chave, mas tem rate limits

## 📝 Licença

Este projeto é de uso interno.

## 🤝 Contribuindo

Para contribuir:
1. Faça suas alterações
2. Teste localmente
3. Documente mudanças
4. Submeta para revisão

## 📞 Suporte

Para problemas ou dúvidas:
- Verifique a documentação em `docs/`
- Consulte os logs do backend
- Verifique a documentação da API em http://localhost:8000/docs

---

**Desenvolvido para tradução eficiente de arquivos JSON mantendo integridade estrutural** 🚀
