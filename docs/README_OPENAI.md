# Script de Tradução JSON com OpenAI

Versão melhorada do script de tradução usando OpenAI API (GPT-4o-mini).

## Vantagens

✅ **Preserva placeholders** - Mantém `{{name}}`, `{count}`, `%s`, etc.  
✅ **Cache inteligente** - Evita retraduzir textos já processados  
✅ **Processamento em batch** - Mais eficiente e econômico  
✅ **Modo dry-run** - Testa sem escrever arquivo  
✅ **Preserva traduções manuais** - Não sobrescreve edições manuais  
✅ **Tradução de alta qualidade** - Usa GPT-4o-mini  

## Instalação

### 1. Instalar dependências

```bash
# Com ambiente virtual (recomendado)
source venv/bin/activate
pip install -r requirements_openai.txt

# Ou sem ambiente virtual
pip install openai python-dotenv
```

### 2. Configurar API Key

1. Obtenha sua API Key em: https://platform.openai.com/api-keys
2. Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

3. Edite `.env` e adicione sua chave:

```
OPENAI_API_KEY=sk-sua-chave-aqui
```

## Uso

### Tradução básica

```bash
python backend/scripts/script_openai.py en.json pt
```

### Modo dry-run (teste sem salvar)

```bash
python backend/scripts/script_openai.py en.json pt --dry
```

### Customizar tamanho do batch

```bash
python backend/scripts/script_openai.py en.json pt --batch 5
```

### Especificar arquivo de saída

```bash
python backend/scripts/script_openai.py en.json pt pt.json
```

### Usar modelo diferente

```bash
python backend/scripts/script_openai.py en.json pt --model gpt-4
```

## Opções

- `--dry` - Modo dry-run (não escreve arquivo, apenas mostra exemplos)
- `--batch N` - Tamanho do batch (padrão: 10)
- `--model MODEL` - Modelo OpenAI (padrão: gpt-4o-mini)

## Como funciona

1. **Lê o arquivo JSON** de entrada (`en.json`)
2. **Carrega traduções existentes** (se `pt.json` já existir)
3. **Carrega cache** de traduções anteriores
4. **Identifica strings para traduzir** (apenas as que mudaram ou não existem)
5. **Processa em batches** para eficiência
6. **Preserva placeholders** durante a tradução
7. **Salva cache** incrementalmente
8. **Mescla traduções** (preserva manuais, usa geradas para novas)
9. **Salva arquivo final** com backup automático

## Arquivos gerados

- `pt.json` - Arquivo traduzido
- `pt.json.bak` - Backup do arquivo anterior (se existir)
- `.translate_cache_pt.json` - Cache de traduções

## Custos

O modelo `gpt-4o-mini` é muito econômico:
- ~$0.15 por 1M tokens de entrada
- ~$0.60 por 1M tokens de saída

Para um arquivo como `en.json` (3702 linhas), o custo estimado é de **$0.01 - $0.05**.

## Exemplo de saída

```
Lendo arquivo: en.json
Arquivo pt.json existente carregado (preservará traduções manuais)
Cache carregado: 150 entradas

Total de strings em en.json: 3702
Strings para traduzir: 120
Tamanho do batch: 10
Modelo: gpt-4o-mini

Traduzindo batch 1/12 (tamanho: 10)...
Traduzindo batch 2/12 (tamanho: 10)...
...

✓ Tradução concluída!
  Arquivo salvo: pt.json
  Cache salvo: .translate_cache_pt.json
  Total traduzido: 120 strings
```

## Preservação de placeholders

O script preserva automaticamente:
- `{{name}}` → mantido como `{{name}}`
- `{count}` → mantido como `{count}`
- `%s`, `%d` → mantidos como estão

Exemplo:
- Original: `"Hello {{name}}, you have {count} messages"`
- Traduzido: `"Olá {{name}}, você tem {count} mensagens"`

## Comparação com versão Google Translate

| Característica | Google Translate | OpenAI |
|---------------|------------------|--------|
| Qualidade | Boa | Excelente |
| Preservação placeholders | Manual | Automática |
| Cache | Não | Sim |
| Batch processing | Não | Sim |
| Dry-run | Não | Sim |
| Custo | Grátis | ~$0.01-0.05 |
| Requer API Key | Não | Sim |

## Troubleshooting

### Erro: "OPENAI_API_KEY não encontrada"
- Verifique se o arquivo `.env` existe
- Confirme que a chave está correta
- Certifique-se de que `python-dotenv` está instalado

### Erro: "Rate limit exceeded"
- Reduza o tamanho do batch: `--batch 5`
- Aguarde alguns minutos e tente novamente

### Erro: "Insufficient quota"
- Verifique seu saldo na conta OpenAI
- Considere usar `gpt-4o-mini` (mais barato)


