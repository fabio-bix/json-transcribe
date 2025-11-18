import json
import asyncio
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response
from pydantic import BaseModel, Field
import uvicorn


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.translator_service import (
    validate_json,
    estimate_translation,
    translate_json_async,
    create_job,
    get_job,
    list_jobs,
    delete_job,
    TranslationJob,
    MODEL_PRICING,
    DEFAULT_MODEL,
    DEFAULT_BATCH_SIZE,
    DEFAULT_PARALLEL,
)

app = FastAPI(
    title="JSON Translator API",
    description="API para tradução de arquivos JSON usando OpenAI ou Google Translate",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranslationRequest(BaseModel):
    target_language: str = Field(..., description="Código do idioma de destino (pt, es, fr, de, etc.)")
    model: Optional[str] = Field(DEFAULT_MODEL, description="Modelo OpenAI a usar")
    batch_size: Optional[int] = Field(DEFAULT_BATCH_SIZE, description="Tamanho do batch")
    parallel: Optional[int] = Field(DEFAULT_PARALLEL, description="Número de batches paralelos")
    method: str = Field("openai", description="Método de tradução: 'openai' ou 'google'")
    json_data: Dict[str, Any] = Field(..., description="Dados JSON a traduzir")


class EstimateRequest(BaseModel):
    target_language: str
    model: Optional[str] = DEFAULT_MODEL
    batch_size: Optional[int] = DEFAULT_BATCH_SIZE
    parallel: Optional[int] = DEFAULT_PARALLEL
    json_data: Dict[str, Any]


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    total_strings: int
    translated_strings: int
    cached_strings: int
    current_batch: int
    total_batches: int
    stats: Dict[str, Any]
    estimated_cost: float
    actual_cost: float
    eta_seconds: Optional[int]
    estimated_total_seconds: Optional[int]
    elapsed_seconds: Optional[float]
    target_language: Optional[str] = None
    model: Optional[str] = None
    error_message: Optional[str]


@app.get("/")
async def root():
    
    return {
        "name": "JSON Translator API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /api/upload",
            "estimate": "POST /api/translate/estimate",
            "start": "POST /api/translate/start",
            "status": "GET /api/translate/{job_id}/status",
            "result": "GET /api/translate/{job_id}/result",
            "models": "GET /api/models",
            "languages": "GET /api/languages",
        }
    }


@app.post("/api/upload")
async def upload_json(file: UploadFile = File(...)):
    
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .json")
    
    try:
        contents = await file.read()
        json_data = json.loads(contents.decode('utf-8'))
        

        is_valid, error_msg = validate_json(json_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"JSON inválido: {error_msg}")
        

        from core.translator_service import flatten_object
        flat_data = flatten_object(json_data)
        strings_count = sum(1 for e in flat_data if isinstance(e["value"], str) and e["value"].strip())
        
        return {
            "success": True,
            "filename": file.filename,
            "total_entries": len(flat_data),
            "strings_count": strings_count,
            "data": json_data,
        }
    
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Erro ao parsear JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@app.post("/api/translate/estimate")
async def estimate(estimate_req: EstimateRequest):
    
    try:
        estimate_result = estimate_translation(
            json_data=estimate_req.json_data,
            target_language=estimate_req.target_language,
            model=estimate_req.model or DEFAULT_MODEL,
            batch_size=estimate_req.batch_size or DEFAULT_BATCH_SIZE,
            parallel=estimate_req.parallel or DEFAULT_PARALLEL,
        )
        
        return {
            "success": True,
            **estimate_result,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao estimar: {str(e)}")


@app.post("/api/translate/start")
async def start_translation(
    translation_req: TranslationRequest,
    background_tasks: BackgroundTasks,
):
    
    try:

        if translation_req.method not in ["openai", "google"]:
            raise HTTPException(status_code=400, detail="Método deve ser 'openai' ou 'google'")
        

        if translation_req.method == "google":
            raise HTTPException(status_code=501, detail="Google Translate ainda não implementado na API")
        

        job = create_job()
        

        job.config = translation_req
        

        background_tasks.add_task(
            translate_json_async,
            json_data=translation_req.json_data,
            target_language=translation_req.target_language,
            job_id=job.job_id,
            model=translation_req.model or DEFAULT_MODEL,
            batch_size=translation_req.batch_size or DEFAULT_BATCH_SIZE,
            parallel=translation_req.parallel or DEFAULT_PARALLEL,
        )
        
        return {
            "success": True,
            "job_id": job.job_id,
            "status": job.status,
            "message": "Tradução iniciada",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar tradução: {str(e)}")


@app.get("/api/translate/{job_id}/status")
async def get_translation_status(job_id: str):
    
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")
    
    elapsed = None
    if job.start_time:
        elapsed = time.time() - job.start_time if job.status == "processing" else (job.end_time - job.start_time if job.end_time else None)
    

    language_map = {
        "es": "Espanhol", "pt": "Português", "fr": "Francês", "de": "Alemão",
        "it": "Italiano", "nl": "Holandês", "pl": "Polonês", "sv": "Sueco",
        "da": "Dinamarquês", "no": "Norueguês", "fi": "Finlandês", "cs": "Tcheco",
        "hu": "Húngaro", "ro": "Romeno", "hr": "Croata", "sr": "Sérvio (Latinizado)",
        "tr": "Turco", "id": "Indonésio", "tl": "Filipino (Tagalog)", "ms": "Malaio",
    }
    target_language_name = language_map.get(getattr(job, 'target_language', None), getattr(job, 'target_language', 'Unknown'))
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        total_strings=job.total_strings,
        translated_strings=job.translated_strings,
        cached_strings=job.cached_strings,
        current_batch=job.current_batch,
        total_batches=job.total_batches,
        stats=job.stats,
        estimated_cost=job.estimated_cost,
        actual_cost=job.actual_cost,
        eta_seconds=job.eta_seconds,
        estimated_total_seconds=getattr(job, 'estimated_total_seconds', None),
        elapsed_seconds=elapsed,
        target_language=target_language_name,
        model=getattr(job, 'model', None),
        error_message=job.error_message,
    )


@app.get("/api/translate/{job_id}/result")
async def get_translation_result(job_id: str):
    
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")
    
    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job ainda não concluído. Status: {job.status}"
        )
    
    if not job.result_data:
        raise HTTPException(status_code=500, detail="Resultado não disponível")
    

    from core.translator_service import flatten_object
    from scripts.script_openai import DEFAULT_ON_FAILURE
    
    flat_result = flatten_object(job.result_data)
    

    failed_keys = []
    empty_keys = []
    needs_review_keys = []
    
    for entry in flat_result:
        key = entry["key"]
        value = entry["value"]
        if isinstance(value, str):
            if value == DEFAULT_ON_FAILURE:
                needs_review_keys.append(key)
            elif len(value) == 0:
                empty_keys.append(key)
            elif value.strip() == "":
                empty_keys.append(key)
    
    failed_keys = needs_review_keys + empty_keys
    
    return {
        "success": True,
        "job_id": job.job_id,
        "data": job.result_data,
        "stats": {
            "total_strings": job.total_strings,
            "translated": job.translated_strings,
            "cached": job.cached_strings,
            "cost_usd": job.actual_cost,
            "tokens": job.stats["total_tokens"],
            "errors": job.stats.get("errors", 0),
            "failed_keys": failed_keys[:50],
            "failed_count": len(failed_keys),
            "needs_review_count": len(needs_review_keys),
            "empty_count": len(empty_keys),
        },
        "error_message": job.error_message,
    }


@app.get("/api/models")
async def get_models():
    
    models = []
    for model_name, pricing in MODEL_PRICING.items():
        models.append({
            "id": model_name,
            "name": model_name,
            "pricing": {
                "input_per_1m": pricing["input"],
                "output_per_1m": pricing["output"],
            }
        })
    
    return {
        "success": True,
        "models": models,
        "default": DEFAULT_MODEL,
    }


@app.get("/api/languages")
async def get_languages():
    
    languages = [
        {"code": "es", "name": "Espanhol"},
        {"code": "pt", "name": "Português"},
        {"code": "fr", "name": "Francês"},
        {"code": "de", "name": "Alemão"},
        {"code": "it", "name": "Italiano"},
        {"code": "nl", "name": "Holandês"},
        {"code": "pl", "name": "Polonês"},
        {"code": "sv", "name": "Sueco"},
        {"code": "da", "name": "Dinamarquês"},
        {"code": "no", "name": "Norueguês"},
        {"code": "fi", "name": "Finlandês"},
        {"code": "cs", "name": "Tcheco"},
        {"code": "hu", "name": "Húngaro"},
        {"code": "ro", "name": "Romeno"},
        {"code": "hr", "name": "Croata"},
        {"code": "sr", "name": "Sérvio (Latinizado)"},
        {"code": "tr", "name": "Turco"},
        {"code": "id", "name": "Indonésio"},
        {"code": "tl", "name": "Filipino (Tagalog)"},
        {"code": "ms", "name": "Malaio"},
    ]
    
    return {
        "success": True,
        "languages": languages,
        "source_language": "en",
        "source_language_name": "Inglês",
    }


@app.get("/api/jobs")
async def list_all_jobs():
    
    jobs = list_jobs()
    return {
        "success": True,
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
            }
            for job in jobs
        ],
        "total": len(jobs),
    }


@app.delete("/api/translate/{job_id}")
async def delete_translation_job(job_id: str):
    
    deleted = delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")
    
    return {
        "success": True,
        "message": f"Job {job_id} removido",
    }


@app.post("/api/translate/{job_id}/save")
async def save_translation_result(job_id: str, filename: Optional[str] = None):
    
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")
    
    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job ainda não concluído. Status: {job.status}"
        )
    
    if not job.result_data:
        raise HTTPException(status_code=500, detail="Resultado não disponível")
    

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    

    if not filename:
        target_lang = getattr(job, 'config', None)
        if target_lang and hasattr(target_lang, 'target_language'):
            lang = target_lang.target_language
        else:
            lang = 'unknown'
        filename = f"translated_{job_id[:8]}_{lang}.json"
    

    if not filename.endswith('.json'):
        filename += '.json'
    
    output_path = output_dir / filename
    

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(job.result_data, f, ensure_ascii=False, indent=2)
        
        file_size = output_path.stat().st_size
        
        return {
            "success": True,
            "filename": filename,
            "path": str(output_path),
            "size": file_size,
            "size_kb": round(file_size / 1024, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")


def extract_language_from_filename(filename: str) -> Optional[str]:
    

    name_without_ext = filename.replace('.json', '')
    

    language_codes = ["es", "pt", "fr", "de", "it", "nl", "pl", "sv", "da", "no", 
                     "fi", "cs", "hu", "ro", "hr", "sr", "tr", "id", "tl", "ms"]
    

    for lang_code in language_codes:
        if name_without_ext.endswith(f"_{lang_code}"):
            return lang_code
    
    return None


def get_language_name(lang_code: Optional[str]) -> Optional[str]:
    
    if not lang_code:
        return None
    
    language_map = {
        "es": "Espanhol",
        "pt": "Português",
        "fr": "Francês",
        "de": "Alemão",
        "it": "Italiano",
        "nl": "Holandês",
        "pl": "Polonês",
        "sv": "Sueco",
        "da": "Dinamarquês",
        "no": "Norueguês",
        "fi": "Finlandês",
        "cs": "Tcheco",
        "hu": "Húngaro",
        "ro": "Romeno",
        "hr": "Croata",
        "sr": "Sérvio (Latinizado)",
        "tr": "Turco",
        "id": "Indonésio",
        "tl": "Filipino (Tagalog)",
        "ms": "Malaio",
    }
    
    return language_map.get(lang_code)


@app.get("/api/files")
async def list_translated_files():
    
    output_dir = Path("output")
    
    if not output_dir.exists():
        return {
            "success": True,
            "files": [],
            "total": 0,
        }
    
    files = []
    for file_path in output_dir.glob("*.json"):
        if file_path.name == ".gitkeep":
            continue
        
        try:
            stat = file_path.stat()
            

            lang_code = extract_language_from_filename(file_path.name)
            lang_name = get_language_name(lang_code)
            
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 2),
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "language_code": lang_code,
                "language_name": lang_name,
            })
        except Exception:
            continue
    

    files.sort(key=lambda x: x["modified"], reverse=True)
    
    return {
        "success": True,
        "files": files,
        "total": len(files),
    }


@app.get("/api/files/{filename}")
async def get_translated_file(filename: str):
    
    output_dir = Path("output")
    file_path = output_dir / filename
    

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Arquivo {filename} não encontrado")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail=f"{filename} não é um arquivo")
    

    if not str(file_path.resolve()).startswith(str(output_dir.resolve())):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "success": True,
            "filename": filename,
            "data": data,
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Arquivo JSON inválido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler arquivo: {str(e)}")


@app.get("/api/files/{filename}/download")
async def download_translated_file(filename: str):
    
    output_dir = Path("output")
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Arquivo {filename} não encontrado")
    

    if not str(file_path.resolve()).startswith(str(output_dir.resolve())):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/json',
    )


@app.delete("/api/files/{filename}")
async def delete_translated_file(filename: str):
    
    output_dir = Path("output")
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Arquivo {filename} não encontrado")
    

    if not str(file_path.resolve()).startswith(str(output_dir.resolve())):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        file_path.unlink()
        return {
            "success": True,
            "message": f"Arquivo {filename} removido",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover arquivo: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

