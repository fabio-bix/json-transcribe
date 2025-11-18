# API REST - JSON Translator

API REST para tradução de arquivos JSON usando OpenAI ou Google Translate.

## 🚀 Iniciando a API

```bash
# Instalar dependências (se ainda não instalou)
./install.sh

# Iniciar a API
./run_api.sh
```

A API estará disponível em: `http://localhost:8000`

## 📖 Documentação Interativa

Após iniciar a API, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints

### 1. Upload e Validação

**POST** `/api/upload`

Faz upload de um arquivo JSON e valida sua estrutura.

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@en.json"
```

**Resposta:**
```json
{
  "success": true,
  "filename": "en.json",
  "total_entries": 1234,
  "strings_count": 567,
  "data": { ... }
}
```

### 2. Estimar Custo e Tempo

**POST** `/api/translate/estimate`

Estima custo e tempo para uma tradução.

```bash
curl -X POST "http://localhost:8000/api/translate/estimate" \
  -H "Content-Type: application/json" \
  -d '{
    "target_language": "pt",
    "model": "gpt-4o-mini",
    "batch_size": 100,
    "parallel": 3,
    "json_data": { ... }
  }'
```

**Resposta:**
```json
{
  "success": true,
  "total_strings": 567,
  "total_entries": 1234,
  "estimated_batches": 6,
  "estimated_tokens_input": 12345,
  "estimated_tokens_output": 14814,
  "estimated_cost_usd": 0.012345,
  "estimated_time_seconds": 18,
  "model": "gpt-4o-mini",
  "batch_size": 100,
  "parallel": 3
}
```

### 3. Iniciar Tradução

**POST** `/api/translate/start`

Inicia uma tradução de forma assíncrona. Retorna um `job_id` para acompanhar o progresso.

```bash
curl -X POST "http://localhost:8000/api/translate/start" \
  -H "Content-Type: application/json" \
  -d '{
    "target_language": "pt",
    "model": "gpt-4o-mini",
    "batch_size": 100,
    "parallel": 3,
    "method": "openai",
    "json_data": { ... }
  }'
```

**Resposta:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Tradução iniciada"
}
```

### 4. Verificar Status

**GET** `/api/translate/{job_id}/status`

Obtém o status e progresso de uma tradução.

```bash
curl "http://localhost:8000/api/translate/550e8400-e29b-41d4-a716-446655440000/status"
```

**Resposta:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 0.65,
  "total_strings": 567,
  "translated_strings": 368,
  "cached_strings": 0,
  "current_batch": 4,
  "total_batches": 6,
  "stats": {
    "total_prompt_tokens": 12345,
    "total_completion_tokens": 14814,
    "total_tokens": 27159,
    "api_calls": 4,
    "translated": 368,
    "cached": 0,
    "errors": 0
  },
  "estimated_cost": 0.012345,
  "actual_cost": 0.008234,
  "eta_seconds": 12,
  "elapsed_seconds": 15.5,
  "error_message": null
}
```

**Status possíveis:**
- `pending`: Aguardando início
- `processing`: Em processamento
- `completed`: Concluído
- `failed`: Falhou

### 5. Obter Resultado

**GET** `/api/translate/{job_id}/result`

Obtém o resultado de uma tradução concluída.

```bash
curl "http://localhost:8000/api/translate/550e8400-e29b-41d4-a716-446655440000/result"
```

**Resposta:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": { ... },
  "stats": {
    "total_strings": 567,
    "translated": 567,
    "cached": 0,
    "cost_usd": 0.012345,
    "tokens": 27159
  }
}
```

### 6. Listar Modelos

**GET** `/api/models`

Lista modelos OpenAI disponíveis com preços.

```bash
curl "http://localhost:8000/api/models"
```

**Resposta:**
```json
{
  "success": true,
  "models": [
    {
      "id": "gpt-4o-mini",
      "name": "gpt-4o-mini",
      "pricing": {
        "input_per_1m": 0.15,
        "output_per_1m": 0.60
      }
    },
    ...
  ],
  "default": "gpt-4o-mini"
}
```

### 7. Listar Idiomas

**GET** `/api/languages`

Lista idiomas suportados.

```bash
curl "http://localhost:8000/api/languages"
```

**Resposta:**
```json
{
  "success": true,
  "languages": [
    {"code": "pt", "name": "Portuguese (Brazilian)"},
    {"code": "es", "name": "Spanish"},
    ...
  ]
}
```

### 8. Listar Jobs

**GET** `/api/jobs`

Lista todos os jobs ativos.

```bash
curl "http://localhost:8000/api/jobs"
```

### 9. Remover Job

**DELETE** `/api/translate/{job_id}`

Remove um job de tradução.

```bash
curl -X DELETE "http://localhost:8000/api/translate/550e8400-e29b-41d4-a716-446655440000"
```

## 🔄 Fluxo de Uso

1. **Upload**: Faça upload do JSON e valide
2. **Estimar**: Estime custo e tempo
3. **Iniciar**: Inicie a tradução e obtenha o `job_id`
4. **Monitorar**: Verifique o status periodicamente usando o `job_id`
5. **Resultado**: Obtenha o resultado quando `status` for `completed`

## 📝 Exemplo Completo (cURL)

```bash
# 1. Upload
UPLOAD_RESPONSE=$(curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@en.json")

# 2. Estimar (usando o JSON do upload)
curl -X POST "http://localhost:8000/api/translate/estimate" \
  -H "Content-Type: application/json" \
  -d "{
    \"target_language\": \"pt\",
    \"json_data\": $(echo $UPLOAD_RESPONSE | jq -r '.data')
  }"

# 3. Iniciar tradução
JOB_RESPONSE=$(curl -X POST "http://localhost:8000/api/translate/start" \
  -H "Content-Type: application/json" \
  -d "{
    \"target_language\": \"pt\",
    \"json_data\": $(echo $UPLOAD_RESPONSE | jq -r '.data')
  }")

JOB_ID=$(echo $JOB_RESPONSE | jq -r '.job_id')

# 4. Monitorar (em loop)
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/translate/$JOB_ID/status" | jq -r '.status')
  echo "Status: $STATUS"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  
  sleep 2
done

# 5. Obter resultado
curl "http://localhost:8000/api/translate/$JOB_ID/result" | jq '.data' > output.json
```

## 🛠️ Testando com Swagger

A forma mais fácil de testar é usando a interface Swagger:

1. Inicie a API: `./run_api.sh`
2. Acesse: http://localhost:8000/docs
3. Teste os endpoints diretamente na interface

## ⚠️ Notas

- Os jobs são armazenados em memória. Ao reiniciar a API, os jobs são perdidos.
- Para produção, considere usar Redis ou banco de dados para persistência.
- O método "google" ainda não está implementado na API (apenas no script CLI).

