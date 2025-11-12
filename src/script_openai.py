#!/usr/bin/env python3
"""
Script para traduzir arquivos JSON usando OpenAI API.

Funcionalidades:
- Preserva placeholders como {{name}}, {count}, %s, etc.
- Cache local para evitar retraduções
- Processamento em batch para eficiência
- Modo dry-run: gera relatório sem escrever arquivo
- Preserva traduções manuais existentes

Requisitos:
  pip install openai python-dotenv

Uso:
  python src/script_openai.py en.json pt              # tradução normal
  python src/script_openai.py en.json pt --dry        # dry-run
  python src/script_openai.py en.json pt --batch 5    # batch size customizado
"""

import json
import sys
import os
import re
import shutil
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    print("ERRO: Biblioteca 'openai' não instalada.")
    print("Execute: pip install openai python-dotenv")
    sys.exit(1)

load_dotenv()

# Configuração
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("ERRO: OPENAI_API_KEY não encontrada no arquivo .env")
    print("Crie um arquivo .env com: OPENAI_API_KEY=sk-...")
    sys.exit(1)

# Inicializar cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Constantes
DEFAULT_BATCH_SIZE = 100  # Otimizado: gpt-4o-mini suporta ~16k tokens
DEFAULT_MODEL = "gpt-4o-mini"  # Modelo mais barato e rápido
DEFAULT_PARALLEL = 3  # Número de batches paralelos (3-5 é ideal)

# Preços por 1M tokens (atualizado em dezembro 2024)
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}


def parse_args() -> Dict[str, Any]:
    """Parse argumentos da linha de comando."""
    args = {
        "input_file": None,
        "target_language": "pt",
        "output_file": None,
        "dry_run": False,
        "batch_size": DEFAULT_BATCH_SIZE,
        "model": DEFAULT_MODEL,
        "verbose": False,
        "parallel": DEFAULT_PARALLEL,
    }
    
    if len(sys.argv) < 2:
        return args
    
    args["input_file"] = sys.argv[1]
    
    if len(sys.argv) > 2:
        args["target_language"] = sys.argv[2]
    
    if len(sys.argv) > 3:
        args["output_file"] = sys.argv[3]
    
    # Parse flags
    if "--dry" in sys.argv:
        args["dry_run"] = True
    
    if "--batch" in sys.argv:
        idx = sys.argv.index("--batch")
        if idx + 1 < len(sys.argv):
            try:
                args["batch_size"] = int(sys.argv[idx + 1])
            except ValueError:
                pass
    
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            args["model"] = sys.argv[idx + 1]
    
    if "--verbose" in sys.argv or "-v" in sys.argv:
        args["verbose"] = True
    else:
        args["verbose"] = False
    
    if "--parallel" in sys.argv:
        idx = sys.argv.index("--parallel")
        if idx + 1 < len(sys.argv):
            try:
                args["parallel"] = int(sys.argv[idx + 1])
            except ValueError:
                pass
    else:
        args["parallel"] = DEFAULT_PARALLEL
    
    return args


def flatten_object(obj: Any, prefix: str = "") -> List[Dict[str, Any]]:
    """
    Percorre objeto JSON e retorna lista de paths e valores.
    
    Args:
        obj: Objeto JSON (dict, list, ou valor primitivo)
        prefix: Prefixo para as chaves (usado recursivamente)
    
    Returns:
        Lista de dicionários com 'key' e 'value'
    """
    entries = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                entries.extend(flatten_object(value, full_key))
            else:
                # Para arrays e valores primitivos, preserva como está
                entries.append({"key": full_key, "value": value})
    elif isinstance(obj, list):
        # Se o objeto raiz é uma lista, processa cada item
        for i, item in enumerate(obj):
            item_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
            if isinstance(item, dict):
                entries.extend(flatten_object(item, item_key))
            else:
                entries.append({"key": item_key, "value": item})
    
    return entries


def unflatten(entries: List[Dict[str, Any]]) -> Dict:
    """
    Reconstrói objeto JSON a partir de entradas achatadas.
    
    Args:
        entries: Lista de dicionários com 'key' e 'value'
    
    Returns:
        Objeto JSON reconstruído
    """
    result = {}
    
    # Ordena entradas por profundidade (mais rasas primeiro) para construir hierarquia corretamente
    # Chaves mais rasas (menos pontos) vêm primeiro
    sorted_entries = sorted(entries, key=lambda x: (x["key"].count("."), x["key"]))
    
    for entry in sorted_entries:
        key = entry["key"]
        value = entry["value"]
        
        # Processa arrays (chaves com [index]) - por enquanto ignora
        # Arrays são preservados como valores completos no flatten
        if "[" in key and "]" in key:
            continue
        
        parts = key.split(".")
        
        current = result
        conflict = False
        
        # Navega até o penúltimo nível
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                # Cria novo dicionário se não existe
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Conflito: já existe um valor não-dict nesta posição
                # Isso significa que temos "key": "value" e "key.subkey": "value2"
                # Neste caso, ignoramos a entrada aninhada
                conflict = True
                break
            current = current[part]
        
        # Só atribui se não houve conflito
        if not conflict:
            final_key = parts[-1]
            if isinstance(current, dict):
                current[final_key] = value
    
    return result


def reconstruct_json_preserving_order(
    original_obj: Any,
    translated_dict: Dict[str, str],
    path: str = ""
) -> Any:
    """
    Reconstrói JSON preservando a ordem original das chaves,
    apenas substituindo os valores traduzidos.
    
    Args:
        original_obj: Objeto JSON original
        translated_dict: Dicionário com chaves achatadas e valores traduzidos
        path: Caminho atual (usado recursivamente)
    
    Returns:
        Objeto JSON reconstruído com valores traduzidos
    """
    if isinstance(original_obj, dict):
        result = {}
        for key, value in original_obj.items():
            full_key = f"{path}.{key}" if path else key
            
            if isinstance(value, dict):
                # Recursivamente processa dicionários aninhados
                result[key] = reconstruct_json_preserving_order(
                    value, translated_dict, full_key
                )
            elif isinstance(value, list):
                # Processa arrays
                result[key] = [
                    reconstruct_json_preserving_order(
                        item, translated_dict, f"{full_key}[{i}]"
                    )
                    for i, item in enumerate(value)
                ]
            else:
                # Valor primitivo - verifica se há tradução
                if full_key in translated_dict:
                    result[key] = translated_dict[full_key]
                else:
                    result[key] = value
        
        return result
    
    elif isinstance(original_obj, list):
        # Se o objeto raiz é uma lista
        return [
            reconstruct_json_preserving_order(
                item, translated_dict, f"{path}[{i}]" if path else f"[{i}]"
            )
            for i, item in enumerate(original_obj)
        ]
    
    else:
        # Valor primitivo na raiz
        if path in translated_dict:
            return translated_dict[path]
        return original_obj


def mask_placeholders(text: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Preserva placeholders substituindo por tokens antes de enviar à API.
    
    Args:
        text: Texto original
    
    Returns:
        Tupla (texto_mascarado, lista_de_placeholders)
    """
    patterns = [
        (re.compile(r'\{\{\s*[\w\.\-]+\s*\}\}'), "__PH_GG__"),      # {{name}}
        (re.compile(r'\{\s*[\w\.\-]+\s*\}'), "__PH_ICU__"),         # {count} or ICU
        (re.compile(r'%[sd]'), "__PH_PRINTF__"),                    # %s, %d
    ]
    
    placeholder_map = []
    masked_text = text
    
    for pattern, tag in patterns:
        def replace_func(match):
            token = f"{tag}{len(placeholder_map)}__"
            placeholder_map.append({"token": token, "original": match.group(0)})
            return token
        
        masked_text = pattern.sub(replace_func, masked_text)
    
    return masked_text, placeholder_map


def restore_placeholders(text: str, placeholder_map: List[Dict[str, str]]) -> str:
    """
    Restaura placeholders originais no texto traduzido.
    
    Args:
        text: Texto traduzido com tokens
        placeholder_map: Mapa de tokens para placeholders originais
    
    Returns:
        Texto com placeholders restaurados
    """
    result = text
    for item in placeholder_map:
        result = result.replace(item["token"], item["original"])
    return result


def call_openai_batch(
    texts: List[str], 
    model: str = DEFAULT_MODEL, 
    target_lang: str = "pt",
    stats: Optional[Dict] = None
) -> Tuple[List[str], Dict[str, int]]:
    """
    Chama API OpenAI para traduzir múltiplos textos de uma vez (batch real).
    
    Args:
        texts: Lista de textos a traduzir
        model: Modelo OpenAI a usar
        target_lang: Idioma de destino
        stats: Dicionário para acumular estatísticas (opcional)
    
    Returns:
        Tupla (lista_textos_traduzidos, uso_tokens)
    """
    lang_names = {
        "pt": "Brazilian Portuguese",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
    }
    
    target_lang_name = lang_names.get(target_lang, target_lang)
    
    # Prompt simplificado (reduz tokens em ~10-15%)
    texts_list = "\n".join(texts)
    prompt = (
        f"Translate the following texts into {target_lang_name}. "
        "Preserve placeholders like {{name}}, {{count}}, %s exactly as-is. "
        "Return only the translations, one per line, in order:\n\n"
        + texts_list
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"Translate texts into {target_lang_name}. Preserve placeholders like {{name}}, {{count}}, %s. Return only translations, one per line, in order."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0,
            max_tokens=8000  # Aumentado para batches maiores
        )
        
        # Extrai informações de uso
        usage = response.usage
        token_usage = {
            "prompt_tokens": usage.prompt_tokens if hasattr(usage, 'prompt_tokens') else usage.input_tokens,
            "completion_tokens": usage.completion_tokens if hasattr(usage, 'completion_tokens') else usage.output_tokens,
            "total_tokens": usage.total_tokens
        }
        
        # Atualiza estatísticas se fornecido
        if stats:
            stats["total_prompt_tokens"] = stats.get("total_prompt_tokens", 0) + token_usage["prompt_tokens"]
            stats["total_completion_tokens"] = stats.get("total_completion_tokens", 0) + token_usage["completion_tokens"]
            stats["total_tokens"] = stats.get("total_tokens", 0) + token_usage["total_tokens"]
            stats["api_calls"] = stats.get("api_calls", 0) + 1
        
        # Parse resposta - divide por linhas
        translated_text = response.choices[0].message.content.strip()
        
        # Divide por linhas e limpa
        lines = [line.strip() for line in translated_text.split('\n') if line.strip()]
        
        # Remove números e marcadores se a IA adicionou (ex: "1. texto" -> "texto")
        cleaned_lines = []
        for line in lines:
            # Remove padrões como "1.", "1)", "- ", etc.
            cleaned = re.sub(r'^[\d\-•]\s*[\.\)]\s*', '', line)
            cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
            cleaned_lines.append(cleaned)
        
        # Se não temos linhas suficientes, tenta dividir por outros separadores
        if len(cleaned_lines) < len(texts):
            # Tenta dividir por ponto e vírgula ou outros separadores
            if len(cleaned_lines) == 1:
                # Pode estar tudo em uma linha separada por algo
                alt_split = re.split(r'[;|]', cleaned_lines[0])
                if len(alt_split) > 1:
                    cleaned_lines = [s.strip() for s in alt_split if s.strip()]
        
        # Garante que temos o mesmo número de traduções
        while len(cleaned_lines) < len(texts):
            cleaned_lines.append("")
        
        return cleaned_lines[:len(texts)], token_usage
    
    except Exception as e:
        print(f"\n❌ Erro ao chamar OpenAI API: {e}")
        raise


async def translate_batch_async(
    items: List[Dict[str, Any]],
    cache: Dict[str, str],
    target_lang: str,
    model: str,
    stats: Dict[str, Any],
    batch_num: int = 0,
    total_batches: int = 0,
    verbose: bool = False,
    lock: Optional[asyncio.Lock] = None
) -> List[Dict[str, Any]]:
    """
    Traduz um batch de itens usando batch real (múltiplas strings por chamada).
    
    Args:
        items: Lista de itens para traduzir [{key, value}]
        cache: Cache de traduções
        target_lang: Idioma de destino
        model: Modelo OpenAI
        stats: Dicionário de estatísticas
        batch_num: Número do batch atual
        total_batches: Total de batches
        verbose: Se True, mostra logs detalhados
    
    Returns:
        Lista de resultados [{key, translated, fromCache}]
    """
    results = []
    
    # Separa itens em cache e itens para traduzir
    items_to_translate = []
    placeholder_maps = []
    
    for item in items:
        original = str(item["value"])
        key = item["key"]
        
        # Verifica cache
        if original in cache:
            stats["cached"] = stats.get("cached", 0) + 1
            results.append({
                "key": key,
                "translated": cache[original],
                "fromCache": True
            })
        else:
            # Mascara placeholders e adiciona à lista
            masked, placeholder_map = mask_placeholders(original)
            items_to_translate.append({
                "key": key,
                "original": original,
                "masked": masked
            })
            placeholder_maps.append(placeholder_map)
    
    # Se não há nada para traduzir, retorna
    if not items_to_translate:
        return results
    
    # Traduz todos de uma vez (batch real)
    try:
        masked_texts = [item["masked"] for item in items_to_translate]
        # Usa asyncio para chamada assíncrona
        # Cria stats local para thread-safety
        local_stats = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        
        translated_raw_list, token_usage = await asyncio.to_thread(
            call_openai_batch, masked_texts, model, target_lang, local_stats
        )
        
        # Atualiza stats global com lock para thread-safety
        if lock and stats:
            async with lock:
                stats["total_prompt_tokens"] = stats.get("total_prompt_tokens", 0) + token_usage["prompt_tokens"]
                stats["total_completion_tokens"] = stats.get("total_completion_tokens", 0) + token_usage["completion_tokens"]
                stats["total_tokens"] = stats.get("total_tokens", 0) + token_usage["total_tokens"]
                stats["api_calls"] = stats.get("api_calls", 0) + 1
        
        # Processa resultados
        for i, item in enumerate(items_to_translate):
            try:
                translated_raw = translated_raw_list[i] if i < len(translated_raw_list) else item["original"]
                translated = restore_placeholders(translated_raw, placeholder_maps[i])
                
                # Salva no cache (com lock se paralelo)
                if lock:
                    async with lock:
                        cache[item["original"]] = translated
                        stats["translated"] = stats.get("translated", 0) + 1
                else:
                    cache[item["original"]] = translated
                    stats["translated"] = stats.get("translated", 0) + 1
                
                results.append({
                    "key": item["key"],
                    "translated": translated,
                    "fromCache": False
                })
            except Exception as e:
                if verbose:
                    print(f"  ⚠️  Erro ao processar '{item['key']}': {e}")
                stats["errors"] = stats.get("errors", 0) + 1
                results.append({
                    "key": item["key"],
                    "translated": item["original"],
                    "fromCache": False
                })
        
        # Log resumido do batch (apenas se verbose)
        if verbose:
            cost = calculate_cost(token_usage, model)
            print(f"  📊 Batch {batch_num}: {len(items_to_translate)} strings | "
                  f"Tokens: {token_usage['total_tokens']:,} | Custo: ${cost:.6f}")
        
    except Exception as e:
        if verbose:
            print(f"  ❌ Erro no batch {batch_num}: {e}")
        stats["errors"] = stats.get("errors", 0) + len(items_to_translate)
        # Em caso de erro, mantém originais
        for item in items_to_translate:
            results.append({
                "key": item["key"],
                "translated": item["original"],
                "fromCache": False
            })
    
    return results


def calculate_cost(token_usage: Dict[str, int], model: str) -> float:
    """
    Calcula o custo baseado no uso de tokens.
    
    Args:
        token_usage: Dicionário com prompt_tokens, completion_tokens, total_tokens
        model: Nome do modelo
    
    Returns:
        Custo em dólares
    """
    if model not in MODEL_PRICING:
        return 0.0
    
    pricing = MODEL_PRICING[model]
    input_cost = (token_usage["prompt_tokens"] / 1_000_000) * pricing["input"]
    output_cost = (token_usage["completion_tokens"] / 1_000_000) * pricing["output"]
    
    return input_cost + output_cost


def main():
    """Função principal."""
    args = parse_args()
    
    if not args["input_file"]:
        print("Uso: python src/script_openai.py <arquivo_json> [idioma] [arquivo_saida] [opções]")
        print("\nOpções:")
        print("  --dry              Modo dry-run (não escreve arquivo)")
        print("  --batch N          Tamanho do batch (padrão: 100, recomendado: 100-200)")
        print("  --parallel N       Batches paralelos (padrão: 3, recomendado: 3-5)")
        print("  --model MODEL      Modelo OpenAI (padrão: gpt-4o-mini)")
        print("  --verbose, -v      Logs detalhados (padrão: resumido)")
        print("\nExemplos:")
        print("  python src/script_openai.py en.json pt")
        print("  python src/script_openai.py en.json pt --dry")
        print("  python src/script_openai.py en.json pt pt.json --batch 5")
        sys.exit(1)
    
    input_path = Path(args["input_file"])
    if not input_path.exists():
        print(f"ERRO: Arquivo '{args['input_file']}' não encontrado!")
        sys.exit(1)
    
    # Define arquivos
    if args["output_file"]:
        output_path = Path(args["output_file"])
    else:
        output_path = input_path.parent / f"{input_path.stem}_{args['target_language']}{input_path.suffix}"
    
    cache_file = input_path.parent / f".translate_cache_{args['target_language']}.json"
    backup_file = output_path.with_suffix(output_path.suffix + ".bak")
    
    print("=" * 70)
    print("🤖 TRADUTOR JSON - OPENAI API")
    print("=" * 70)
    print(f"📁 Arquivo de entrada: {input_path}")
    print(f"📁 Arquivo de saída: {output_path}")
    print(f"🌍 Idioma destino: {args['target_language']}")
    print(f"🤖 Modelo: {args['model']}")
    if args['model'] in MODEL_PRICING:
        pricing = MODEL_PRICING[args['model']]
        print(f"💰 Preços: ${pricing['input']}/1M input | ${pricing['output']}/1M output")
    print("=" * 70)
    
    print(f"\n📖 Lendo arquivo: {input_path}")
    
    # Lê arquivo de entrada
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
    except Exception as e:
        print(f"ERRO ao ler arquivo: {e}")
        sys.exit(1)
    
    # Lê arquivo de saída existente (se houver)
    existing_data = {}
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"Arquivo {output_path} existente carregado (preservará traduções manuais)")
        except Exception as e:
            print(f"Aviso: Não foi possível ler arquivo existente: {e}")
    
    # Carrega cache
    cache = {}
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            print(f"✓ Cache carregado: {len(cache)} traduções em cache")
        except Exception as e:
            print(f"⚠️  Não foi possível carregar cache: {e}")
    else:
        print("ℹ️  Nenhum cache encontrado (primeira execução)")
    
    # Achata objetos
    print("\n📊 Analisando estrutura do JSON...")
    flat_base = flatten_object(base_data)
    flat_existing = {e["key"]: e["value"] for e in flatten_object(existing_data)}
    
    # Filtra strings para traduzir
    to_translate = [
        e for e in flat_base
        if isinstance(e["value"], str) and e["value"].strip() and
        (e["key"] not in flat_existing or flat_existing[e["key"]] == e["value"])
    ]
    
    # Conta quantas estão em cache
    cached_count = sum(1 for e in to_translate if e["value"] in cache)
    to_translate_count = len(to_translate) - cached_count
    
    print(f"✓ Análise concluída!")
    print(f"  • Total de entradas: {len(flat_base)}")
    print(f"  • Strings para traduzir: {len(to_translate)}")
    print(f"  • Já em cache: {cached_count}")
    print(f"  • Precisam tradução: {to_translate_count}")
    print(f"  • Tamanho do batch: {args['batch_size']}")
    if args["parallel"] > 1:
        estimated_batches = (to_translate_count + args["batch_size"] - 1) // args["batch_size"] if to_translate_count > 0 else 0
        print(f"  • Batches paralelos: {args['parallel']}")
        print(f"  • Total de batches: ~{estimated_batches}")
    
    if to_translate_count == 0:
        print("\n✅ Todas as strings já estão traduzidas no cache!")
        if not args["dry_run"]:
            print("   Se quiser retraduzir, delete o arquivo de cache.")
    
    if args["dry_run"]:
        print("\n" + "=" * 70)
        print("🧪 MODO DRY-RUN (não salvará arquivo)")
        print("=" * 70)
    
    # Inicializa estatísticas
    import time
    start_time = time.time()
    stats = {
        "translated": 0,
        "cached": 0,
        "errors": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_tokens": 0,
        "api_calls": 0
    }
    
    # Processa em batches com paralelização
    print("\n" + "=" * 70)
    print("🔄 INICIANDO TRADUÇÃO...")
    if args["parallel"] > 1:
        print(f"⚡ Paralelização: {args['parallel']} batches simultâneos")
    print("=" * 70)
    
    translated_entries = []
    num_batches = (to_translate_count + args["batch_size"] - 1) // args["batch_size"] if to_translate_count > 0 else 0
    
    # Prepara todos os batches
    all_batches = []
    for i in range(0, len(to_translate), args["batch_size"]):
        batch = to_translate[i:i + args["batch_size"]]
        batch_num = i // args["batch_size"] + 1
        all_batches.append((batch, batch_num))
    
    # Função async para processar batches com paralelização
    async def process_batches_parallel():
        nonlocal translated_entries
        lock = asyncio.Lock()
        semaphore = asyncio.Semaphore(args["parallel"])
        
        async def process_single_batch(batch_data):
            batch, batch_num = batch_data
            async with semaphore:  # Limita paralelismo
                results = await translate_batch_async(
                    batch, cache, args["target_language"], args["model"],
                    stats, batch_num, num_batches, args["verbose"], lock
                )
                
                # Atualiza progresso
                processed = stats['translated'] + stats['cached']
                elapsed = time.time() - start_time
                progress_pct = (processed / len(to_translate) * 100) if len(to_translate) > 0 else 0
                
                # Calcula custo acumulado
                current_cost = 0.0
                if args['model'] in MODEL_PRICING and stats["api_calls"] > 0:
                    pricing = MODEL_PRICING[args['model']]
                    input_cost = (stats["total_prompt_tokens"] / 1_000_000) * pricing["input"]
                    output_cost = (stats["total_completion_tokens"] / 1_000_000) * pricing["output"]
                    current_cost = input_cost + output_cost
                
                # Calcula ETA (usa stats["api_calls"] como proxy para batches completos)
                eta_str = "calculando..."
                estimated_total_cost = 0.0
                if stats["api_calls"] > 0 and processed > 0:
                    completed_batches = stats["api_calls"]  # Cada chamada = 1 batch
                    if completed_batches > 0:
                        avg_time_per_batch = elapsed / completed_batches
                        remaining_batches = num_batches - completed_batches
                        eta_seconds = int(avg_time_per_batch * remaining_batches)
                        
                        if eta_seconds < 60:
                            eta_str = f"{eta_seconds}s"
                        elif eta_seconds < 3600:
                            eta_min = eta_seconds // 60
                            eta_sec = eta_seconds % 60
                            eta_str = f"{eta_min}m {eta_sec}s"
                        else:
                            eta_hour = eta_seconds // 3600
                            eta_min = (eta_seconds % 3600) // 60
                            eta_str = f"{eta_hour}h {eta_min}m"
                        
                        # Estima custo total
                        if current_cost > 0 and completed_batches > 0:
                            cost_per_batch = current_cost / completed_batches
                            estimated_total_cost = cost_per_batch * num_batches
                
                # Log de progresso
                if not args["verbose"]:
                    elapsed_min = int(elapsed // 60)
                    elapsed_sec = int(elapsed % 60)
                    elapsed_str = f"{elapsed_min}m {elapsed_sec}s" if elapsed_min > 0 else f"{elapsed_sec}s"
                    
                    cost_str = f"${current_cost:.6f}"
                    if estimated_total_cost > 0:
                        cost_str += f" (est. ${estimated_total_cost:.6f})"
                    
                    print(f"\r🔄 Batch {batch_num}/{num_batches} | "
                          f"Progresso: {processed}/{len(to_translate)} ({progress_pct:.1f}%) | "
                          f"Tempo: {elapsed_str} | ETA: {eta_str} | "
                          f"Custo: {cost_str}", end="", flush=True)
                
                # Salva cache periodicamente
                if not args["dry_run"] and batch_num % 5 == 0:  # A cada 5 batches
                    async with lock:
                        try:
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                json.dump(cache, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                
                return results
        
        # Processa todos os batches em paralelo
        tasks = [process_single_batch(batch_data) for batch_data in all_batches]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Coleta resultados
        for result in all_results:
            if isinstance(result, Exception):
                if args["verbose"]:
                    print(f"\n❌ Erro no batch: {result}")
                continue
            for r in result:
                translated_entries.append({
                    "key": r["key"],
                    "value": r["translated"]
                })
    
    # Executa processamento assíncrono
    if args["parallel"] > 1:
        asyncio.run(process_batches_parallel())
    else:
        # Modo sequencial (fallback)
        for batch, batch_num in all_batches:
            if args["verbose"]:
                print(f"\n{'='*70}")
                print(f"📦 BATCH {batch_num}/{num_batches} (tamanho: {len(batch)})")
                print(f"{'='*70}")
            
            results = asyncio.run(translate_batch_async(
                batch, cache, args["target_language"], args["model"],
                stats, batch_num, num_batches, args["verbose"], None
            ))
            
            for r in results:
                translated_entries.append({
                    "key": r["key"],
                    "value": r["translated"]
                })
            
            # Salva cache incrementalmente
            if not args["dry_run"]:
                try:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"⚠️  Erro ao salvar cache: {e}")
            
            # Log de progresso
            processed = stats['translated'] + stats['cached']
            elapsed = time.time() - start_time
            progress_pct = (processed / len(to_translate) * 100) if len(to_translate) > 0 else 0
            
            current_cost = 0.0
            if args['model'] in MODEL_PRICING and stats["api_calls"] > 0:
                pricing = MODEL_PRICING[args['model']]
                input_cost = (stats["total_prompt_tokens"] / 1_000_000) * pricing["input"]
                output_cost = (stats["total_completion_tokens"] / 1_000_000) * pricing["output"]
                current_cost = input_cost + output_cost
            
            eta_str = "calculando..."
            estimated_total_cost = 0.0
            if stats["api_calls"] > 0 and processed > 0 and batch_num > 0:
                avg_time_per_batch = elapsed / batch_num
                remaining_batches = num_batches - batch_num
                eta_seconds = int(avg_time_per_batch * remaining_batches)
                
                if current_cost > 0:
                    cost_per_batch = current_cost / batch_num
                    estimated_total_cost = cost_per_batch * num_batches
                
                if eta_seconds < 60:
                    eta_str = f"{eta_seconds}s"
                elif eta_seconds < 3600:
                    eta_min = eta_seconds // 60
                    eta_sec = eta_seconds % 60
                    eta_str = f"{eta_min}m {eta_sec}s"
                else:
                    eta_hour = eta_seconds // 3600
                    eta_min = (eta_seconds % 3600) // 60
                    eta_str = f"{eta_hour}h {eta_min}m"
            
            if not args["verbose"]:
                elapsed_min = int(elapsed // 60)
                elapsed_sec = int(elapsed % 60)
                elapsed_str = f"{elapsed_min}m {elapsed_sec}s" if elapsed_min > 0 else f"{elapsed_sec}s"
                
                cost_str = f"${current_cost:.6f}"
                if estimated_total_cost > 0:
                    cost_str += f" (est. ${estimated_total_cost:.6f})"
                
                print(f"\r🔄 Batch {batch_num}/{num_batches} | "
                      f"Progresso: {processed}/{len(to_translate)} ({progress_pct:.1f}%) | "
                      f"Tempo: {elapsed_str} | ETA: {eta_str} | "
                      f"Custo: {cost_str}", end="", flush=True)
    
    # Limpa linha de progresso
    if not args["verbose"]:
        print("\r" + " " * 100 + "\r", end="")
    
    # Salva cache final
    if not args["dry_run"]:
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Erro ao salvar cache final: {e}")
    
    # Calcula custos totais
    total_time = time.time() - start_time
    total_cost = 0.0
    input_cost = 0.0
    output_cost = 0.0
    
    if args['model'] in MODEL_PRICING:
        pricing = MODEL_PRICING[args['model']]
        input_cost = (stats["total_prompt_tokens"] / 1_000_000) * pricing["input"]
        output_cost = (stats["total_completion_tokens"] / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
    
    # Mescla traduções preservando ordem original
    print("\n" + "=" * 70)
    print("🔨 RECONSTRUINDO ESTRUTURA JSON...")
    print("=" * 70)
    
    # Cria dicionário com todas as traduções geradas
    translated_dict = {e["key"]: e["value"] for e in translated_entries}
    
    # Mescla com traduções existentes (prioriza traduções manuais do arquivo existente)
    # flat_existing contém chaves achatadas do arquivo de saída existente
    for key, existing_value in flat_existing.items():
        # Encontra o valor original correspondente
        original_entry = next((e for e in flat_base if e["key"] == key), None)
        if original_entry:
            original_value = original_entry["value"]
            # Se a tradução existente é diferente do original, preserva ela
            if existing_value != original_value:
                translated_dict[key] = existing_value
    
    # Reconstrói JSON preservando ordem original das chaves
    output_data = reconstruct_json_preserving_order(base_data, translated_dict)
    print("✓ Estrutura reconstruída!")
    
    # Backup
    if output_path.exists() and not args["dry_run"]:
        shutil.copy2(output_path, backup_file)
        print(f"✓ Backup criado: {backup_file}")
    
    # Estatísticas finais
    print("\n" + "=" * 70)
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 70)
    print(f"✅ Strings traduzidas: {stats['translated']}")
    print(f"💾 Strings do cache: {stats['cached']}")
    print(f"❌ Erros: {stats['errors']}")
    print(f"📞 Chamadas à API: {stats['api_calls']}")
    print(f"⏱️  Tempo total: {int(total_time // 60)}m {int(total_time % 60)}s")
    
    if stats["api_calls"] > 0:
        print(f"\n📈 USO DE TOKENS:")
        print(f"  • Prompt tokens: {stats['total_prompt_tokens']:,}")
        print(f"  • Completion tokens: {stats['total_completion_tokens']:,}")
        print(f"  • Total tokens: {stats['total_tokens']:,}")
        print(f"  • Média por chamada: {stats['total_tokens'] // stats['api_calls']:,} tokens")
        
        if total_cost > 0:
            print(f"\n💰 CUSTOS:")
            print(f"  • Custo input: ${input_cost:.6f}")
            print(f"  • Custo output: ${output_cost:.6f}")
            print(f"  • CUSTO TOTAL: ${total_cost:.6f}")
            if stats['translated'] > 0:
                print(f"  • Custo por string: ${total_cost / stats['translated']:.6f}")
    
    # Dry-run: apenas mostra exemplos
    if args["dry_run"]:
        print("\n" + "=" * 70)
        print("🧪 DRY-RUN: Exemplos de traduções")
        print("=" * 70)
        # Mostra exemplos das traduções
        example_keys = list(translated_dict.keys())[:15]
        for key in example_keys:
            value = translated_dict[key]
            value_preview = value[:60] + "..." if len(value) > 60 else value
            print(f"  {key} => {value_preview}")
        print(f"\nTotal: {len(translated_dict)} traduções processadas")
        print("Execute sem --dry para salvar o arquivo")
        return
    
    # Salva arquivo
    print(f"\n💾 Salvando arquivo traduzido: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"✓ Arquivo salvo com sucesso!")
        print(f"  • Tamanho: {file_size:.1f} KB")
        print(f"  • Localização: {output_path.absolute()}")
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("🎉 PROCESSO FINALIZADO COM SUCESSO!")
    print("=" * 70)
    if total_cost > 0:
        print(f"💰 Custo total da tradução: ${total_cost:.6f}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


