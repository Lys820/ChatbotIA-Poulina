"""
Configuration centralisée - Variables d'environnement pour SQL Server
"""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    
    # LLM Provider
    LLM_PROVIDER: str = ""
    
    # Security
    ANTHROPIC_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    GENAI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"

    # ML Model
    ML_MODEL: Literal["random_forest", "gradient_boosting", "xgboost", "auto"] = "auto"
    
    # RAG
    TOP_K: int = 5
    EMBEDDING_METHOD: Literal["tfidf", "bm25", "sentence_transformers"] = "tfidf"
    
    # SQL Server Database
    SQLSERVER_SERVER: str = r""
    SQLSERVER_DATABASE: str = ""
    SQLSERVER_DRIVER: str = ""
    Trusted_Connection: str = "yes"
    
    # Redis
    REDIS_URL: str = ""
    CACHE_TTL_HOURS: int = 2
    MEMORY_ENABLED: bool = True
    
    # CSV Upload
    MAX_CSV_SIZE_MB: int = 50  
    
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256" 
    JWT_EXPIRE_MINUTES: int = ""


    class Config:
        env_file = "backend/.env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


