"""
Data endpoint – Requêtes BD directes (sans LLM)
Retourne données brutes JSON
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.config import get_settings
from app.data.database import get_db
from app.data.models import (
    CentreFilter, LaboratoireFilter, SoucheFilter,
    CentreResponse, LaboratoireResponse, SoucheResponse,
)

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/data/centres", response_model=list[CentreResponse])
async def get_centres(
    gouvernorat: str = Query(None, description="Filtre par gouvernorat"),
    type_production: str = Query(None, description="Poulet / Oeuf / Dinde"),
    actif: bool = Query(True),
    db = Depends(get_db),
):
    """
    Retourne liste des centres d'élevage.
    Pas de LLM, données brutes.
    """
    try:
        filters = CentreFilter(
            gouvernorat=gouvernorat,
            type_production=type_production,
            actif=actif
        )
        df = db.get_centres(filters)
        return df.to_dict("records")
    except Exception as e:
        log.error(f"Error get_centres: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/labos", response_model=list[LaboratoireResponse])
async def get_labos(
    gouvernorat: str = Query(None),
    accepte_urgence: bool = Query(None),
    certifie_iso: bool = Query(True),
    actif: bool = Query(True),
    db = Depends(get_db),
):
    """Retourne laboratoires avec filtres optionnels"""
    try:
        filters = LaboratoireFilter(
            gouvernorat=gouvernorat,
            accepte_urgence=accepte_urgence,
            certifie_iso=certifie_iso,
            actif=actif
        )
        df = db.get_labos(filters)
        return df.to_dict("records")
    except Exception as e:
        log.error(f"Error get_labos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/souches", response_model=list[SoucheResponse])
async def get_souches(
    type_produit: str = Query(None, description="Poulet / Oeuf / Dinde"),
    fertilite_min: float = Query(None),
    taux_mortalite_max: float = Query(None),
    db = Depends(get_db),
):
    """Retourne souches avec filtres"""
    try:
        filters = SoucheFilter(
            type_produit_final=type_produit,
            fertilite_min=fertilite_min,
            taux_mortalite_max=taux_mortalite_max
        )
        df = db.get_souches(filters)
        return df.to_dict("records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/centre/{centre_id}", response_model=CentreResponse)
async def get_centre_by_id(centre_id: int, db = Depends(get_db)):
    """Détail d'un centre spécifique"""
    try:
        row = db.query_one(f"SELECT * FROM centre_elevage WHERE id_centre = {centre_id}")
        if not row:
            raise HTTPException(status_code=404, detail="Centre not found")
        return row
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/labo/{labo_id}", response_model=LaboratoireResponse)
async def get_labo_by_id(labo_id: int, db = Depends(get_db)):
    """Détail d'un laboratoire"""
    try:
        row = db.query_one(f"SELECT * FROM laboratoire WHERE id_labo = {labo_id}")
        if not row:
            raise HTTPException(status_code=404, detail="Laboratoire not found")
        return row
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/count")
async def get_counts(db = Depends(get_db)):
    """Retourne comptes globaux"""
    try:
        return {
            "centres": db.query_one("SELECT COUNT(*) as count FROM centre_elevage WHERE actif=1")["count"],
            "labos": db.query_one("SELECT COUNT(*) as count FROM laboratoire WHERE actif=1")["count"],
            "souches": db.query_one("SELECT COUNT(*) as count FROM souche")["count"],
            "analyses": db.query_one("SELECT COUNT(*) as count FROM demande_analyse")["count"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))