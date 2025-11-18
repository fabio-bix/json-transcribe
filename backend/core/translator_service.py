import json
import os
import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

from openai import OpenAI


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.script_openai import (
    flatten_object,
    reconstruct_json_preserving_order,
    mask_placeholders,
    restore_placeholders,
    call_openai_batch_json,
    translate_batch_async,
    calculate_cost,
    MODEL_PRICING,
    DEFAULT_BATCH_SIZE,
    DEFAULT_MODEL,
    DEFAULT_PARALLEL,
    DEFAULT_ON_FAILURE,
)

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

client = OpenAI(api_key=OPENAI_API_KEY)


class TranslationJob:
    
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status = "pending"
        self.progress = 0.0
        self.total_strings = 0
        self.translated_strings = 0
        self.cached_strings = 0
        self.current_batch = 0
        self.total_batches = 0
        self.stats = {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "api_calls": 0,
            "translated": 0,
            "cached": 0,
            "errors": 0,
        }
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.result_data = None
        self.estimated_cost = 0.0
        self.actual_cost = 0.0
        self.eta_seconds = None
        self.estimated_total_seconds = None
        self.config = None
        self.target_language = None
        self.model = None


_active_jobs: Dict[str, TranslationJob] = {}


def validate_json(data: Any) -> Tuple[bool, Optional[str]]:
    
    try:
        if isinstance(data, (dict, list)):

            json.dumps(data)
            return True, None
        return False, "JSON deve ser um objeto ou array"
    except Exception as e:
        return False, str(e)


def estimate_translation(
    json_data: Dict[str, Any],
    target_language: str,
    model: str = DEFAULT_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    parallel: int = DEFAULT_PARALLEL,
) -> Dict[str, Any]:
    

    flat_data = flatten_object(json_data)
    

    all_strings = [
        e for e in flat_data
        if isinstance(e["value"], str) and e["value"].strip()
    ]
    
    total_strings = len(all_strings)
    

    estimated_chars = sum(len(str(e["value"])) for e in all_strings)
    estimated_tokens_input = estimated_chars // 4
    estimated_tokens_output = int(estimated_tokens_input * 1.2)
    

    estimated_cost = 0.0
    if model in MODEL_PRICING:
        pricing = MODEL_PRICING[model]
        input_cost = (estimated_tokens_input / 1_000_000) * pricing["input"]
        output_cost = (estimated_tokens_output / 1_000_000) * pricing["output"]
        estimated_cost = input_cost + output_cost
    

    num_batches = (total_strings + batch_size - 1) // batch_size if total_strings > 0 else 0
    estimated_time_per_batch = 3.0

    estimated_time_seconds = (num_batches / parallel) * estimated_time_per_batch
    
    return {
        "total_strings": total_strings,
        "total_entries": len(flat_data),
        "estimated_batches": num_batches,
        "estimated_tokens_input": estimated_tokens_input,
        "estimated_tokens_output": estimated_tokens_output,
        "estimated_cost_usd": round(estimated_cost, 6),
        "estimated_time_seconds": int(estimated_time_seconds),
        "model": model,
        "batch_size": batch_size,
        "parallel": parallel,
    }


async def translate_json_async(
    json_data: Dict[str, Any],
    target_language: str,
    job_id: str,
    model: str = DEFAULT_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    parallel: int = DEFAULT_PARALLEL,
    existing_data: Optional[Dict[str, Any]] = None,
    cache: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    
    job = _active_jobs.get(job_id)
    if not job:
        raise ValueError(f"Job {job_id} não encontrado")
    
    job.status = "processing"
    job.start_time = time.time()
    
    try:

        if cache is None:
            cache = {}
        

        flat_base = flatten_object(json_data)
        flat_existing = {e["key"]: e["value"] for e in flatten_object(existing_data or {})}
        

        all_strings = [
            e for e in flat_base
            if isinstance(e["value"], str) and len(e["value"]) > 0
        ]
        

        to_translate = [
            e for e in all_strings
            if (e["key"] not in flat_existing or flat_existing[e["key"]] == e["value"])
        ]
        

        cached_count = sum(1 for e in to_translate if e["value"] in cache)
        to_translate_count = len(to_translate) - cached_count
        

        job.total_strings = len(all_strings)
        job.cached_strings = cached_count
        job.target_language = target_language
        job.model = model
        

        all_batches = []
        for i in range(0, len(to_translate), batch_size):
            batch = to_translate[i:i + batch_size]
            batch_num = i // batch_size + 1
            all_batches.append((batch, batch_num))
        
        job.total_batches = len(all_batches)
        
        translated_entries = []
        lock = asyncio.Lock()
        

        async def process_batches_parallel():
            nonlocal translated_entries
            semaphore = asyncio.Semaphore(parallel)
            
            async def process_single_batch(batch_data):
                batch, batch_num = batch_data
                async with semaphore:
                    results = await translate_batch_async(
                        batch, cache, target_language, model,
                        job.stats, batch_num, job.total_batches, False, lock
                    )
                    

                    async with lock:
                        job.translated_strings = job.stats.get("translated", 0)
                        job.cached_strings = job.stats.get("cached", 0)
                        job.current_batch = batch_num
                        
                        processed = job.translated_strings + job.cached_strings
                        job.progress = processed / job.total_strings if job.total_strings > 0 else 0.0
                        

                        if model in MODEL_PRICING and job.stats["api_calls"] > 0:
                            pricing = MODEL_PRICING[model]
                            input_cost = (job.stats["total_prompt_tokens"] / 1_000_000) * pricing["input"]
                            output_cost = (job.stats["total_completion_tokens"] / 1_000_000) * pricing["output"]
                            job.actual_cost = input_cost + output_cost
                        

                        elapsed = time.time() - job.start_time
                        if processed > 0 and job.total_strings > 0:

                            progress_ratio = processed / job.total_strings
                            
                            if progress_ratio > 0:

                                avg_time_per_string = elapsed / processed
                                remaining_strings = job.total_strings - processed
                                

                                effective_parallel = min(parallel, job.total_batches - job.current_batch)
                                if effective_parallel > 0:

                                    job.eta_seconds = int((remaining_strings * avg_time_per_string) / effective_parallel)
                                else:
                                    job.eta_seconds = int(remaining_strings * avg_time_per_string)
                                

                                if progress_ratio > 0.01:
                                    job.estimated_total_seconds = int(elapsed / progress_ratio)
                                else:

                                    num_batches = job.total_batches
                                    estimated_time_per_batch = 3.0
                                    job.estimated_total_seconds = int((num_batches / parallel) * estimated_time_per_batch)
                            else:
                                job.eta_seconds = None
                                job.estimated_total_seconds = None
                        else:
                            job.eta_seconds = None
                            job.estimated_total_seconds = None
                    
                    return results
            

            tasks = [process_single_batch(batch_data) for batch_data in all_batches]
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            

            for result in all_results:
                if isinstance(result, Exception):
                    continue
                for r in result:
                    translated_entries.append({
                        "key": r["key"],
                        "value": r["translated"]
                    })
        

        if parallel > 1:
            await process_batches_parallel()
        else:

            for batch, batch_num in all_batches:
                results = await translate_batch_async(
                    batch, cache, target_language, model,
                    job.stats, batch_num, job.total_batches, False, None
                )
                for r in results:
                    translated_entries.append({
                        "key": r["key"],
                        "value": r["translated"]
                    })
                

                job.translated_strings = job.stats.get("translated", 0)
                job.cached_strings = job.stats.get("cached", 0)
                job.current_batch = batch_num
                processed = job.translated_strings + job.cached_strings
                job.progress = processed / job.total_strings if job.total_strings > 0 else 0.0
                

                elapsed = time.time() - job.start_time
                if processed > 0 and job.total_strings > 0:
                    progress_ratio = processed / job.total_strings
                    
                    if progress_ratio > 0:
                        avg_time_per_string = elapsed / processed
                        remaining_strings = job.total_strings - processed
                        
                        effective_parallel = min(parallel, job.total_batches - job.current_batch)
                        if effective_parallel > 0:
                            job.eta_seconds = int((remaining_strings * avg_time_per_string) / effective_parallel)
                        else:
                            job.eta_seconds = int(remaining_strings * avg_time_per_string)
                        
                        if progress_ratio > 0.01:
                            job.estimated_total_seconds = int(elapsed / progress_ratio)
                        else:
                            num_batches = job.total_batches
                            estimated_time_per_batch = 3.0
                            job.estimated_total_seconds = int((num_batches / parallel) * estimated_time_per_batch)
                    else:
                        job.eta_seconds = None
                        job.estimated_total_seconds = None
                else:
                    job.eta_seconds = None
                    job.estimated_total_seconds = None
        

        translated_dict = {e["key"]: e["value"] for e in translated_entries}
        

        flat_base = flatten_object(json_data)
        missing_keys = []
        for entry in flat_base:
            if isinstance(entry["value"], str) and len(entry["value"]) > 0:
                if entry["key"] not in translated_dict:
                    missing_keys.append(entry["key"])
                elif not translated_dict[entry["key"]] or len(translated_dict[entry["key"]]) == 0:
                    missing_keys.append(entry["key"])
        
        if missing_keys:

            retry_items = []
            for entry in flat_base:
                if entry["key"] in missing_keys and isinstance(entry["value"], str) and len(entry["value"]) > 0:
                    retry_items.append(entry)
            
            if retry_items:

                for entry in retry_items:
                    try:
                        masked, placeholder_map = mask_placeholders(entry["value"])
                        local_stats = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                        

                        from scripts.script_openai import call_openai_single_key
                        translated_masked, retry_tokens = await asyncio.to_thread(
                            call_openai_single_key, entry["key"], masked, model, target_language, local_stats
                        )
                        

                        if translated_masked and len(translated_masked) > 0:
                            translated = restore_placeholders(translated_masked, placeholder_map)
                            

                            if "__PH_" in translated:

                                for ph_item in placeholder_map:
                                    translated = translated.replace(ph_item["token"], ph_item["original"])
                                

                                if "__PH_" in translated:
                                    translated_dict[entry["key"]] = DEFAULT_ON_FAILURE
                                    job.stats["errors"] = job.stats.get("errors", 0) + 1
                                    continue
                            
                            translated_dict[entry["key"]] = translated
                            

                            job.stats["total_prompt_tokens"] = job.stats.get("total_prompt_tokens", 0) + retry_tokens["prompt_tokens"]
                            job.stats["total_completion_tokens"] = job.stats.get("total_completion_tokens", 0) + retry_tokens["completion_tokens"]
                            job.stats["total_tokens"] = job.stats.get("total_tokens", 0) + retry_tokens["total_tokens"]
                            job.stats["api_calls"] = job.stats.get("api_calls", 0) + 1
                        else:

                            translated_dict[entry["key"]] = DEFAULT_ON_FAILURE
                            job.stats["errors"] = job.stats.get("errors", 0) + 1
                    except Exception as e:

                        translated_dict[entry["key"]] = DEFAULT_ON_FAILURE
                        job.stats["errors"] = job.stats.get("errors", 0) + 1
        
        output_data = reconstruct_json_preserving_order(json_data, translated_dict)
        

        final_missing = []
        placeholder_errors = []
        
        for entry in flat_base:
            if isinstance(entry["value"], str) and len(entry["value"]) > 0:
                key = entry["key"]
                

                if key not in translated_dict or not translated_dict[key] or len(translated_dict[key]) == 0:
                    final_missing.append(key)
                else:

                    translated_value = translated_dict[key]
                    if "__PH_" in translated_value:
                        placeholder_errors.append(key)

                        original_value = entry["value"]
                        masked, placeholder_map = mask_placeholders(original_value)
                        

                        for ph_item in placeholder_map:
                            translated_value = translated_value.replace(ph_item["token"], ph_item["original"])
                        

                        if "__PH_" in translated_value:
                            translated_dict[key] = DEFAULT_ON_FAILURE
                            job.stats["errors"] = job.stats.get("errors", 0) + 1
                        else:
                            translated_dict[key] = translated_value
        
        if final_missing:

            for key in final_missing:
                translated_dict[key] = DEFAULT_ON_FAILURE
            job.stats["validation_errors"] = len(final_missing)
            if len(final_missing) > 0:
                job.error_message = f"{len(final_missing)} chaves não foram traduzidas e foram marcadas como '{DEFAULT_ON_FAILURE}'"
        
        if placeholder_errors:
            job.stats["placeholder_errors"] = len(placeholder_errors)
            if job.error_message:
                job.error_message += f" | {len(placeholder_errors)} chaves com placeholders corrigidos"
            else:
                job.error_message = f"{len(placeholder_errors)} chaves com placeholders corrigidos"
        

        if model in MODEL_PRICING:
            pricing = MODEL_PRICING[model]
            input_cost = (job.stats["total_prompt_tokens"] / 1_000_000) * pricing["input"]
            output_cost = (job.stats["total_completion_tokens"] / 1_000_000) * pricing["output"]
            job.actual_cost = input_cost + output_cost
        
        job.result_data = output_data
        job.status = "completed"
        job.progress = 1.0
        job.end_time = time.time()
        
        return output_data
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.end_time = time.time()
        raise


def create_job(job_id: Optional[str] = None) -> TranslationJob:
    
    if job_id is None:
        import uuid
        job_id = str(uuid.uuid4())
    
    job = TranslationJob(job_id)
    _active_jobs[job_id] = job
    return job


def get_job(job_id: str) -> Optional[TranslationJob]:
    
    return _active_jobs.get(job_id)


def list_jobs() -> List[TranslationJob]:
    
    return list(_active_jobs.values())


def delete_job(job_id: str) -> bool:
    
    if job_id in _active_jobs:
        del _active_jobs[job_id]
        return True
    return False

