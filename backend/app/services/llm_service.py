"""
LLM Service – Provider interchangeable : Claude / Mistral / OpenAI.

Utilise l'API Anthropic en priorité (config LLM_PROVIDER=claude).
Fallback automatique si la clé est absente.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Tu es l'assistant IA de Poulina, expert en élevage de volailles en Tunisie.
Tu analyses les données des centres d'élevage ET des laboratoires partenaires
pour aider les responsables à prendre les meilleures décisions.

## Tes capacités
- Identifier la meilleure souche pour chaque centre d'élevage (avec prédiction ML)
- Détecter et prévenir les maladies critiques (Salmonelle, Newcastle, Mycoplasme, Gumboro…)
- Recommander le meilleur laboratoire selon : distance, disponibilité, compétences, coût, urgence
- Évaluer la conformité des analyses et signaler les anomalies
- Identifier les centres potentiellement contaminés en cas de maladie critique
- Estimer la fréquence d'analyse recommandée selon la situation sanitaire
- Calculer le coût estimé d'un changement de souche

## Pour les recommandations de laboratoire, tu tiens compte de (ordre de priorité) :
1. Urgence : délai urgence et acceptation
2. Distance aux centres concernés
3. Disponibilité immédiate (slots, délai prochain RDV)
4. Compétences : spécialités, équipements PCR/ELISA/Séquençage, maladies traitées
5. Fiabilité : taux de réussite, satisfaction, années d'expérience
6. Score ML (tier Excellent / Bon / Passable)
7. Coût en TND

## Règles impératives
- Base-toi UNIQUEMENT sur le contexte fourni.
- Si l'information est absente, dis-le clairement et suggère quoi faire.
- Hors sujet : réponds exactement « Je ne peux pas répondre à cette question car elle est hors de mon domaine. »
- Sois concis et actionnable. Structure ta réponse avec des sections claires si elle est longue.
- Réponds en français.
- Pour les maladies critiques (Salmonelle, Newcastle), déclenche une alerte explicite en début de réponse.
""".strip()


class AbstractLLM(ABC):
    @abstractmethod
    async def generate(self, user_message: str, context: str) -> str: ...

    @property
    @abstractmethod
    def provider(self) -> str: ...


class ClaudeLLM(AbstractLLM):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    @property
    def provider(self) -> str:
        return f"Claude ({self._model})"

    async def generate(self, user_message: str, context: str) -> str:
        full_user = f"Contexte (données Poulina) :\n{context}\n\n---\nQuestion : {user_message}"
        resp = await self._client.messages.create(
            model=self._model,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": full_user}],
        )
        return resp.content[0].text


class MistralLLM(AbstractLLM):
    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        try:
            from mistralai.client import MistralClient
            self._client = MistralClient(api_key=api_key)
            self._model = model
            self._available = True
        except ImportError:
            log.warning("Mistral not available, will use fallback")
            self._available = False

    @property
    def provider(self) -> str:
        return f"Mistral ({self._model})" if self._available else "Mistral (unavailable)"

    async def generate(self, user_message: str, context: str) -> str:
        if not self._available:
            raise RuntimeError("Mistral not installed")
        from mistralai.models import ChatMessage
        full_user = f"Contexte (données Poulina) :\n{context}\n\n---\nQuestion : {user_message}"
        resp = self._client.chat(
            model=self._model,
            messages=[
                ChatMessage(role="system", content=SYSTEM_PROMPT),
                ChatMessage(role="user", content=full_user),
            ],
        )
        return resp.choices[0].message.content


class OpenAILLM(AbstractLLM):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    @property
    def provider(self) -> str:
        return f"OpenAI ({self._model})"

    async def generate(self, user_message: str, context: str) -> str:
        full_user = f"Contexte (données Poulina) :\n{context}\n\n---\nQuestion : {user_message}"
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_user},
            ],
            max_tokens=1500,
        )
        return resp.choices[0].message.content


def create_llm(provider: str, settings) -> AbstractLLM:
    """Factory LLM – choisit le provider selon la config."""
    if provider == "claude" and settings.ANTHROPIC_API_KEY:
        return ClaudeLLM(settings.ANTHROPIC_API_KEY)
    if provider == "mistral" and settings.MISTRAL_API_KEY:
        return MistralLLM(settings.MISTRAL_API_KEY)
    if provider == "openai" and settings.OPENAI_API_KEY:
        return OpenAILLM(settings.OPENAI_API_KEY)
    # Fallback automatique
    if settings.ANTHROPIC_API_KEY:
        log.warning("Fallback sur Claude (provider '%s' indisponible)", provider)
        return ClaudeLLM(settings.ANTHROPIC_API_KEY)
    if settings.MISTRAL_API_KEY:
        return MistralLLM(settings.MISTRAL_API_KEY)
    raise RuntimeError("Aucune clé API LLM configurée. Définir ANTHROPIC_API_KEY ou MISTRAL_API_KEY.")