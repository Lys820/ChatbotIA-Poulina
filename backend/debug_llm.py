#!/usr/bin/env python
"""
DEBUG : Teste Claude LLM directement
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, '.')
from app.services.llm_service import create_llm
from app.core.config import get_settings

async def test():
    settings = get_settings()
    print(f"LLM_PROVIDER: {settings.LLM_PROVIDER}")
    print(f"MISTRAL_API_KEY: {'✓' if settings.MISTRAL_API_KEY else '❌'}")
    
    try:
        llm = create_llm(settings.LLM_PROVIDER, settings)
        print(f"✓ LLM créé : {llm.provider}")
        
        context = """
        Centre d'élevage : Tunis
        Type production : Poulet de chair
        Meilleure souche identifiée : Cobb 500
        Biosécurité : 8.5/10
        Taux mortalité : 2.1%
        """
        
        question = "Quelle souche recommandes-tu ?"
        
        print(f"\nGénération réponse...")
        answer = await llm.generate(question, context)
        print(f"\n✓ Réponse reçue ({len(answer)} caractères):")
        print(f"\n{answer[:300]}...")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())