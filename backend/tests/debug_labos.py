#!/usr/bin/env python
"""
DEBUG LABOS – Appelle exactement get_labos_data() depuis l'app
pour voir l'erreur SQL réelle
"""
import sys
import logging
logging.basicConfig(level=logging.DEBUG)

sys.path.insert(0, '..')  # remonte à la racine du backend

from dotenv import load_dotenv
load_dotenv('../.env')  # ajuste si ton .env est ailleurs

from backend.app.core.config import get_settings
from backend.app.data.database import get_db

settings = get_settings()
print(f"DSN: {settings.ORACLE_DSN}")
print(f"USER: {settings.ORACLE_USER}")

db = get_db(settings)
db.connect()

print("\n--- get_analyses_data ---")
df_a = db.get_analyses_data()
print(f"Résultat: {len(df_a)} lignes")

print("\n--- get_labos_data ---")
try:
    # Patch pour voir l'erreur sans catch
    import pandas as pd
    query = """
    SELECT
        l.ID_LABO,
        l.NOM_LABO AS nom_laboratoire,
        l.GOUVERNORAT AS ville,
        l.GOUVERNORAT AS region,
        l.LATITUDE, l.LONGITUDE, l.TELEPHONE, l.EMAIL, l.ACTIF,
        COUNT(DISTINCT lab.ID_LABORANTIN) AS nb_laborantins,
        COALESCE(ROUND(AVG(sl.TAUX_CONFORMITE),1), 95) AS taux_reussite_pct,
        COALESCE(SUM(sl.NB_ANALYSES_EFFECTUEES), 0) AS nb_analyses_effectuees,
        COALESCE(ROUND(AVG(sl.DUREE_MOY_JOURS),1), 3) AS delai_standard_jours,
        CASE
            WHEN COALESCE(ROUND(AVG(sl.DUREE_MOY_JOURS),1),3) <= 2 THEN 12
            WHEN COALESCE(ROUND(AVG(sl.DUREE_MOY_JOURS),1),3) <= 3 THEN 18
            ELSE 24
        END AS delai_urgence_heures,
        1 AS accepte_urgence,
        1 AS certifie_iso,
        1 AS equipement_pcr,
        1 AS equipement_elisa,
        COALESCE(MAX(lab.ANNEES_EXPERIENCE), 5) AS annees_experience_labo,
        ROUND(8.0 + (COALESCE(ROUND(AVG(sl.TAUX_CONFORMITE),1),95) / 100.0) * 1.5, 1) AS score_global,
        CASE
            WHEN ROUND(8.0+(COALESCE(ROUND(AVG(sl.TAUX_CONFORMITE),1),95)/100.0)*1.5,1) >= 9.0 THEN 'Excellent'
            WHEN ROUND(8.0+(COALESCE(ROUND(AVG(sl.TAUX_CONFORMITE),1),95)/100.0)*1.5,1) >= 8.0 THEN 'Bon'
            ELSE 'Passable'
        END AS tier_labo,
        'Prive' AS type_laboratoire,
        'PCR, Virologie, Bacteriologie' AS specialites_principales,
        'Salmonelle, Newcastle, Gumboro' AS maladies_avicoles_traitees
    FROM LABORATOIRE l
    LEFT JOIN LABORANTIN lab ON l.ID_LABO = lab.ID_LABO
    LEFT JOIN STAT_LABORANTIN sl ON lab.ID_LABORANTIN = sl.ID_LABORANTIN
    WHERE l.ACTIF = 1
    GROUP BY l.ID_LABO, l.NOM_LABO, l.GOUVERNORAT, l.LATITUDE, l.LONGITUDE, l.TELEPHONE, l.EMAIL, l.ACTIF
    ORDER BY score_global DESC
    """
    df_l = pd.read_sql(query, db._conn)
    print(f"✓ {len(df_l)} labos")
except Exception as e:
    print(f"❌ ERREUR EXACTE: {type(e).__name__}: {e}")

db.close()