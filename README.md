# Script de Tradução JSON

Script Python para traduzir arquivos JSON mantendo a estrutura e traduzindo apenas os valores de texto.

## Instalação

### Opção 1: Instalação Automática (Recomendado)
```bash
./install.sh
```

### Opção 2: Instalação Manual

1. Instale o pip3 (se ainda não tiver):
```bash
sudo apt install python3-pip
```

2. Instale as dependências:
```bash
pip3 install -r requirements.txt
```

### Opção 3: Usar pip do usuário (sem sudo)
```bash
# Baixar e instalar pip para o usuário
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user

# Adicionar ao PATH
export PATH=$PATH:~/.local/bin

# Instalar dependências
pip install --user -r requirements.txt
```

Para mais detalhes, consulte [INSTALL.md](INSTALL.md)

## Uso

### Opção 1: Usar o script helper (Recomendado)
```bash
# Traduzir para português
./run.sh en.json pt

# Especificar arquivo de saída
./run.sh en.json pt pt.json

# Traduzir para outros idiomas
./run.sh en.json es es.json
```

### Opção 2: Ativar ambiente virtual manualmente
```bash
# Ativar o ambiente virtual
source venv/bin/activate

# Traduzir para português
python src/script.py en.json pt

# Especificar arquivo de saída
python src/script.py en.json pt pt.json

# Traduzir para outros idiomas
python src/script.py en.json es es.json

# Desativar o ambiente virtual (quando terminar)
deactivate
```

## Parâmetros

- `arquivo_json`: Caminho do arquivo JSON de entrada (obrigatório)
- `idioma_destino`: Código do idioma de destino (padrão: 'pt')
- `arquivo_saida`: Caminho do arquivo JSON de saída (opcional, se não especificado, será criado automaticamente)

## Idiomas suportados

O script usa Google Translator, que suporta diversos idiomas. Alguns exemplos:
- `pt` - Português
- `es` - Espanhol
- `fr` - Francês
- `de` - Alemão
- `it` - Italiano
- `ja` - Japonês
- `zh` - Chinês

## Exemplo

```bash
# Traduzir en.json para português
./run.sh en.json pt

# Isso criará um arquivo en_pt.json com todas as traduções
```

## Notas

- O script mantém todas as chaves do JSON originais
- Apenas os valores de texto são traduzidos
- Números, booleanos e null são mantidos sem alteração
- A estrutura aninhada do JSON é preservada
- O processo pode levar alguns minutos para arquivos grandes

