"""
Poulina AI Chatbot – Backend FastAPI
Architecture API-first : aucune donnée locale, modèle ML interchangeable
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, analyses, souches, labos, health, data, recommendation

app = FastAPI(
    title="Poulina AI Chatbot API",
    description="RAG + ML interchangeable pour recommandation souche/labo",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "https://poulina.app"],  # Angular dev + prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,    prefix="/api/v1", tags=["health"])
app.include_router(chat.router,      prefix="/api/v1", tags=["chat"])
app.include_router(analyses.router,  prefix="/api/v1", tags=["analyses"])
app.include_router(souches.router,   prefix="/api/v1", tags=["souches"])
app.include_router(labos.router,     prefix="/api/v1", tags=["labos"])
app.include_router(data.router,          prefix="/api/v1", tags=["data"])
app.include_router(recommendation.router, prefix="/api/v1", tags=["recommendations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)