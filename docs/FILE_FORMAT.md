# Formato de Arquivo - JSON Translator

Guia completo sobre o formato de arquivo esperado e como o sistema processa os arquivos JSON.

## 📄 Formato Esperado

O JSON Translator aceita **qualquer arquivo JSON válido** com estrutura aninhada de qualquer profundidade.

### Estrutura Básica

```json
{
  "chave1": "valor1",
  "chave2": "valor2",
  "chave3": {
    "subchave1": "subvalor1",
    "subchave2": "subvalor2"
  }
}
```

### Estrutura Aninhada (Suportada)

```json
{
  "level1": {
    "level2": {
      "level3": {
        "level4": "Texto profundo"
      }
    }
  },
  "array": [
    {
      "item": "Item do array"
    }
  ]
}
```

## ✅ O que é Traduzido

### Traduzido

- ✅ **Strings não vazias**: Qualquer string com conteúdo
- ✅ **Strings em objetos**: Valores de propriedades
- ✅ **Strings em arrays**: Elementos de array que são strings
- ✅ **Strings aninhadas**: Strings em qualquer nível de profundidade

**Exemplo:**
```json
{
  "title": "Welcome",           // ✅ Traduzido
  "items": ["One", "Two"],      // ✅ Traduzido
  "nested": {
    "text": "Hello"             // ✅ Traduzido
  }
}
```

### NÃO Traduzido

- ❌ **Chaves**: Todas as chaves permanecem inalteradas
- ❌ **Números**: Valores numéricos não são traduzidos
- ❌ **Booleanos**: `true` e `false` permanecem inalterados
- ❌ **Null**: Valores `null` permanecem `null`
- ❌ **Strings vazias**: `""` não é traduzido
- ❌ **Strings já em cache**: Strings já traduzidas são reutilizadas

**Exemplo:**
```json
{
  "title": "Welcome",           // ✅ Traduzido
  "count": 42,                  // ❌ Não traduzido (número)
  "active": true,               // ❌ Não traduzido (booleano)
  "data": null,                 // ❌ Não traduzido (null)
  "empty": "",                  // ❌ Não traduzido (vazio)
  "items": [1, 2, 3]           // ❌ Não traduzido (números)
}
```

## 📝 Exemplos Práticos

### Exemplo 1: Arquivo de Localização Simples

**Entrada (en.json):**
```json
{
  "Header": {
    "title": "Welcome",
    "subtitle": "Hello world",
    "button": "Click here"
  },
  "Footer": {
    "copyright": "All rights reserved",
    "year": 2024
  }
}
```

**Saída (pt.json):**
```json
{
  "Header": {
    "title": "Bem-vindo",
    "subtitle": "Olá mundo",
    "button": "Clique aqui"
  },
  "Footer": {
    "copyright": "Todos os direitos reservados",
    "year": 2024
  }
}
```

**Observações**:
- ✅ Chaves (`Header`, `title`, `subtitle`, etc.) permanecem inalteradas
- ✅ Strings são traduzidas
- ✅ Número (`year: 2024`) permanece inalterado

### Exemplo 2: Arquivo com Arrays

**Entrada (en.json):**
```json
{
  "menu": {
    "items": [
      "Home",
      "About",
      "Contact"
    ],
    "labels": {
      "home": "Home",
      "about": "About Us",
      "contact": "Get in Touch"
    }
  }
}
```

**Saída (pt.json):**
```json
{
  "menu": {
    "items": [
      "Início",
      "Sobre",
      "Contato"
    ],
    "labels": {
      "home": "Início",
      "about": "Sobre Nós",
      "contact": "Entre em Contato"
    }
  }
}
```

### Exemplo 3: Arquivo Complexo (Real)

**Entrada (en.json):**
```json
{
  "Metadata": {
    "title": "Social Protection",
    "description": "The knowledge-sharing platform on social protection"
  },
  "CookieBanner": {
    "title": "Your privacy matters",
    "description": "We use cookies to enhance your browsing experience, analyze site traffic, and personalise content. By clicking 'Accept', you agree to our use of cookies.",
    "accept": "Accept All",
    "decline": "Decline"
  },
  "Header": {
    "languagePickPlaceHolder": "Select a language",
    "english": "English",
    "spanish": "Spanish",
    "french": "French"
  }
}
```

**Saída (pt.json):**
```json
{
  "Metadata": {
    "title": "Proteção Social",
    "description": "A plataforma de compartilhamento de conhecimento sobre proteção social"
  },
  "CookieBanner": {
    "title": "Sua privacidade importa",
    "description": "Usamos cookies para melhorar sua experiência de navegação, analisar o tráfego do site e personalizar o conteúdo. Ao clicar em 'Aceitar', você concorda com o uso de cookies.",
    "accept": "Aceitar Tudo",
    "decline": "Recusar"
  },
  "Header": {
    "languagePickPlaceHolder": "Selecione um idioma",
    "english": "Inglês",
    "spanish": "Espanhol",
    "french": "Francês"
  }
}
```

## 🔍 Detalhes Técnicos

### Processamento

1. **Flattening**: O JSON é "achatado" em uma lista de entradas
   ```
   {"Header": {"title": "Welcome"}}
   ↓
   [{"key": "Header.title", "value": "Welcome"}]
   ```

2. **Filtragem**: Apenas strings não vazias são selecionadas

3. **Tradução**: Strings são traduzidas em lotes (batches)

4. **Reconstrução**: JSON é reconstruído mantendo estrutura original

### Preservação de Estrutura

O sistema garante que:
- ✅ Ordem das chaves é preservada
- ✅ Estrutura aninhada é mantida
- ✅ Arrays mantêm mesma ordem
- ✅ Tipos de dados são preservados

### Cache

Strings traduzidas são armazenadas em cache:
- **Primeira execução**: Todas as strings são traduzidas
- **Execuções subsequentes**: Strings em cache são reutilizadas
- **Benefício**: Reduz tempo e custo em 30-70%

## ⚠️ Limitações e Considerações

### Tamanho do Arquivo

- **Recomendado**: Até 10MB
- **Máximo prático**: 50MB (pode ser lento)
- **Muito grande**: Considere dividir em múltiplos arquivos

### Strings Muito Longas

- Strings > 5000 caracteres podem ser divididas
- Recomendado: Strings < 2000 caracteres
- Para textos longos, considere dividir em parágrafos

### Caracteres Especiais

- ✅ Suporta Unicode completo
- ✅ Emojis são preservados
- ✅ Caracteres especiais são mantidos
- ⚠️ Alguns caracteres podem não traduzir bem

### Placeholders

O sistema tenta preservar placeholders:
- `{variable}` → Preservado
- `{{variable}}` → Preservado
- `%s`, `%d` → Preservado

**Exemplo:**
```json
{
  "message": "Hello {name}, you have {count} messages"
}
```

Pode resultar em:
```json
{
  "message": "Olá {name}, você tem {count} mensagens"
}
```

## 📋 Checklist de Validação

Antes de fazer upload, verifique:

- [ ] Arquivo é JSON válido
- [ ] Extensão é `.json`
- [ ] Estrutura está correta
- [ ] Strings estão em inglês (idioma origem)
- [ ] Tamanho é razoável (< 10MB)
- [ ] Não há caracteres problemáticos

## 🧪 Testando o Formato

### Validação Online

Use um validador JSON online:
- https://jsonlint.com/
- https://jsonformatter.org/

### Teste Local

```bash
python3 -m json.tool seu_arquivo.json
```

Se não houver erros, o JSON é válido!

## 💡 Dicas

1. **Organize bem**: Estrutura clara facilita manutenção
2. **Use chaves descritivas**: Facilita encontrar traduções
3. **Evite strings muito longas**: Divida em parágrafos menores
4. **Mantenha consistência**: Use mesmo padrão de chaves
5. **Teste primeiro**: Teste com arquivo pequeno antes de processar grandes volumes

---

**Pronto para traduzir?** Veja [QUICK_START.md](QUICK_START.md) para começar!

