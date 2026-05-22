"""
Analyses upload - Recharge CSV et entraîne ML à chaud
Fonctionne avec SQL Server
"""
import logging
from fastapi import APIRouter, UploadFile, Depends, HTTPException
import pandas as pd
import io

from app.ml.model_factory import model_registry
from app.services.rag_service import rag_service
from app.core.config import get_settings
from app.data.database import get_db

log = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyses/upload")
async def upload_analyses(
    file_analyses: UploadFile,
    file_labos: UploadFile,
):
    """
    Upload 2 CSV (analyses + labos) et réentraîne tout à chaud.
    """
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
            "message": "CSV charge, ML entraîne, RAG indexe",
            "analyses": rag_results["analyses"],
            "labos": rag_results["labos"],
            "model_status": {
                "souche": ml_results.get("souche", {}),
                "labo": ml_results.get("labo", {}),
            },
            "trained_at": model_registry._trained_at,
        }

    except Exception as e:
        log.error(f"Upload/training error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyses/train-from-sqlserver")
async def train_from_sqlserver(settings=Depends(get_settings)):
    """
    Entraîne directement depuis SQL Server DB.
    """
    if not settings.SQLSERVER_SERVER or not settings.SQLSERVER_DATABASE:
        raise HTTPException(
            status_code=400,
            detail="SQL Server non configure. Definir SQLSERVER_SERVER, SQLSERVER_DATABASE, SQLSERVER_USER, SQLSERVER_PASSWORD dans .env"
        )

    db = get_db(settings)
    log.info("Connexion SQL Server...")

    if not db.connect():
        raise HTTPException(
            status_code=500,
            detail="Impossible de se connecter a SQL Server. Verifie les credentials dans .env"
        )

    try:
        log.info("Recuperation des donnees SQL Server...")
        df_analyses, df_labos = db.get_all_data()
    finally:
        db.close()

    log.info(f"SQL Server: {len(df_analyses)} analyses, {len(df_labos)} labos")

    if df_analyses.empty:
        raise HTTPException(
            status_code=400,
            detail=f"get_analyses_data() a retourne 0 lignes. Verifie les logs serveur pour l'erreur SQL."
        )
    if df_labos.empty:
        raise HTTPException(
            status_code=400,
            detail=f"get_labos_data() a retourne 0 lignes. Verifie les logs serveur pour l'erreur SQL."
        )

    ml_results = model_registry.train_from_dataframes(
        df_analyses, df_labos, ml_model_name=settings.ML_MODEL,
    )
    rag_results = rag_service.build_from_dataframes(
        df_analyses, df_labos, embedding_method=settings.EMBEDDING_METHOD,
    )

    return {
        "status": "trained_from_sqlserver",
        "message": f"SQL Server: {len(df_analyses)} analyses + {len(df_labos)} labos",
        "analyses": rag_results["analyses"],
        "labos": rag_results["labos"],
        "model_status": {
            "souche": ml_results.get("souche", {}),
            "labo": ml_results.get("labo", {}),
        },
        "trained_at": model_registry._trained_at,
    }