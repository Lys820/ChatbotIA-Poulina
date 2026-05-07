#!/usr/bin/env python
"""
DEBUG QUERY – Lance exactement les requêtes de database.py et affiche l'erreur précise
"""
import oracledb
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

conn = oracledb.connect(
    user=os.getenv("ORACLE_USER"),
    password=os.getenv("ORACLE_PASSWORD"),
    dsn=os.getenv("ORACLE_DSN")
)
print("✓ Connexion OK\n")

# ── Test query analyses ────────────────────────────────────────────────────
print("=" * 60)
print("TEST QUERY ANALYSES")
print("=" * 60)

query_analyses = """
SELECT
    da.ID_DEMANDE,
    da.NUM_ANALYSE,
    ce.ID_CENTRE                            AS id_centre,
    ce.NOM_CENTRE                           AS nom_centre,
    ce.GOUVERNORAT                          AS ville,
    ce.TYPE_PRODUCTION                      AS type_production,
    b.ID_BATIMENT,
    s.NOM_SOUCHE                            AS meilleure_souche,
    s.FERTILITE_SCORE                       AS fertilite_visee,
    s.TAUX_MORTALITE,
    ta.CODE_ANALYSE                         AS type_analyse,
    da.TYPE_ECHANTILLON,
    da.DATE_PRELEVEMENT,
    da.DATE_ANALYSE,
    da.PRIORITE,
    da.EST_CONFORME                         AS conforme,
    da.POURCENTAGE_SECURITE,
    da.STATUT,
    da.RESULTAT_SOUCHE_DETECTEE,
    da.NIVEAU_SATISFACTION,
    CASE
        WHEN TO_CHAR(da.DATE_PRELEVEMENT,'MM') IN ('06','07','08') THEN 'Ete'
        WHEN TO_CHAR(da.DATE_PRELEVEMENT,'MM') IN ('03','04','05') THEN 'Printemps'
        WHEN TO_CHAR(da.DATE_PRELEVEMENT,'MM') IN ('09','10','11') THEN 'Automne'
        ELSE 'Hiver'
    END                                     AS saison,
    b.CAPACITE,
    ROUND(DBMS_RANDOM.VALUE(4.5,6.5),2)    AS cout_aliment,
    ROUND(DBMS_RANDOM.VALUE(20,40),1)      AS temperature_moyenne,
    ROUND(DBMS_RANDOM.VALUE(40,70),0)      AS humidite,
    ROUND(DBMS_RANDOM.VALUE(85,95),0)      AS biosecurite_score,
    ROUND(DBMS_RANDOM.VALUE(5,30),0)       AS experience_equipe,
    ROUND(DBMS_RANDOM.VALUE(5,30),0)       AS distance_labo,
    ROUND(DBMS_RANDOM.VALUE(30000,100000),0) AS budget
FROM DEMANDE_ANALYSE da
LEFT JOIN CENTRE_ELEVAGE ce  ON da.ID_CENTRE      = ce.ID_CENTRE
LEFT JOIN BATIMENT b         ON da.ID_BATIMENT     = b.ID_BATIMENT
LEFT JOIN SOUCHE s           ON b.ID_SOUCHE        = s.ID_SOUCHE
LEFT JOIN TYPE_ANALYSE ta    ON da.ID_TYPE_ANALYSE = ta.ID_TYPE_ANALYSE
WHERE ce.ACTIF = 1
  AND ROWNUM <= 100
"""

try:
    df = pd.read_sql(query_analyses, conn)
    df.columns = [c.lower() for c in df.columns]
    print(f"✓ {len(df)} lignes retournées")
    print(f"  Colonnes: {list(df.columns)}")
    if len(df) > 0:
        print(f"  Première ligne: {df.iloc[0][['id_centre','nom_centre','meilleure_souche','conforme']].to_dict()}")
except Exception as e:
    print(f"❌ ERREUR: {type(e).__name__}: {e}")

# ── Test query labos ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TEST QUERY LABOS")
print("=" * 60)

query_labos = """
SELECT
    l.ID_LABO,
    l.NOM_LABO                                        AS nom_laboratoire,
    l.GOUVERNORAT                                     AS ville,
    l.GOUVERNORAT                                     AS region,
    l.LATITUDE,
    l.LONGITUDE,
    l.ACTIF,
    COUNT(DISTINCT lab.ID_LABORANTIN)                 AS nb_laborantins,
    COALESCE(ROUND(AVG(sl.TAUX_CONFORMITE),1), 95)   AS taux_reussite_pct,
    COALESCE(SUM(sl.NB_ANALYSES_EFFECTUEES), 0)      AS nb_analyses_effectuees,
    COALESCE(ROUND(AVG(sl.DUREE_MOY_JOURS),1), 3)   AS delai_standard_jours,
    CASE
        WHEN COALESCE(ROUND(AVG(sl.DUREE_MOY_JOURS),1),3) <= 2 THEN 12
        WHEN COALESCE(ROUND(AVG(sl.DUREE_MOY_JOURS),1),3) <= 3 THEN 18
        ELSE 24
    END                                               AS delai_urgence_heures,
    1                                                 AS accepte_urgence,
    1                                                 AS certifie_iso,
    COALESCE(MAX(lab.ANNEES_EXPERIENCE), 5)           AS annees_experience_labo,
    ROUND(
        8.0 + (COALESCE(ROUND(AVG(sl.TAUX_CONFORMITE),1),95) / 100.0) * 1.5,
        1
    )                                                 AS score_global,
    CASE
        WHEN ROUND(8.0+(COALESCE(ROUND(AVG(sl.TAUX_CONFORMITE),1),95)/100.0)*1.5,1) >= 9.0 THEN 'Excellent'
        WHEN ROUND(8.0+(COALESCE(ROUND(AVG(sl.TAUX_CONFORMITE),1),95)/100.0)*1.5,1) >= 8.0 THEN 'Bon'
        ELSE 'Passable'
    END                                               AS tier_labo,
    'Prive'                                           AS type_laboratoire
FROM LABORATOIRE l
LEFT JOIN LABORANTIN lab     ON l.ID_LABO          = lab.ID_LABO
LEFT JOIN STAT_LABORANTIN sl ON lab.ID_LABORANTIN  = sl.ID_LABORANTIN
WHERE l.ACTIF = 1
GROUP BY l.ID_LABO, l.NOM_LABO, l.GOUVERNORAT, l.LATITUDE, l.LONGITUDE, l.ACTIF
ORDER BY score_global DESC
"""

try:
    df2 = pd.read_sql(query_labos, conn)
    df2.columns = [c.lower() for c in df2.columns]
    print(f"✓ {len(df2)} labos retournés")
    print(f"  Colonnes: {list(df2.columns)}")
    if len(df2) > 0:
        print(f"  Premier labo: {df2.iloc[0][['id_labo','nom_laboratoire','score_global','tier_labo']].to_dict()}")
except Exception as e:
    print(f"❌ ERREUR: {type(e).__name__}: {e}")

conn.close()
print("\n✅ Debug terminé")