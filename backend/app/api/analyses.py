"""
Analyses upload – Recharge CSV et entraîne ML à chaud
"""
import logging
from fastapi import APIRouter, UploadFile, Depends, HTTPException
import pandas as pd
import io

from app.ml.model_factory import model_registry
from app.services.rag_service import rag_service
from app.core.config import get_settings

log = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyses/upload")
async def upload_analyses(
    file_analyses: UploadFile,
    file_labos: UploadFile,
):
    try:
        settings = get_settings()

        content_a = await file_analyses.read()
        df_analyses = pd.read_csv(io.BytesIO(content_a))
        log.info(f"CSV analyses: {len(df_analyses)} lignes")

        content_l = await file_labos.read()
        df_labos = pd.read_csv(io.BytesIO(content_l))
        log.info(f"CSV labos: {len(df_labos)} lignes")

        ml_results = model_registry.train_from_dataframes(
            df_analyses, df_labos, ml_model_name=settings.ML_MODEL,
        )
        rag_results = rag_service.build_from_dataframes(
            df_analyses, df_labos, embedding_method=settings.EMBEDDING_METHOD,
        )

        return {
            "status": "trained",
            "message": "CSV chargé, ML entraîné, RAG indexé",
            "analyses": rag_results["analyses"],
            "labos": rag_results["labos"],
            "model_status": {
                "souche": ml_results.get("souche", {}),
                "labo":   ml_results.get("labo", {}),
            },
            "trained_at": model_registry._trained_at,
        }

    except Exception as e:
        log.error(f"Upload/training error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyses/train-from-oracle")
async def train_from_oracle(settings=Depends(get_settings)):
    """Entraîne directement depuis Oracle DB."""
    from app.services.database import get_db

    if not settings.ORACLE_DSN or not settings.ORACLE_USER:
        raise HTTPException(
            status_code=400,
            detail="Oracle non configuré. Définir ORACLE_DSN + ORACLE_USER + ORACLE_PASSWORD dans .env"
        )

    db = get_db(settings)
    log.info("Connexion Oracle...")

    if not db.connect():
        raise HTTPException(
            status_code=500,
            detail="Impossible de se connecter à Oracle. Vérifie les credentials dans .env"
        )

    try:
        log.info("Récupération des données Oracle...")
        df_analyses, df_labos = db.get_all_data()
    finally:
        db.close()

    log.info(f"Oracle: {len(df_analyses)} analyses, {len(df_labos)} labos")

    if df_analyses.empty:
        raise HTTPException(
            status_code=400,
            detail=f"get_analyses_data() a retourné 0 lignes. Vérifie les logs serveur pour l'erreur SQL."
        )
    if df_labos.empty:
        raise HTTPException(
            status_code=400,
            detail=f"get_labos_data() a retourné 0 lignes. Vérifie les logs serveur pour l'erreur SQL."
        )

    ml_results  = model_registry.train_from_dataframes(
        df_analyses, df_labos, ml_model_name=settings.ML_MODEL,
    )
    rag_results = rag_service.build_from_dataframes(
        df_analyses, df_labos, embedding_method=settings.EMBEDDING_METHOD,
    )

    return {
        "status": "trained_from_oracle",
        "message": f"Oracle: {len(df_analyses)} analyses + {len(df_labos)} labos",
        "analyses": rag_results["analyses"],
        "labos":    rag_results["labos"],
        "model_status": {
            "souche": ml_results.get("souche", {}),
            "labo":   ml_results.get("labo", {}),
        },
        "trained_at": model_registry._trained_at,
    }