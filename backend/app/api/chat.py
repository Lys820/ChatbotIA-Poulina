"""
Chat endpoint – Point d'entrée RAG + ML + LLM
"""
import logging
import time
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional

from backend.app.core.config import get_settings
from app.ml.model_factory import model_registry
from app.services.rag_service import rag_service
from app.services.llm_service import create_llm

log = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(..., description="La question en langage naturel")
    predict_souche: Optional[dict] = Field(None, description="Features du centre pour prédire la souche (optionnel)")
    filtre_centre: Optional[str] = None
    filtre_ville: Optional[str] = None
    force_collection: Optional[str] = None  # 'analyses', 'labos', 'both'


class ChatResponse(BaseModel):
    question: str
    answer: str
    retrieved_analyses: list
    retrieved_labos: list
    souche_prediction: Optional[dict] = None
    model_used: str
    execution_time_ms: float


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, settings=Depends(get_settings)):
    """
    Pipeline RAG complet :
    1. Routing (keyword)
    2. TF-IDF retrieval
    3. Random Forest (optionnel)
    4. Mistral/Claude génère la réponse
    """
    t0 = time.time()

    if not rag_service.is_ready:
        return ChatResponse(
            question=req.question,
            answer="Erreur : RAG non initialisé. Upload d'abord un CSV via /analyses/upload",
            retrieved_analyses=[],
            retrieved_labos=[],
            model_used="N/A",
            execution_time_ms=time.time() - t0,
        )

    # 1. Retrieve
    chunks_a, chunks_l = rag_service.retrieve(
        req.question,
        force=req.force_collection,
        filtre_centre=req.filtre_centre,
        filtre_ville=req.filtre_ville,
    )

    # 2. ML prediction (optionnel)
    pred_souche = None
    if req.predict_souche and model_registry._souche_model:
        try:
            pred_souche = model_registry.predict_souche(req.predict_souche)
        except Exception as e:
            log.warning(f"Prédiction souche échouée: {e}")

    # 3. Score labos avec Random Forest
    if req.predict_souche and model_registry._labo_model:
        import pandas as pd
        try:
            df_labos_scored = model_registry.score_labos(
                pd.DataFrame([r["metadata"] for r in chunks_l])
            )
            # Intégrer tier_rf dans metadata
            for i, r in enumerate(chunks_l):
                if i < len(df_labos_scored):
                    r["metadata"]["tier_rf"] = df_labos_scored.iloc[i].get("tier_rf", "N/A")
        except Exception as e:
            log.warning(f"Scoring labos échoué: {e}")

    # 4. Build context
    context_parts = []
    if pred_souche:
        context_parts.append(f"=== PRÉDICTION ML – SOUCHE ===\nSouche: {pred_souche['souche']} (confiance: {pred_souche['confiance_pct']}%)\nModel: {pred_souche['model']}\nAlternatives: {pred_souche['alternatives']}\n")

    if chunks_a:
        context_parts.append("=== DONNÉES ANALYSES / SOUCHES ===")
        for i, r in enumerate(chunks_a, 1):
            context_parts.append(f"\n[Analyse {i} - score {r['score']}]")
            context_parts.append(r["text"])

    if chunks_l:
        context_parts.append("\n=== DONNÉES LABORATOIRES ===")
        for i, r in enumerate(chunks_l, 1):
            tier = r["metadata"].get("tier_rf", "")
            tier_str = f" | Tier ML: {tier}" if tier else ""
            context_parts.append(f"\n[Labo {i} - score {r['score']}{tier_str}]")
            context_parts.append(r["text"])

    context = "\n".join(context_parts) if context_parts else "Aucune donnée pertinente trouvée."

    # 5. LLM generation
    try:
        llm = create_llm(settings.LLM_PROVIDER, settings)
        answer = await llm.generate(req.question, context)
        model_name = llm.provider
    except Exception as e:
        log.error(f"LLM génération échouée: {e}")
        answer = f"Erreur LLM : {str(e)}"
        model_name = "N/A"

    return ChatResponse(
        question=req.question,
        answer=answer,
        retrieved_analyses=[{"score": r["score"], "text": r["text"][:200]} for r in chunks_a],
        retrieved_labos=[{"score": r["score"], "nom": r["metadata"].get("nom_laboratoire")} for r in chunks_l],
        souche_prediction=pred_souche,
        model_used=model_name,
        execution_time_ms=round(time.time() - t0, 2),
    )