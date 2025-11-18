#!/usr/bin/env python3


import json
import sys
import os
import re
import shutil
import asyncio
import time
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


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("ERRO: OPENAI_API_KEY não encontrada no arquivo .env")
    print("Crie um arquivo .env com: OPENAI_API_KEY=sk-...")
    sys.exit(1)


client = OpenAI(api_key=OPENAI_API_KEY)


DEFAULT_BATCH_SIZE = 50
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_PARALLEL = 3

DEFAULT_ON_FAILURE = "NEEDS_MANUAL_REVIEW"


MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}


def parse_args() -> Dict[str, Any]:
    
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
    
    entries = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                entries.extend(flatten_object(value, full_key))
            else:

                entries.append({"key": full_key, "value": value})
    elif isinstance(obj, list):

        for i, item in enumerate(obj):
            item_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
            if isinstance(item, dict):
                entries.extend(flatten_object(item, item_key))
            else:
                entries.append({"key": item_key, "value": item})
    
    return entries


def reconstruct_json_preserving_order(
    original_obj: Any,
    translated_dict: Dict[str, str],
    path: str = ""
) -> Any:
    
    if isinstance(original_obj, dict):
        result = {}
        for key, value in original_obj.items():
            full_key = f"{path}.{key}" if path else key
            
            if isinstance(value, dict):

                result[key] = reconstruct_json_preserving_order(
                    value, translated_dict, full_key
                )
            elif isinstance(value, list):

                result[key] = [
                    reconstruct_json_preserving_order(
                        item, translated_dict, f"{full_key}[{i}]"
                    )
                    for i, item in enumerate(value)
                ]
            else:

                if full_key in translated_dict:
                    result[key] = translated_dict[full_key]
                else:
                    result[key] = value
        
        return result
    
    elif isinstance(original_obj, list):

        return [
            reconstruct_json_preserving_order(
                item, translated_dict, f"{path}[{i}]" if path else f"[{i}]"
            )
            for i, item in enumerate(original_obj)
        ]
    
    else:

        if path in translated_dict:
            return translated_dict[path]
        return original_obj


def mask_placeholders(text: str) -> Tuple[str, List[Dict[str, str]]]:
    
    patterns = [
        (re.compile(r'\{\{\s*[\w\.\-]+\s*\}\}'), "__PH_GG__"),
        (re.compile(r'\{\s*[\w\.\-]+\s*\}'), "__PH_ICU__"),
        (re.compile(r'%[sd]'), "__PH_PRINTF__"),
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
    
    if not placeholder_map:
        return text
    
    result = text
    

    max_iterations = 5
    iteration = 0
    while "__PH_" in result and iteration < max_iterations:

        for item in reversed(placeholder_map):
            token = item["token"]
            original = item["original"]
            if token in result:
                result = result.replace(token, original)
        iteration += 1
    
    return result


def call_openai_single_key(
    key: str,
    value: str,
    model: str = DEFAULT_MODEL,
    target_lang: str = "pt",
    stats: Optional[Dict] = None
) -> Tuple[str, Dict[str, int]]:
    

    single_item_dict = {key: value}
    translated_dict, token_usage = call_openai_batch_json(
        single_item_dict, model, target_lang, stats
    )
    

    translated_value = translated_dict.get(key, "")
    return translated_value, token_usage


def call_openai_batch_json(
    items_dict: Dict[str, str], 
    model: str = DEFAULT_MODEL, 
    target_lang: str = "pt",
    stats: Optional[Dict] = None
) -> Tuple[Dict[str, str], Dict[str, int]]:
    
    lang_names = {
        "es": "Spanish", "pt": "Brazilian Portuguese", "fr": "French", "de": "German",
        "it": "Italian", "nl": "Dutch", "pl": "Polish", "sv": "Swedish",
        "da": "Danish", "no": "Norwegian", "fi": "Finnish", "cs": "Czech",
        "hu": "Hungarian", "ro": "Romanian", "hr": "Croatian", "sr": "Serbian (Latinized)",
        "tr": "Turkish", "id": "Indonesian", "tl": "Filipino (Tagalog)", "ms": "Malay",
    }
    
    target_lang_name = lang_names.get(target_lang, target_lang)
    

    input_json_str = json.dumps(items_dict, indent=2, ensure_ascii=False, sort_keys=False)
    

    has_placeholders = any("__PH_" in text for text in items_dict.values())
    placeholder_instruction = ""
    if has_placeholders:
        placeholder_instruction = (
            "\n\nCRITICAL INSTRUCTION: The JSON values contain placeholder tokens "
            "(like __PH_GG__0__, __PH_ICU__1__, __PH_PRINTF__0__). "
            "These tokens are PLACEHOLDER MARKERS, NOT text to translate. "
            "You MUST preserve these tokens EXACTLY as they are - do NOT translate them, modify them, or remove them. "
            "Keep them in the exact same positions in your translation. "
            "Only translate the actual words and sentences, leaving all __PH_*__ tokens completely unchanged."
        )
    
    system_prompt = (
        f"You are a professional JSON translator. Your task is to translate the text **values** in the provided JSON object into {target_lang_name}. "
        "You MUST return a valid JSON object. "
        "CRITICAL: The **keys** of the returned JSON object MUST be *exactly* the same as the keys in the input JSON object. "
        "You MUST return ALL keys that were in the input. Do NOT add new keys. Do NOT remove keys. Do NOT translate the keys. "
        "Only translate the string values. "
        "CRITICAL: Preserve ALL punctuation, spacing, and formatting exactly as in the original. "
        "If a value starts with a comma, space, or other punctuation (like \", your \"), you MUST preserve it exactly in the same position. "
        "If a value ends with punctuation or spacing, preserve it. Do NOT remove or modify punctuation marks. "
        "Preserve original placeholders like {{name}} or {count} exactly as-is."
        f"{placeholder_instruction}"
    )
    
    user_prompt = (
        f"Translate the values of the following JSON object into {target_lang_name}. "
        "Return a valid JSON object with the exact same keys.\n\n"
        "CRITICAL RULES:\n"
        "1. The **keys** in your response MUST be EXACTLY the same as the keys in the input JSON.\n"
        "2. Each key must have its corresponding translated value - do NOT mix values between keys.\n"
        "3. Preserve the exact key names, including dots (.) in nested keys like 'Onboarding.welcomeModal.title'.\n"
        "4. The dot (.) character is part of the key name and MUST be preserved.\n"
        "5. Do NOT modify, escape, or change any key names.\n"
        "6. Return ALL keys that were in the input - one key, one value, in the same order.\n"
        "7. If a value is short (like \", your \" or \"on\"), translate it but keep the same structure.\n\n"
        f"Input JSON:\n{input_json_str}\n\n"
        "Remember: Each key maps to ONE value. Do not mix them up."
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=8000,
            response_format={"type": "json_object"}
        )
        

        usage = response.usage
        token_usage = {
            "prompt_tokens": usage.prompt_tokens if hasattr(usage, 'prompt_tokens') else usage.input_tokens,
            "completion_tokens": usage.completion_tokens if hasattr(usage, 'completion_tokens') else usage.output_tokens,
            "total_tokens": usage.total_tokens
        }
        

        if stats:
            stats["total_prompt_tokens"] = stats.get("total_prompt_tokens", 0) + token_usage["prompt_tokens"]
            stats["total_completion_tokens"] = stats.get("total_completion_tokens", 0) + token_usage["completion_tokens"]
            stats["total_tokens"] = stats.get("total_tokens", 0) + token_usage["total_tokens"]
            stats["api_calls"] = stats.get("api_calls", 0) + 1
        

        translated_json_str = response.choices[0].message.content
        
        try:
            translated_dict = json.loads(translated_json_str)
            if not isinstance(translated_dict, dict):
                raise ValueError("API did not return a dictionary.")
            

            input_keys = set(items_dict.keys())
            output_keys = set(translated_dict.keys())
            missing_keys = input_keys - output_keys
            extra_keys = output_keys - input_keys
            
            if missing_keys:
                print(f"\n⚠️  AVISO: A IA não retornou {len(missing_keys)} chaves:")
                for key in list(missing_keys)[:10]:
                    print(f"     - {key}")
                if len(missing_keys) > 10:
                    print(f"     ... e mais {len(missing_keys) - 10} chaves")

                for key in missing_keys:
                    translated_dict[key] = ""
            
            if extra_keys:
                print(f"\n⚠️  AVISO: A IA retornou {len(extra_keys)} chaves extras:")
                for key in list(extra_keys)[:10]:
                    print(f"     + {key}")
                if len(extra_keys) > 10:
                    print(f"     ... e mais {len(extra_keys) - 10} chaves")

                for key in extra_keys:
                    del translated_dict[key]
            

            deep_keys = [k for k in input_keys if k.count('.') > 2]
            if deep_keys and missing_keys:
                print(f"\n⚠️  AVISO: {len(deep_keys)} chaves aninhadas profundas detectadas. Verifique se todas foram retornadas.")
            
        except json.JSONDecodeError as e:
            print(f"\n❌ Erro ao decodificar JSON da API: {e}")
            print(f"   Resposta recebida: {translated_json_str[:500]}...")

            return {}, token_usage

        return translated_dict, token_usage
    
    except Exception as e:
        print(f"\n❌ Erro ao chamar OpenAI API: {e}")

        return {}, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


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
    
    results = []
    

    items_to_translate_map = {}
    items_for_individual_translation = []
    
    for item in items:
        original = str(item["value"])
        key = item["key"]
        

        if original in cache:
            cached_translation = cache[original]
            if "__PH_" in cached_translation:
                if verbose: print(f"  ⚠️  Cache corrompido para '{key}', retraduzindo...")
                del cache[original]
            else:
                stats["cached"] = stats.get("cached", 0) + 1
                results.append({ "key": key, "translated": cached_translation, "fromCache": True })
                continue
        

        masked, placeholder_map = mask_placeholders(original)
        

        is_nested_object = key.count('.') >= 2
        is_short_string = len(original) <= 20
        has_edge_punctuation = original.strip() != original
        

        should_translate_individually = (
            is_nested_object or
            (is_short_string and has_edge_punctuation) or
            (is_short_string and key.count('.') >= 1)
        )
        
        if should_translate_individually:
            items_for_individual_translation.append({
                "key": key,
                "original": original,
                "masked": masked,
                "placeholder_map": placeholder_map
            })
        else:
            items_to_translate_map[key] = {
                "original": original,
                "masked": masked,
                "placeholder_map": placeholder_map
            }
    

    for item_data in items_for_individual_translation:
        try:
            local_stats = {}
            translated_masked, token_usage = await asyncio.to_thread(
                call_openai_single_key, item_data["key"], item_data["masked"], model, target_lang, local_stats
            )
            

            if lock and stats:
                async with lock:
                    stats["total_prompt_tokens"] = stats.get("total_prompt_tokens", 0) + token_usage["prompt_tokens"]
                    stats["total_completion_tokens"] = stats.get("total_completion_tokens", 0) + token_usage["completion_tokens"]
                    stats["total_tokens"] = stats.get("total_tokens", 0) + token_usage["total_tokens"]
                    stats["api_calls"] = stats.get("api_calls", 0) + 1
            
            if translated_masked and len(translated_masked) > 0:
                translated = restore_placeholders(translated_masked, item_data["placeholder_map"])
                

                if "__PH_" in translated:
                    for ph_item in item_data["placeholder_map"]:
                        translated = translated.replace(ph_item["token"], ph_item["original"])
                    if "__PH_" in translated:
                        if verbose:
                            print(f"  ⚠️  Placeholders não restaurados em '{item_data['key']}'")
                        stats["errors"] = stats.get("errors", 0) + 1
                        results.append({
                            "key": item_data["key"],
                            "translated": DEFAULT_ON_FAILURE,
                            "fromCache": False
                        })
                        continue
                

                if lock:
                    async with lock:
                        cache[item_data["original"]] = translated
                        stats["translated"] = stats.get("translated", 0) + 1
                else:
                    cache[item_data["original"]] = translated
                    stats["translated"] = stats.get("translated", 0) + 1
                
                results.append({
                    "key": item_data["key"],
                    "translated": translated,
                    "fromCache": False
                })
            else:
                stats["errors"] = stats.get("errors", 0) + 1
                results.append({
                    "key": item_data["key"],
                    "translated": DEFAULT_ON_FAILURE,
                    "fromCache": False
                })
        except Exception as e:
            if verbose:
                print(f"  ❌ Erro ao traduzir individualmente '{item_data['key']}': {e}")
            stats["errors"] = stats.get("errors", 0) + 1
            results.append({
                "key": item_data["key"],
                "translated": DEFAULT_ON_FAILURE,
                "fromCache": False
            })
    

    if not items_to_translate_map:
        return results
    

    input_json_dict = {
        key: data["masked"] for key, data in items_to_translate_map.items()
    }
    

    if len(input_json_dict) != len(items_to_translate_map):
        if verbose:
            print(f"  ⚠️  AVISO: Número de chaves no input_json_dict ({len(input_json_dict)}) diferente do esperado ({len(items_to_translate_map)})")
    

    if verbose:
        print(f"  📤 Enviando {len(input_json_dict)} chaves para tradução:")
        for i, key in enumerate(list(input_json_dict.keys())[:5]):
            print(f"     {i+1}. {key}")
        if len(input_json_dict) > 5:
            print(f"     ... e mais {len(input_json_dict) - 5} chaves")
    

    try:
        local_stats = {}
        
        translated_dict, token_usage = await asyncio.to_thread(
            call_openai_batch_json, input_json_dict, model, target_lang, local_stats
        )
        

        if verbose:
            print(f"  📥 Recebidas {len(translated_dict)} chaves da API:")
            for i, key in enumerate(list(translated_dict.keys())[:5]):
                print(f"     {i+1}. {key}")
            if len(translated_dict) > 5:
                print(f"     ... e mais {len(translated_dict) - 5} chaves")
        

        if lock and stats:
            async with lock:
                stats["total_prompt_tokens"] = stats.get("total_prompt_tokens", 0) + token_usage["prompt_tokens"]
                stats["total_completion_tokens"] = stats.get("total_completion_tokens", 0) + token_usage["completion_tokens"]
                stats["total_tokens"] = stats.get("total_tokens", 0) + token_usage["total_tokens"]
                stats["api_calls"] = stats.get("api_calls", 0) + 1
        

        for key, item_data in items_to_translate_map.items():
            original = item_data["original"]
            placeholder_map = item_data["placeholder_map"]
            

            translated_masked = translated_dict.get(key)
            

            if not translated_masked or len(translated_masked) == 0:
                if verbose: 
                    print(f"  ⚠️  Chave '{key}' não encontrada na resposta do batch, traduzindo individualmente...")
                

                try:
                    local_stats = {}
                    translated_masked, retry_tokens = await asyncio.to_thread(
                        call_openai_single_key, key, item_data["masked"], model, target_lang, local_stats
                    )
                    

                    if lock and stats:
                        async with lock:
                            stats["total_prompt_tokens"] = stats.get("total_prompt_tokens", 0) + retry_tokens["prompt_tokens"]
                            stats["total_completion_tokens"] = stats.get("total_completion_tokens", 0) + retry_tokens["completion_tokens"]
                            stats["total_tokens"] = stats.get("total_tokens", 0) + retry_tokens["total_tokens"]
                            stats["api_calls"] = stats.get("api_calls", 0) + 1
                    
                    if not translated_masked or len(translated_masked) == 0:
                        if verbose:
                            print(f"  ❌ Falha ao traduzir individualmente '{key}'")
                        stats["errors"] = stats.get("errors", 0) + 1
                        results.append({
                            "key": key,
                            "translated": DEFAULT_ON_FAILURE,
                            "fromCache": False
                        })
                        continue
                except Exception as e:
                    if verbose:
                        print(f"  ❌ Erro ao traduzir individualmente '{key}': {e}")
                    stats["errors"] = stats.get("errors", 0) + 1
                    results.append({
                        "key": key,
                        "translated": DEFAULT_ON_FAILURE,
                        "fromCache": False
                    })
                    continue


            translated = restore_placeholders(translated_masked, placeholder_map)
            

            original_len = len(original)
            translated_len = len(translated)
            if translated_len > original_len * 3 and original_len > 0:
                if verbose:
                    print(f"  ⚠️  VALOR CONCATENADO DETECTADO em '{key}':")
                    print(f"      Original ({original_len} chars): {original[:50]}...")
                    print(f"      Traduzido ({translated_len} chars): {translated[:100]}...")
                    print(f"      Retraduzindo individualmente...")
                

                try:
                    retry_masked, retry_tokens = await asyncio.to_thread(
                        call_openai_single_key, key, item_data["masked"], model, target_lang, {}
                    )
                    
                    if retry_masked and len(retry_masked) > 0:
                        retry_translated = restore_placeholders(retry_masked, placeholder_map)
                        

                        retry_len = len(retry_translated)
                        if retry_len <= original_len * 2.5:
                            translated = retry_translated
                            if lock and stats:
                                async with lock:
                                    stats["total_prompt_tokens"] = stats.get("total_prompt_tokens", 0) + retry_tokens["prompt_tokens"]
                                    stats["total_completion_tokens"] = stats.get("total_completion_tokens", 0) + retry_tokens["completion_tokens"]
                                    stats["total_tokens"] = stats.get("total_tokens", 0) + retry_tokens["total_tokens"]
                                    stats["api_calls"] = stats.get("api_calls", 0) + 1
                        else:
                            if verbose:
                                print(f"  ❌ Retry ainda retornou valor muito grande, marcando como falha")
                            stats["errors"] = stats.get("errors", 0) + 1
                            results.append({
                                "key": key,
                                "translated": DEFAULT_ON_FAILURE,
                                "fromCache": False
                            })
                            continue
                    else:
                        if verbose:
                            print(f"  ❌ Retry retornou vazio, marcando como falha")
                        stats["errors"] = stats.get("errors", 0) + 1
                        results.append({
                            "key": key,
                            "translated": DEFAULT_ON_FAILURE,
                            "fromCache": False
                        })
                        continue
                except Exception as e:
                    if verbose:
                        print(f"  ❌ Erro no retry de '{key}': {e}")
                    stats["errors"] = stats.get("errors", 0) + 1
                    results.append({
                        "key": key,
                        "translated": DEFAULT_ON_FAILURE,
                        "fromCache": False
                    })
                    continue
            

            if "__PH_" in translated:

                for ph_item in placeholder_map:
                    token = ph_item["token"]
                    original_ph = ph_item["original"]

                    translated = translated.replace(token, original_ph)
                

                if "__PH_" in translated:
                    if verbose: 
                        print(f"  ⚠️  Placeholders não restaurados em '{key}': {translated[:100]}")
                    stats["errors"] = stats.get("errors", 0) + 1
                    results.append({
                        "key": key,
                        "translated": DEFAULT_ON_FAILURE,
                        "fromCache": False
                    })
                    continue
            

            if lock:
                async with lock:
                    cache[original] = translated
                    stats["translated"] = stats.get("translated", 0) + 1
            else:
                cache[original] = translated
                stats["translated"] = stats.get("translated", 0) + 1
            
            results.append({
                "key": key,
                "translated": translated,
                "fromCache": False
            })


        if verbose:
            cost = calculate_cost(token_usage, model)
            print(f"  📊 Batch {batch_num}: {len(input_json_dict)} strings | "
                  f"Tokens: {token_usage['total_tokens']:,} | Custo: ${cost:.6f}")
        
    except Exception as e:
        if verbose:
            print(f"  ❌ Erro GERAL no batch {batch_num}: {e}")

        num_items = len(items_to_translate_map)
        stats["errors"] = stats.get("errors", 0) + num_items
        for key in items_to_translate_map.keys():
            results.append({
                "key": key,
                "translated": DEFAULT_ON_FAILURE,
                "fromCache": False
            })
    
    return results


def calculate_cost(token_usage: Dict[str, int], model: str) -> float:
    
    if model not in MODEL_PRICING:
        return 0.0
    
    pricing = MODEL_PRICING[model]
    input_cost = (token_usage.get("prompt_tokens", 0) / 1_000_000) * pricing["input"]
    output_cost = (token_usage.get("completion_tokens", 0) / 1_000_000) * pricing["output"]
    
    return input_cost + output_cost


def main():
    
    args = parse_args()
    
    if not args["input_file"]:
        print("Uso: python src/script_openai.py <arquivo_json> [idioma] [arquivo_saida] [opções]")
        print("\nOpções:")
        print("  --dry              Modo dry-run (não escreve arquivo)")
        print("  --batch N          Tamanho do batch (padrão: 50, recomendado: 50-100)")
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
    

    if args["output_file"]:
        output_path = Path(args["output_file"])
    else:
        output_path = input_path.parent / f"{input_path.stem}_{args['target_language']}{input_path.suffix}"
    
    cache_file = input_path.parent / f".translate_cache_{args['target_language']}.json"
    backup_file = output_path.with_suffix(output_path.suffix + ".bak")
    
    print("=" * 70)
    print("🤖 TRADUTOR JSON (Modo JSON Otimizado) - OPENAI API")
    print("=" * 70)
    print(f"📁 Arquivo de entrada: {input_path}")
    print(f"📁 Arquivo de saída: {output_path}")
    print(f"🌍 Idioma destino: {args['target_language']}")
    print(f"🤖 Modelo: {args['model']}")
    if args['model'] in MODEL_PRICING:
        pricing = MODEL_PRICING[args['model']]
        print(f"💰 Preços: ${pricing['input']}/1M input | ${pricing['output']}/1M output")
    print(f"⚠️  Valor em caso de falha: '{DEFAULT_ON_FAILURE}'")
    print("=" * 70)
    
    print(f"\n📖 Lendo arquivo: {input_path}")
    

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
    except Exception as e:
        print(f"ERRO ao ler arquivo: {e}")
        sys.exit(1)
    

    existing_data = {}
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"✓ Arquivo {output_path} existente carregado (preservará traduções manuais)")
        except Exception as e:
            print(f"Aviso: Não foi possível ler arquivo existente: {e}")
    

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
    

    print("\n📊 Analisando estrutura do JSON...")
    flat_base = flatten_object(base_data)
    flat_existing = {e["key"]: e["value"] for e in flatten_object(existing_data)}
    

    to_translate = []
    for e in flat_base:
        if isinstance(e["value"], str) and len(e["value"]) > 0:
            key = e["key"]
            existing_val = flat_existing.get(key)
            
            if (key not in flat_existing or 
                existing_val == e["value"] or 
                existing_val == DEFAULT_ON_FAILURE):
                to_translate.append(e)


    cached_count = sum(1 for e in to_translate if e["value"] in cache)
    to_translate_count = len(to_translate) - cached_count
    
    print(f"✓ Análise concluída!")
    print(f"  • Total de entradas: {len(flat_base)}")
    print(f"  • Strings para traduzir (novas/modificadas): {len(to_translate)}")
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
    

    print("\n" + "=" * 70)
    print("🔄 INICIANDO TRADUÇÃO...")
    if args["parallel"] > 1:
        print(f"⚡ Paralelização: {args['parallel']} batches simultâneos")
    print("=" * 70)
    
    translated_entries = []
    

    items_requiring_api_call = [e for e in to_translate if e["value"] not in cache]
    num_batches = (len(items_requiring_api_call) + args["batch_size"] - 1) // args["batch_size"] if items_requiring_api_call else 0
    

    all_batches = []
    for i in range(0, len(items_requiring_api_call), args["batch_size"]):
        batch = items_requiring_api_call[i:i + args["batch_size"]]
        batch_num = i // args["batch_size"] + 1
        all_batches.append((batch, batch_num))
    

    for item in to_translate:
        if item["value"] in cache:
            stats["cached"] = stats.get("cached", 0) + 1
            translated_entries.append({
                "key": item["key"],
                "value": cache[item["value"]]
            })


    async def process_batches_parallel():
        nonlocal translated_entries
        lock = asyncio.Lock()
        semaphore = asyncio.Semaphore(args["parallel"])
        
        async def process_single_batch(batch_data):
            batch, batch_num = batch_data
            async with semaphore:
                results = await translate_batch_async(
                    batch, cache, args["target_language"], args["model"],
                    stats, batch_num, num_batches, args["verbose"], lock
                )
                

                processed = stats['translated'] + stats['cached']
                total_to_process = len(to_translate)
                elapsed = time.time() - start_time
                progress_pct = (processed / total_to_process * 100) if total_to_process > 0 else 0
                

                current_cost = 0.0
                if args['model'] in MODEL_PRICING and stats["api_calls"] > 0:
                    pricing = MODEL_PRICING[args['model']]
                    input_cost = (stats["total_prompt_tokens"] / 1_000_000) * pricing["input"]
                    output_cost = (stats["total_completion_tokens"] / 1_000_000) * pricing["output"]
                    current_cost = input_cost + output_cost
                

                eta_str = "calculando..."
                estimated_total_cost = 0.0
                if stats["api_calls"] > 0 and processed > 0:
                    completed_batches = stats["api_calls"]
                    if completed_batches > 0:
                        avg_time_per_batch = elapsed / completed_batches
                        remaining_batches = num_batches - completed_batches
                        eta_seconds = int(avg_time_per_batch * remaining_batches)
                        
                        if eta_seconds < 60: eta_str = f"{eta_seconds}s"
                        elif eta_seconds < 3600: eta_str = f"{eta_seconds // 60}m {eta_seconds % 60}s"
                        else: eta_str = f"{eta_seconds // 3600}h {(eta_seconds % 3600) // 60}m"
                        
                        if current_cost > 0:
                            cost_per_batch = current_cost / completed_batches
                            estimated_total_cost = cost_per_batch * num_batches
                

                if not args["verbose"]:
                    elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"
                    cost_str = f"${current_cost:.6f}"
                    if estimated_total_cost > 0:
                        cost_str += f" (est. ${estimated_total_cost:.6f})"
                    
                    print(f"\r🔄 Batch {batch_num}/{num_batches} | "
                          f"Progresso: {processed}/{total_to_process} ({progress_pct:.1f}%) | "
                          f"Tempo: {elapsed_str} | ETA: {eta_str} | "
                          f"Custo: {cost_str}", end="", flush=True)
                

                if not args["dry_run"] and batch_num % 5 == 0:
                    async with lock:
                        try:
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                json.dump(cache, f, ensure_ascii=False, indent=2)
                        except Exception: pass
                
                return results
        

        tasks = [process_single_batch(batch_data) for batch_data in all_batches]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        

        for result in all_results:
            if isinstance(result, Exception):
                if args["verbose"]: print(f"\n❌ Erro no batch: {result}")
                continue
            for r in result:
                translated_entries.append({ "key": r["key"], "value": r["translated"] })
    

    if num_batches > 0:
        if args["parallel"] > 1:
            asyncio.run(process_batches_parallel())
        else:

            for batch, batch_num in all_batches:
                if args["verbose"]:
                    print(f"\n{'='*70}\n📦 BATCH {batch_num}/{num_batches} (tamanho: {len(batch)})\n{'='*70}")
                
                results = asyncio.run(translate_batch_async(
                    batch, cache, args["target_language"], args["model"],
                    stats, batch_num, num_batches, args["verbose"], None
                ))
                
                for r in results:
                    translated_entries.append({ "key": r["key"], "value": r["translated"] })
                

                if not args["dry_run"]:
                    try:
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump(cache, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        print(f"⚠️  Erro ao salvar cache: {e}")
                

                processed = stats['translated'] + stats['cached']
                total_to_process = len(to_translate)
                elapsed = time.time() - start_time
                progress_pct = (processed / total_to_process * 100) if total_to_process > 0 else 0
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
                    if eta_seconds < 60: eta_str = f"{eta_seconds}s"
                    elif eta_seconds < 3600: eta_str = f"{eta_seconds // 60}m {eta_seconds % 60}s"
                    else: eta_str = f"{eta_seconds // 3600}h {(eta_seconds % 3600) // 60}m"
                
                if not args["verbose"]:
                    elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"
                    cost_str = f"${current_cost:.6f}"
                    if estimated_total_cost > 0: cost_str += f" (est. ${estimated_total_cost:.6f})"
                    print(f"\r🔄 Batch {batch_num}/{num_batches} | "
                          f"Progresso: {processed}/{total_to_process} ({progress_pct:.1f}%) | "
                          f"Tempo: {elapsed_str} | ETA: {eta_str} | "
                          f"Custo: {cost_str}", end="", flush=True)


    if not args["verbose"]:
        print("\r" + " " * 100 + "\r", end="")
    

    if not args["dry_run"]:
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Erro ao salvar cache final: {e}")
    

    total_time = time.time() - start_time
    total_cost = 0.0
    input_cost = 0.0
    output_cost = 0.0
    
    if args['model'] in MODEL_PRICING:
        pricing = MODEL_PRICING[args['model']]
        input_cost = (stats["total_prompt_tokens"] / 1_000_000) * pricing["input"]
        output_cost = (stats["total_completion_tokens"] / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
    

    print("\n" + "=" * 70)
    print("🔨 RECONSTRUINDO ESTRUTURA JSON...")
    print("=" * 70)
    

    translated_dict = {e["key"]: e["value"] for e in translated_entries}
    

    for key, existing_value in flat_existing.items():

        original_entry = next((e for e in flat_base if e["key"] == key), None)
        if original_entry:
            original_value = original_entry["value"]


            if (existing_value != original_value and 
                existing_value != DEFAULT_ON_FAILURE and 
                key not in translated_dict):
                translated_dict[key] = existing_value
    

    print("\n🔍 Validando traduções finais...")
    final_errors = 0
    placeholder_errors_final = []
    

    missing_keys = []
    for entry in flat_base:
        key = entry["key"]
        if isinstance(entry["value"], str) and len(entry["value"]) > 0:
            if key not in translated_dict or not translated_dict[key] or len(translated_dict[key]) == 0:
                missing_keys.append(key)
    
    if missing_keys:
        print(f"⚠️  {len(missing_keys)} chaves sem tradução válida, tentando retraduzir...")
        

        for key in missing_keys:
            entry = next((e for e in flat_base if e["key"] == key), None)
            if not entry:
                continue
            
            try:
                masked, placeholder_map = mask_placeholders(entry["value"])
                local_stats = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                

                translated_masked, retry_tokens = call_openai_single_key(
                    entry["key"], masked, args["model"], args["target_language"], local_stats
                )
                

                if translated_masked and len(translated_masked) > 0:
                    translated = restore_placeholders(translated_masked, placeholder_map)
                    

                    if "__PH_" in translated:

                        for ph_item in placeholder_map:
                            translated = translated.replace(ph_item["token"], ph_item["original"])
                        

                        if "__PH_" in translated:
                            if args["verbose"]:
                                print(f"  ⚠️  Placeholders não restaurados em '{entry['key']}' (retry), marcando como falha")
                            translated_dict[entry["key"]] = DEFAULT_ON_FAILURE
                            stats["errors"] = stats.get("errors", 0) + 1
                            continue
                    
                    translated_dict[entry["key"]] = translated
                    cache[entry["value"]] = translated
                    

                    stats["total_prompt_tokens"] = stats.get("total_prompt_tokens", 0) + retry_tokens["prompt_tokens"]
                    stats["total_completion_tokens"] = stats.get("total_completion_tokens", 0) + retry_tokens["completion_tokens"]
                    stats["total_tokens"] = stats.get("total_tokens", 0) + retry_tokens["total_tokens"]
                    stats["api_calls"] = stats.get("api_calls", 0) + 1
                    stats["translated"] = stats.get("translated", 0) + 1
                    
                    if args["verbose"]:
                        print(f"  ✓ Retraduzido: {entry['key']}")
                else:

                    translated_dict[entry["key"]] = DEFAULT_ON_FAILURE
                    stats["errors"] = stats.get("errors", 0) + 1
                    if args["verbose"]:
                        print(f"  ❌ Falha ao retraduzir: {entry['key']}")
            except Exception as e:

                translated_dict[entry["key"]] = DEFAULT_ON_FAILURE
                stats["errors"] = stats.get("errors", 0) + 1
                if args["verbose"]:
                    print(f"  ❌ Erro ao retraduzir {entry['key']}: {e}")
    

    for entry in flat_base:
        key = entry["key"]
        if isinstance(entry["value"], str) and len(entry["value"]) > 0:

            if key not in translated_dict:
                translated_dict[key] = DEFAULT_ON_FAILURE
                final_errors += 1
            elif not translated_dict[key] or len(translated_dict[key]) == 0:
                translated_dict[key] = DEFAULT_ON_FAILURE
                final_errors += 1
            elif "__PH_" in translated_dict[key]:

                placeholder_errors_final.append(key)
                original_value = entry["value"]
                masked, placeholder_map = mask_placeholders(original_value)
                

                restored_value = restore_placeholders(translated_dict[key], placeholder_map)
                

                if "__PH_" in restored_value:
                    if args["verbose"]:
                        print(f"  ⚠️  Placeholders não restaurados em '{key}', marcando como falha")
                    translated_dict[key] = DEFAULT_ON_FAILURE
                    final_errors += 1
                else:
                    translated_dict[key] = restored_value
    
    if final_errors > 0:
        print(f"⚠️  AVISO: {final_errors} chaves não puderam ser traduzidas e foram marcadas como '{DEFAULT_ON_FAILURE}'.")
    if placeholder_errors_final:
        print(f"⚠️  AVISO: {len(placeholder_errors_final)} chaves tiveram placeholders corrigidos na validação final.")
    if final_errors == 0 and not placeholder_errors_final:
        print("✓ Todas as chaves validadas!")
    

    output_data = reconstruct_json_preserving_order(base_data, translated_dict)
    print("✓ Estrutura reconstruída!")
    

    if output_path.exists() and not args["dry_run"]:
        shutil.copy2(output_path, backup_file)
        print(f"✓ Backup criado: {backup_file}")
    

    print("\n" + "=" * 70)
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 70)
    

    total_strings_in_json = len([e for e in flat_base if isinstance(e["value"], str) and len(e["value"]) > 0])
    total_translated = stats['translated'] + stats['cached']
    total_errors = stats['errors'] + final_errors
    
    print(f"📝 Total de strings no JSON: {total_strings_in_json}")
    print(f"✅ Strings traduzidas (API): {stats['translated']}")
    print(f"💾 Strings do cache: {stats['cached']}")
    print(f"📊 Total processado: {total_translated} ({total_translated}/{total_strings_in_json})")
    print(f"❌ Erros (marcados c/ '{DEFAULT_ON_FAILURE}'): {total_errors}")
    print(f"📞 Chamadas à API: {stats['api_calls']}")
    print(f"⏱️  Tempo total: {int(total_time // 60)}m {int(total_time % 60)}s")
    
    if stats["api_calls"] > 0:
        print(f"\n📈 USO DE TOKEN:")
        print(f"  • Prompt tokens: {stats['total_prompt_tokens']:,}")
        print(f"  • Completion tokens: {stats['total_completion_tokens']:,}")
        print(f"  • Total tokens: {stats['total_tokens']:,}")
        if stats["api_calls"] > 0:
            print(f"  • Média por chamada: {stats['total_tokens'] // stats['api_calls']:,} tokens")
        
        if total_cost > 0:
            print(f"\n💰 CUSTOS:")
            print(f"  • Custo input: ${input_cost:.6f}")
            print(f"  • Custo output: ${output_cost:.6f}")
            print(f"  • CUSTO TOTAL: ${total_cost:.6f}")
            if stats['translated'] > 0:
                print(f"  • Custo por string (API): ${total_cost / stats['translated']:.6f}")
    

    if args["dry_run"]:
        print("\n" + "=" * 70)
        print("🧪 DRY-RUN: Exemplos de traduções")
        print("=" * 70)
        

        example_keys = [e["key"] for e in translated_entries if "value" in e and e["value"] != DEFAULT_ON_FAILURE][:10]
        error_keys = [e["key"] for e in translated_entries if "value" in e and e["value"] == DEFAULT_ON_FAILURE][:5]

        print("--- Sucessos ---")
        for key in example_keys:
            value = translated_dict.get(key, "")
            value_preview = value[:60] + "..." if len(value) > 60 else value
            print(f"  {key} => {value_preview}")
        
        if error_keys:
            print("--- Falhas ---")
            for key in error_keys:
                print(f"  {key} => {DEFAULT_ON_FAILURE}")

        print(f"\nTotal: {len(translated_dict)} traduções processadas")
        print("Execute sem --dry para salvar o arquivo")
        return
    

    print(f"\n💾 Salvando arquivo traduzido: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        file_size = output_path.stat().st_size / 1024
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
