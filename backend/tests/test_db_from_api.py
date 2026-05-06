#!/usr/bin/env python
"""
TEST DATABASE DEPUIS LE CONTEXTE API
Simule exactement ce que fait l'endpoint /train-from-oracle
"""
import asyncio
import sys
from dotenv import load_dotenv
import os

load_dotenv()

# Simule l'import depuis l'API
sys.path.insert(0, '.')

from app.core.config import get_settings
from app.services.database import get_db

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              TEST DB DEPUIS API CONTEXT                                    ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

try:
    print("\n1️⃣  Chargement settings...")
    settings = get_settings()
    print(f"  ORACLE_DSN: {settings.ORACLE_DSN}")
    print(f"  ORACLE_USER: {settings.ORACLE_USER}")
    print(f"  ORACLE_PASSWORD: {'*' * len(settings.ORACLE_PASSWORD) if settings.ORACLE_PASSWORD else '❌ VIDE'}")
    
    print("\n2️⃣  Création instance DB...")
    db = get_db(settings)
    print(f"  ✓ Instance créée")
    
    print("\n3️⃣  Connexion Oracle...")
    if db.connect():
        print(f"  ✓ Connexion réussie")
    else:
        print(f"  ❌ Connexion échouée")
        sys.exit(1)
    
    print("\n4️⃣  Récupération données analyses...")
    df_analyses = db.get_analyses_data()
    print(f"  ✓ {len(df_analyses)} analyses")
    if not df_analyses.empty:
        print(f"    Colonnes: {list(df_analyses.columns)[:5]}...")
        print(f"    Premier row: {df_analyses.iloc[0].to_dict() if len(df_analyses) > 0 else 'N/A'}")
    else:
        print(f"  ⚠️  DataFrame vide")
    
    print("\n5️⃣  Récupération données labos...")
    df_labos = db.get_labos_data()
    print(f"  ✓ {len(df_labos)} labos")
    if not df_labos.empty:
        print(f"    Colonnes: {list(df_labos.columns)[:5]}...")
    else:
        print(f"  ⚠️  DataFrame vide")
    
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ DB OK depuis API context")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERREUR : {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)