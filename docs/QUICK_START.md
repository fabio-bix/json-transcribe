# Guia Rápido - JSON Translator

Guia rápido para começar a usar o JSON Translator em minutos.

## 🚀 Instalação Rápida

### 1. Instalar Python venv

```bash
sudo apt install python3.12-venv
```

### 2. Executar instalação

```bash
./install.sh
```

### 3. Configurar chave OpenAI (Opcional)

Crie arquivo `.env` na raiz:
```
OPENAI_API_KEY=sk-sua-chave-aqui
```

**Nota**: A chave é necessária apenas para usar o método OpenAI. Google Translate não requer chave.

## 🏃 Rodar o Sistema

### Interface Web (Recomendado)

**Terminal 1 - Backend:**
```bash
./scripts/run_api.sh
```

**Terminal 2 - Frontend:**
```bash
./scripts/run_frontend.sh
```

Acesse: http://localhost:3000

### Scripts CLI

**Google Translate (Gratuito):**
```bash
./scripts/run.sh en.json pt
```

**OpenAI (Requer chave):**
```bash
./scripts/run_openai.sh en.json pt
```

## 📖 Uso Rápido - Interface Web

1. **Upload**: Faça upload do arquivo JSON
2. **Configure**: Escolha método, idioma e parâmetros
3. **Estime**: Veja custo e tempo estimados
4. **Traduza**: Inicie e acompanhe o progresso
5. **Baixe**: Baixe o arquivo traduzido

## 📄 Formato do Arquivo

O sistema aceita qualquer JSON válido. Exemplo:

```json
{
  "Header": {
    "title": "Welcome",
    "subtitle": "Hello world"
  }
}
```

**Resultado traduzido (pt):**
```json
{
  "Header": {
    "title": "Bem-vindo",
    "subtitle": "Olá mundo"
  }
}
```

**Importante**: As chaves permanecem inalteradas! Apenas os valores são traduzidos.

## ⚡ Performance Rápida

| Método | Velocidade | Custo |
|--------|-----------|-------|
| OpenAI | ⚡⚡⚡ Muito Rápido | 💰 ~$0.02-0.03 por 3.6k strings |
| Google Translate | 🐌 Lento | 🆓 Gratuito |

## 🌍 Idiomas Suportados

pt, es, fr, de, it, nl, pl, sv, da, no, fi, cs, hu, ro, hr, sr, tr, id, tl, ms

## ❓ Problemas Comuns

**Erro de chave API**: Crie arquivo `.env` com `OPENAI_API_KEY=...`

**JSON inválido**: Valide seu JSON em um validador online

**Tradução lenta**: Google Translate é naturalmente lento. Use OpenAI para velocidade.

---

Para documentação completa, veja [README.md](../README.md)
