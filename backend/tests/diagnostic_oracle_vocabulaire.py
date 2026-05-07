#!/usr/bin/env python
"""
DIAGNOSTIC ORACLE VOCABULAIRE
Chercher pourquoi mots vides!
Homme caverne parler simple: données mort = robot pas comprendre
"""
import oracledb
import pandas as pd
from dotenv import load_dotenv
import os
import re

load_dotenv()

ORACLE_DSN = os.getenv("ORACLE_DSN")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║         DIAGNOSTIC ORACLE - VOCABULAIRE MORT?                              ║
║         (Pourquoi robot pas trouver mots?)                                 ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

def limiter_texte(texte, max_chars=100):
    """Afficher texte pas trop long"""
    if texte is None:
        return "[NULL]"
    s = str(texte)[:max_chars]
    return s + "..." if len(str(texte)) > max_chars else s

try:
    conn = oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )
    cursor = conn.cursor()
    
    # ========================================================================
    # 1. VÉRIFIER DEMANDE_ANALYSE (principale table)
    # ========================================================================
    print("\n1️⃣  DEMANDE_ANALYSE - Combien de lignes? Vides ou remplies?")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM DEMANDE_ANALYSE")
    count = cursor.fetchone()[0]
    print(f"  Total lignes: {count}")
    
    if count == 0:
        print("  ❌ TABLE VIDE! Robot pas avoir rien à comprendre!")
    else:
        cursor.execute("""
            SELECT 
                ID_DEMANDE,
                NUM_ANALYSE,
                RESULTAT_SOUCHE_DETECTEE,
                RAISON_NON_CONFORMITE,
                OBSERVATIONS
            FROM DEMANDE_ANALYSE 
            WHERE ROWNUM <= 5
        """)
        
        for row in cursor.fetchall():
            print(f"\n  ID: {row[0]}")
            print(f"    NUM_ANALYSE: {limiter_texte(row[1])}")
            print(f"    SOUCHE: {limiter_texte(row[2])}")
            print(f"    RAISON_NON_CONFORM: {limiter_texte(row[3])}")
            print(f"    OBSERVATIONS: {limiter_texte(row[4])}")
    
    # ========================================================================
    # 2. VÉRIFIER SOUCHE (où noms de souches?)
    # ========================================================================
    print("\n\n2️⃣  SOUCHE - Souches disponibles?")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            ID_SOUCHE,
            NOM_SOUCHE,
            TYPE_PRODUIT_FINAL,
            FERTILITE_SCORE,
            TAUX_MORTALITE
        FROM SOUCHE
    """)
    
    souches = cursor.fetchall()
    if len(souches) == 0:
        print("  ❌ AUCUNE SOUCHE! Pas données!")
    else:
        print(f"  ✓ {len(souches)} souches trouvées:")
        for souche in souches:
            print(f"    - {souche[1]} ({souche[2]}): Fertilité={souche[3]}, Mortalité={souche[4]}")
    
    # ========================================================================
    # 3. VÉRIFIER CENTRE_ELEVAGE
    # ========================================================================
    print("\n\n3️⃣  CENTRE_ELEVAGE - Centres existent?")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            ID_CENTRE,
            NOM_CENTRE,
            LOCALISATION,
            TYPE_PRODUCTION
        FROM CENTRE_ELEVAGE
        WHERE ROWNUM <= 5
    """)
    
    centres = cursor.fetchall()
    if len(centres) == 0:
        print("  ❌ AUCUN CENTRE!")
    else:
        print(f"  ✓ Exemples:")
        for centre in centres:
            print(f"    - {centre[1]} ({centre[3]}) à {centre[2]}")
    
    # ========================================================================
    # 4. VÉRIFIER MALADIE
    # ========================================================================
    print("\n\n4️⃣  MALADIE - Maladies connues?")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            ID_MALADIE,
            NOM_MALADIE,
            TYPE_AGENT,
            EST_CRITIQUE
        FROM MALADIE
    """)
    
    maladies = cursor.fetchall()
    if len(maladies) == 0:
        print("  ❌ AUCUNE MALADIE!")
    else:
        print(f"  ✓ {len(maladies)} maladies:")
        for m in maladies:
            critique = "🔴 CRITIQUE" if m[3] == 1 else "⚠️  Normal"
            print(f"    - {m[1]} ({m[2]}) {critique}")
    
    # ========================================================================
    # 5. VÉRIFIER HISTORIQUE_MALADIE
    # ========================================================================
    print("\n\n5️⃣  HISTORIQUE_MALADIE - Historiques existent?")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM HISTORIQUE_MALADIE")
    hist_count = cursor.fetchone()[0]
    print(f"  Total: {hist_count} historiques")
    
    if hist_count > 0:
        cursor.execute("""
            SELECT 
                hm.ID_HISTORIQUE,
                ce.NOM_CENTRE,
                m.NOM_MALADIE,
                hm.DATE_DETECTION,
                hm.EST_RESOLU
            FROM HISTORIQUE_MALADIE hm
            LEFT JOIN CENTRE_ELEVAGE ce ON hm.ID_CENTRE = ce.ID_CENTRE
            LEFT JOIN MALADIE m ON hm.ID_MALADIE = m.ID_MALADIE
            WHERE ROWNUM <= 3
        """)
        print("  Exemples:")
        for h in cursor.fetchall():
            print(f"    - {h[1]}: {h[2]} ({h[3]})")
    
    # ========================================================================
    # 6. VÉRIFIER LABORATOIRE
    # ========================================================================
    print("\n\n6️⃣  LABORATOIRE - Labs existent?")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            ID_LABO,
            NOM_LABO,
            GOUVERNORAT,
            ACTIF
        FROM LABORATOIRE
        WHERE ROWNUM <= 5
    """)
    
    labs = cursor.fetchall()
    if len(labs) == 0:
        print("  ❌ AUCUN LAB!")
    else:
        print(f"  ✓ Exemples:")
        for lab in labs:
            actif = "✓" if lab[3] == 1 else "❌"
            print(f"    {actif} {lab[1]} ({lab[2]})")
    
    # ========================================================================
    # 7. STATISTIQUES GLOBALES
    # ========================================================================
    print("\n\n7️⃣  RÉSUMÉ - Données suffisantes pour IA?")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM CENTRE_ELEVAGE WHERE ACTIF = 1")
    centres_actifs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM BATIMENT WHERE ACTIF = 1")
    batiments_actifs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM LABORATOIRE WHERE ACTIF = 1")
    labs_actifs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM DEMANDE_ANALYSE WHERE STATUT = 'Terminée'")
    analyses_ok = cursor.fetchone()[0]
    
    print(f"\n  📊 DONNÉES DISPONIBLES:")
    print(f"    • Centres actifs: {centres_actifs}")
    print(f"    • Bâtiments actifs: {batiments_actifs}")
    print(f"    • Labos actifs: {labs_actifs}")
    print(f"    • Analyses terminées: {analyses_ok}")
    print(f"    • Souches: {len(souches)}")
    print(f"    • Maladies: {len(maladies)}")
    print(f"    • Historiques: {hist_count}")
    
    # ========================================================================
    # 8. DIAGNOSTIC VOCABULAIRE
    # ========================================================================
    print("\n\n8️⃣  DIAGNOSTIC - Pourquoi vocabulaire vide?")
    print("-" * 70)
    
    problemes = []
    
    if count == 0:
        problemes.append("❌ DEMANDE_ANALYSE vide - pas d'analyses à traiter!")
    
    if centres_actifs == 0:
        problemes.append("❌ CENTRE_ELEVAGE vide - pas de centres!")
    
    if len(souches) == 0:
        problemes.append("❌ SOUCHE vide - pas de souches!")
    
    if labs_actifs == 0:
        problemes.append("❌ LABORATOIRE vide - pas de labs!")
    
    if analyses_ok == 0:
        problemes.append("⚠️  Aucune analyse terminée - résultats manquants!")
    
    if problemes:
        print("\n  PROBLÈMES TROUVÉS:")
        for p in problemes:
            print(f"    {p}")
    else:
        print("\n  ✓ DONNÉES PRÉSENTES! Problème vient d'ailleurs...")
        print("    → Peut-être: données NULL, colonnes vides, ou format bizarre")
    
    # ========================================================================
    # 9. CHECK NULL VALUES
    # ========================================================================
    print("\n\n9️⃣  VÉRIFIER NULL VALUES (données manquantes)")
    print("-" * 70)
    
    if count > 0:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN RESULTAT_SOUCHE_DETECTEE IS NULL THEN 1 ELSE 0 END) as null_souche,
                SUM(CASE WHEN RAISON_NON_CONFORMITE IS NULL THEN 1 ELSE 0 END) as null_raison,
                SUM(CASE WHEN OBSERVATIONS IS NULL THEN 1 ELSE 0 END) as null_obs,
                SUM(CASE WHEN NUM_ANALYSE IS NULL THEN 1 ELSE 0 END) as null_num
            FROM DEMANDE_ANALYSE
        """)
        
        null_counts = cursor.fetchone()
        print(f"\n  Colonnes avec valeurs NULL:")
        print(f"    • RESULTAT_SOUCHE_DETECTEE: {null_counts[0]} / {count} ({100*null_counts[0]//count}%)")
        print(f"    • RAISON_NON_CONFORMITE: {null_counts[1]} / {count} ({100*null_counts[1]//count}%)")
        print(f"    • OBSERVATIONS: {null_counts[2]} / {count} ({100*null_counts[2]//count}%)")
        print(f"    • NUM_ANALYSE: {null_counts[3]} / {count} ({100*null_counts[3]//count}%)")
    
    # ========================================================================
    # 10. CONCLUSION
    # ========================================================================
    print("\n\n" + "=" * 70)
    print("📋 CONCLUSION - Comment fixer vocabulaire?")
    print("=" * 70)
    
    if count > 0 and centres_actifs > 0 and len(souches) > 0:
        print("""
  ✓ DONNÉES EXISTENT!
  
  SOLUTION: Enrichir le context avant embedding!
  
  Moi créer fonction qui:
    1. Lire données Oracle
    2. Combiner colonnes significatives
    3. Enrichir avec noms souches, maladies, centres
    4. Créer "documents" avec vrais mots
    5. Envoyer ça à RAG
    
  Résultat: Robot avoir BEAUCOUP mots, pas vide!
""")
    else:
        print("""
  ❌ DONNÉES MANQUENT OU VIDES!
  
  ACTION REQUISE:
    1. Insérer données de test en Oracle
    2. Ou utiliser CSV fallback
    3. Remplir SOUCHE, CENTRE_ELEVAGE, MALADIE
    4. Créer quelques DEMANDE_ANALYSE
    5. Puis relancer /train-from-oracle
""")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Diagnostic fini")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ ERREUR ORACLE: {e}")
    import traceback
    traceback.print_exc()