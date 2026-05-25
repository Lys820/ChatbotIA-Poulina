"""
Chat endpoint – Point d'entrée RAG + ML + LLM
"""
import logging
import time
from fastapi import APIRouter, Depends
from typing import Optional
from app.core.config import get_settings
from app.ml.model_factory import model_registry
from app.services.rag_service import rag_service
from app.services.llm_service import create_llm
from app.services.memory_service import get_memory_service

log = logging.getLogger(__name__)
router = APIRouter()


from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    question: str = Field(..., description="Question utilisateur", min_length=3, max_length=500)
    session_id: Optional[str] = Field(None, description="ID session pour mémoire")
    predict_souche: Optional[dict] = Field(None, description="Features souche optionnelles")
    filtre_centre: Optional[str] = None
    filtre_ville: Optional[str] = None
    force_collection: Optional[str] = None

class ChatResponse(BaseModel):
    question: str
    answer: str
    session_id: str  # Retourner session_id au client
    retrieved_analyses: list
    retrieved_labos: list
    souche_prediction: Optional[dict] = None
    model_used: str
    execution_time_ms: float
    memory_context_used: bool = False  # Indique si historique a été utilisé


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, settings=Depends(get_settings)):
    """
    Chat endpoint avec mémoire conversation.
    
    Flow:
    1. Initialise ou récupère session
    2. Récupère contexte historique si exists
    3. Retrieve RAG + ML
    4. Enrichit prompt LLM avec historique
    5. Génère réponse
    6. Enregistre en mémoire Redis
    7. Retourne réponse + session_id
    """
    t0 = time.time()
    memory_used = False

    # 1. Gestion session
    memory_service = get_memory_service()
    
    if not req.session_id:
        # Créer nouvelle session
        session_id = memory_service.create_session()
        log.info(f"Nouvelle session: {session_id}")
    else:
        session_id = req.session_id
        log.info(f"Session existante: {session_id}")

    # 2. Récupère historique si mémoire activée
    history_context = ""
    if settings.MEMORY_ENABLED and memory_service.is_available():
        history_context = memory_service.get_context_window(
            session_id=session_id,
            num_messages=3,  # Derniers 3 exchanges
            include_metadata=True
        )
        if history_context:
            memory_used = True
            log.debug(f"Historique récupéré: {len(history_context)} chars")

    # Vérifier RAG ready
    if not rag_service.is_ready:
        return ChatResponse(
            question=req.question,
            answer="Erreur : RAG non initialisé. Upload CSV via /analyses/upload d'abord",
            session_id=session_id,
            retrieved_analyses=[],
            retrieved_labos=[],
            model_used="N/A",
            execution_time_ms=time.time() - t0,
            memory_context_used=False,
        )

    # 3. Retrieve RAG
    chunks_a, chunks_l = rag_service.retrieve(
        req.question,
        force=req.force_collection,
        filtre_centre=req.filtre_centre,
        filtre_ville=req.filtre_ville,
    )

    # 4. ML prediction (optionnel)
    pred_souche = None
    if req.predict_souche and model_registry._souche_model:
        try:
            pred_souche = model_registry.predict_souche(req.predict_souche)
        except Exception as e:
            log.warning(f"Prédiction échouée: {e}")

    # 5. Build context enrichi avec historique
    context_parts = []

    if history_context:
        context_parts.append("=== HISTORIQUE CONVERSATION ===")
        context_parts.append(history_context)
        context_parts.append("")

    if pred_souche:
        context_parts.append("=== PRÉDICTION ML ===")
        context_parts.append(f"Souche: {pred_souche['souche']} ({pred_souche['confiance_pct']}%)")
        context_parts.append("")

    if chunks_a:
        context_parts.append("=== DONNÉES ANALYSES ===")
        for i, r in enumerate(chunks_a, 1):
            context_parts.append(f"[{i}] {r['text'][:200]}")

    if chunks_l:
        context_parts.append("=== LABORATOIRES ===")
        for i, r in enumerate(chunks_l, 1):
            context_parts.append(f"[{i}] {r['metadata'].get('nom_laboratoire', 'N/A')}")

    context = "\n".join(context_parts) if context_parts else "Pas de contexte"

    # 6. LLM generation
    try:
        llm = create_llm(settings.LLM_PROVIDER, settings)
        answer = await llm.generate(req.question, context)
        model_name = llm.provider
    except Exception as e:
        log.error(f"LLM génération échouée: {e}")
        answer = f"Erreur LLM : {str(e)}"
        model_name = "N/A"

    # 7. Enregistre en mémoire
    if settings.MEMORY_ENABLED and memory_service.is_available():
        try:
            memory_service.add_exchange(
                session_id=session_id,
                question=req.question,
                answer=answer,
                metadata={
                    "model_used": model_name,
                    "centres_count": len(chunks_a),
                    "labos_count": len(chunks_l),
                    "has_ml_prediction": pred_souche is not None,
                    "execution_ms": round(time.time() - t0, 2),
                }
            )
        except Exception as e:
            log.warning(f"Erreur enregistrement mémoire: {e}")

    return ChatResponse(
        question=req.question,
        answer=answer,
        session_id=session_id,
        retrieved_analyses=[{"score": r["score"], "text": r["text"][:200]} for r in chunks_a],
        retrieved_labos=[{"score": r["score"], "nom": r["metadata"].get("nom_laboratoire")} for r in chunks_l],
        souche_prediction=pred_souche,
        model_used=model_name,
        execution_time_ms=round(time.time() - t0, 2),
        memory_context_used=memory_used,
    )
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