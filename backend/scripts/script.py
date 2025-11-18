#!/usr/bin/env python3

import json
import sys
import time
from pathlib import Path
from deep_translator import GoogleTranslator
from typing import Any, Dict


def translate_value_recursive(
    value: Any,
    translator: GoogleTranslator,
    cache: Dict[str, str],
    stats: Dict[str, int],
    path: str = ""
) -> Any:
    if isinstance(value, dict):
        return {
            key: translate_value_recursive(
                val, translator, cache, stats, f"{path}.{key}" if path else key
            )
            for key, val in value.items()
        }
    
    elif isinstance(value, list):
        return [
            translate_value_recursive(
                item, translator, cache, stats, f"{path}[{i}]" if path else f"[{i}]"
            )
            for i, item in enumerate(value)
        ]
    
    elif isinstance(value, str) and value.strip():
        original = value
        
        if original in cache:
            stats["cached"] += 1
            return cache[original]
        
        try:
            import builtins
            if hasattr(builtins, '_tracker'):
                builtins._tracker.update(path)
        except:
            pass
        
        try:
            translated = translator.translate(original)
            cache[original] = translated
            stats["translated"] += 1
            return translated
        except Exception as e:
            stats["errors"] += 1
            print(f"\n⚠️  Erro ao traduzir '{path}': {e}")
            cache[original] = original
            return original
    
    else:
        return value


def translate_json_file(
    input_file: str,
    output_file: str = None,
    target_language: str = 'pt',
    source_language: str = 'en'
) -> None:
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Erro: Arquivo '{input_file}' não encontrado!")
        sys.exit(1)
    
    if output_file is None:
        output_path = input_path.parent / f"{input_path.stem}_{target_language}{input_path.suffix}"
    else:
        output_path = Path(output_file)
    
    print("=" * 60)
    print("🌐 TRADUTOR JSON - GOOGLE TRANSLATE")
    print("=" * 60)
    print(f"📁 Arquivo de entrada: {input_path}")
    print(f"📁 Arquivo de saída: {output_path}")
    print(f"🌍 Idioma origem: {source_language}")
    print(f"🌍 Idioma destino: {target_language}")
    print("=" * 60)
    
    cache_file = input_path.parent / f".translate_cache_{target_language}.json"
    
    cache = {}
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            print(f"✓ Cache carregado: {len(cache)} traduções em cache")
        except Exception as e:
            print(f"⚠️  Não foi possível carregar cache: {e}")
    
    print("\n📖 Lendo arquivo...")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Arquivo lido com sucesso!")
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao abrir arquivo: {e}")
        sys.exit(1)
    
    def count_strings(obj: Any) -> int:
        count = 0
        if isinstance(obj, dict):
            for v in obj.values():
                count += count_strings(v)
        elif isinstance(obj, list):
            for item in obj:
                count += count_strings(item)
        elif isinstance(obj, str) and obj.strip():
            if obj not in cache:
                count += 1
        return count
    
    print("\n📊 Analisando estrutura do JSON...")
    total_strings = count_strings(data)
    cached_strings = len([v for v in cache.values() if v])
    
    print(f"✓ Análise concluída!")
    print(f"  • Strings para traduzir: {total_strings}")
    print(f"  • Strings em cache: {cached_strings}")
    
    if total_strings == 0:
        print("\n✅ Todas as strings já estão traduzidas no cache!")
        print("   Se quiser retraduzir, delete o arquivo de cache.")
    
    print("\n" + "=" * 60)
    print("🔄 INICIANDO TRADUÇÃO...")
    print("=" * 60)
    
    start_time = time.time()
    stats = {
        "translated": 0,
        "cached": 0,
        "errors": 0,
        "total": 0
    }
    
    translator = GoogleTranslator(source=source_language, target=target_language)
    
    class ProgressTracker:
        def __init__(self, total: int):
            self.total = total
            self.current = 0
            self.start_time = time.time()
        
        def update(self, path: str = ""):
            self.current += 1
            progress = (self.current / self.total) * 100 if self.total > 0 else 0
            elapsed = time.time() - self.start_time
            
            if self.current > 1:
                avg_time = elapsed / self.current
                remaining = avg_time * (self.total - self.current)
                eta_m = int(remaining // 60)
                eta_s = int(remaining % 60)
                eta_str = f"{eta_m}m {eta_s}s" if eta_m > 0 else f"{eta_s}s"
            else:
                eta_str = "calculando..."
            
            print(f"\r[{self.current:4d}/{self.total}] ({progress:5.1f}%) | "
                  f"Tempo: {int(elapsed)}s | ETA: {eta_str} | "
                  f"Traduzindo: {path[:45]}...", end="", flush=True)
    
    tracker = ProgressTracker(total_strings)
    
    import builtins
    builtins._tracker = tracker
    
    print("Processando...")
    output_data = translate_value_recursive(data, translator, cache, stats)
    
    print("\r" + " " * 100 + "\r", end="")
    
    if cache:
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            print(f"✓ Cache salvo: {cache_file}")
        except Exception as e:
            print(f"⚠️  Erro ao salvar cache: {e}")
    
    total_time = time.time() - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
    
    print("\n" + "=" * 60)
    print("✅ TRADUÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"📊 Estatísticas:")
    print(f"  • Strings traduzidas agora: {stats['translated']}")
    print(f"  • Strings do cache: {stats['cached']}")
    print(f"  • Erros: {stats['errors']}")
    print(f"  • Tempo total: {time_str}")
    if stats['translated'] > 0:
        print(f"  • Velocidade: {stats['translated'] / total_time:.1f} strings/segundo")
    
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
    
    print("\n" + "=" * 60)
    print("🎉 PROCESSO FINALIZADO COM SUCESSO!")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Uso: python script.py <arquivo_json> [idioma_destino] [arquivo_saida]")
        print("\nExemplos:")
        print("  python script.py en.json pt")
        print("  python script.py en.json pt pt.json")
        print("  python script.py en.json es es.json")
        print("\nIdiomas suportados: pt (português), es (espanhol), fr (francês), etc.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    target_language = sys.argv[2] if len(sys.argv) > 2 else 'pt'
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        translate_json_file(input_file, output_file, target_language)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
