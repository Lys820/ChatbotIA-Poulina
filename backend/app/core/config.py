"""
Configuration centralisée – toutes les variables d'environnement ici
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    
    # ── LLM ──────────────────────────────────────────────────────────────
    LLM_PROVIDER: Literal["claude", "mistral", "openai", "genai"] = ""
    # charge depuis .env : LLM_PROVIDER=claude ou mistral ou openai
    

    # ── ML Model ─────────────────────────────────────────────────────────
    # Modèle interchangeable sans toucher au code métier
    ML_MODEL: Literal["random_forest", "gradient_boosting", "xgboost", "auto"] = "auto"
    # "auto" = teste plusieurs modèles et garde le meilleur (AutoML léger)

    # ── Oracle DB ────────────────────────────────────────────────────────
    ORACLE_DSN: str = ""
    ORACLE_USER: str = ""
    ORACLE_PASSWORD: str = ""

    # ── CSV (upload via API) ──────────────────────────────────────────────
    # Plus de chemins locaux : les CSV arrivent via l'endpoint /api/v1/analyses/upload
    MAX_CSV_SIZE_MB: int = 50

    # ── RAG ──────────────────────────────────────────────────────────────
    TOP_K: int = 5
    EMBEDDING_METHOD: Literal["tfidf", "bm25", "sentence_transformers"] = "tfidf"
    # tfidf  = rapide, pas de GPU
    # bm25   = meilleur recall sur texte structuré
    # sentence_transformers = meilleure qualité sémantique (GPU optionnel)

    # ── Cache (Redis si dispo, sinon in-memory) ───────────────────────────
    REDIS_URL: str = ""  # vide = cache in-memory (TTLCache)
    CACHE_TTL_SECONDS: int = 3600

    # ── Sécurité ──────────────────────────────────────────────────────────
    API_KEY_HEADER: str = "X-Poulina-Key"
    GENAI_API_KEY: str = ""  # vide = pas d'auth (dev), obligatoire en prod
    #MISTRAL_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()