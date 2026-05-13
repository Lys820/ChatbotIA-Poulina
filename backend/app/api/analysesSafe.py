
"""
Analyses upload – Recharge CSV et entraîne ML à chaud
"""
import logging
from fastapi import APIRouter, File, UploadFile
import pandas as pd
import io

from app.ml.model_factory import model_registry
from app.services.rag_service import rag_service
from backend.app.core.config import get_settings

log = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyses/upload")
async def upload_analyses(
    file_analyses: UploadFile,
    file_labos: UploadFile,
):
    """
    Upload 2 CSV (analyses + labos) et réentraîne tout à chaud.
    
    - Lis les CSV depuis la requête HTTP (pas de fichier local)
    - Entraîne ML (Random Forest auto-select)
    - Construit l'index RAG
    - Retourne le status
    """
    try:
        settings = get_settings()
        
        # ── Lis les CSV depuis la requête ──────────────────────────────────
        content_a = await file_analyses.read()
        df_analyses = pd.read_csv(io.BytesIO(content_a))
        log.info(f"Loaded analyses CSV: {len(df_analyses)} rows")

        content_l = await file_labos.read()
        df_labos = pd.read_csv(io.BytesIO(content_l))
        log.info(f"Loaded labos CSV: {len(df_labos)} rows")

        # ── Entraîne ML ──────────────────────────────────────────────────────
        ml_results = model_registry.train_from_dataframes(
            df_analyses, df_labos,
            ml_model_name=settings.ML_MODEL,
        )
        log.info(f"ML training done: {ml_results}")

        # ── Construit RAG ────────────────────────────────────────────────────
        rag_results = rag_service.build_from_dataframes(
            df_analyses, df_labos,
            embedding_method=settings.EMBEDDING_METHOD,
        )
        log.info(f"RAG building done: {rag_results}")

        return {
            "status": "trained",
            "message": "CSV chargé, ML entraîné, RAG indexé",
            "analyses": rag_results["analyses"],
            "labos": rag_results["labos"],
            "model_status": {
                "souche": ml_results.get("souche", {}),
                "labo": ml_results.get("labo", {}),
            },
            "trained_at": model_registry._trained_at,
        }

    except Exception as e:
        log.error(f"Upload/training error: {e}")
        return {"status": "error", "message": str(e)}, 500