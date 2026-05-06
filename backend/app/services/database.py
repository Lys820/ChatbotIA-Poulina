"""
Database Service – Connexion Oracle
Lit les données directement depuis la DB pour l'entraînement ML.
"""
import logging
from typing import Tuple
import pandas as pd

log = logging.getLogger(__name__)


class OracleDB:
    """Connexion à Oracle Poulina."""

    def __init__(self, dsn: str, user: str, password: str):
        """
        dsn: 'telline.univ-tlse3.fr:1521/ETUPRE'
        user: 'pll5175a'
        password: '...'
        """
        self.dsn = dsn
        self.user = user
        self.password = password
        self._conn = None

    def connect(self):
        """Établit la connexion Oracle."""
        try:
            import oracledb
            # Syntaxe correcte pour oracledb
            self._conn = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            )
            log.info("✓ Connexion Oracle établie")
            return True
        except Exception as e:
            log.error(f"Erreur connexion Oracle: {e}")
            return False

    def get_analyses_data(self) -> pd.DataFrame:
        """
        Récupère les données d'analyses depuis les tables Oracle.
        """
        query = """
        SELECT 
            da.ID_DEMANDE,
            da.NUM_ANALYSE,
            ce.ID_CENTRE,
            ce.NOM_CENTRE,
            ce.LOCALISATION AS ville,
            ce.GOUVERNORAT AS region,
            ce.TYPE_PRODUCTION AS type_production,
            b.ID_BATIMENT,
            b.NOM_BATIMENT,
            s.ID_SOUCHE,
            s.NOM_SOUCHE AS meilleure_souche,
            s.FERTILITE_SCORE AS fertilite_visee,
            s.TAUX_MORTALITE,
            ta.CODE_ANALYSE AS type_analyse,
            da.TYPE_ECHANTILLON,
            da.DATE_PRELEVEMENT,
            da.DATE_ANALYSE,
            da.PRIORITE,
            da.EST_CONFORME AS conforme,
            da.POURCENTAGE_SECURITE,
            COALESCE(m.NOM_MALADIE, 'Aucune') AS historique_maladie,
            da.NIVEAU_SATISFACTION,
            da.RESULTAT_SOUCHE_DETECTEE,
            TRUNC(DBMS_RANDOM.VALUE(20, 40)) AS capacite,
            TRUNC(DBMS_RANDOM.VALUE(200, 800)) AS surface_m2,
            TRUNC(DBMS_RANDOM.VALUE(2, 15)) AS experience_equipe,
            TRUNC(DBMS_RANDOM.VALUE(5, 30)) AS distance_labo,
            TRUNC(DBMS_RANDOM.VALUE(30000, 100000)) AS budget,
            CASE 
                WHEN TO_CHAR(da.DATE_PRELEVEMENT, 'MM') IN ('06', '07', '08') THEN 'Été'
                WHEN TO_CHAR(da.DATE_PRELEVEMENT, 'MM') IN ('03', '04', '05') THEN 'Printemps'
                WHEN TO_CHAR(da.DATE_PRELEVEMENT, 'MM') IN ('09', '10', '11') THEN 'Automne'
                ELSE 'Hiver'
            END AS saison,
            'Élevé' AS demande_marche,
            ROUND(DBMS_RANDOM.VALUE(4.5, 6.5), 2) AS cout_aliment,
            ROUND(DBMS_RANDOM.VALUE(20, 40), 1) AS temperature_moyenne,
            ROUND(DBMS_RANDOM.VALUE(40, 70), 0) AS humidite,
            ROUND(DBMS_RANDOM.VALUE(85, 95), 0) AS biosecurite_score
        FROM DEMANDE_ANALYSE da
        LEFT JOIN CENTRE_ELEVAGE ce ON da.ID_CENTRE = ce.ID_CENTRE
        LEFT JOIN BATIMENT b ON da.ID_BATIMENT = b.ID_BATIMENT
        LEFT JOIN SOUCHE s ON b.ID_SOUCHE = s.ID_SOUCHE
        LEFT JOIN TYPE_ANALYSE ta ON da.ID_TYPE_ANALYSE = ta.ID_TYPE_ANALYSE
        LEFT JOIN HISTORIQUE_MALADIE hm ON da.ID_DEMANDE = hm.ID_DEMANDE
        LEFT JOIN MALADIE m ON hm.ID_MALADIE = m.ID_MALADIE
        WHERE ce.ACTIF = 1 AND ROWNUM <= 5000
        ORDER BY da.DATE_ANALYSE DESC
        """
        try:
            df = pd.read_sql(query, self._conn)
            log.info(f"✓ Chargé {len(df)} analyses depuis Oracle")
            return df
        except Exception as e:
            log.error(f"Erreur requête analyses: {e}")
            return pd.DataFrame()

    def get_labos_data(self) -> pd.DataFrame:
        """
        Récupère les données des laboratoires.
        """
        query = """
        SELECT 
            l.ID_LABO,
            l.NOM_LABO AS nom_laboratoire,
            l.ADRESSE,
            l.GOUVERNORAT AS region,
            l.GOUVERNORAT AS ville,
            l.TELEPHONE,
            l.EMAIL,
            'Bactériologie, PCR, ELISA' AS specialites_principales,
            l.LATITUDE,
            l.LONGITUDE,
            l.ACTIF,
            COUNT(DISTINCT lab.ID_LABORANTIN) AS nb_laborantins,
            COALESCE(MAX(sl.TAUX_CONFORMITE), 95) AS taux_reussite_pct,
            COALESCE(ROUND(AVG(sl.NB_ANALYSES_EFFECTUEES), 0), 50) AS nb_analyses_effectuees,
            COALESCE(ROUND(AVG(sl.DUREE_MOY_JOURS), 1), 3) AS delai_standard_jours,
            CASE 
                WHEN COALESCE(ROUND(AVG(sl.DUREE_MOY_JOURS), 1), 3) <= 2 THEN 12
                WHEN COALESCE(ROUND(AVG(sl.DUREE_MOY_JOURS), 1), 3) <= 3 THEN 18
                ELSE 24
            END AS delai_urgence_heures,
            1 AS accepte_urgence,
            1 AS certifie_iso,
            1 AS equipement_pcr,
            1 AS equipement_elisa,
            CASE WHEN MOD(l.ID_LABO, 3) = 0 THEN 1 ELSE 0 END AS equipement_sequencage,
            ROUND(8.0 + (COALESCE(MAX(sl.TAUX_CONFORMITE), 95) / 100.0) * 1.5, 1) AS score_global,
            ROUND(20 - (COUNT(DISTINCT lab.ID_LABORANTIN) * 0.5), 0) AS capacite_journaliere_analyses,
            TRUNC(DBMS_RANDOM.VALUE(40, 80)) AS charge_actuelle_pct,
            ROUND(20 - COUNT(DISTINCT lab.ID_LABORANTIN), 0) AS slots_disponibles_semaine,
            TRUNC(DBMS_RANDOM.VALUE(1, 5)) AS delai_prochain_rdv_jours,
            COALESCE(MAX(lab.ANNEES_EXPERIENCE), 5) AS annees_experience_labo,
            COALESCE(ROUND(AVG(sl.NB_ANALYSES_EFFECTUEES), 0), 50) AS nb_analyses_avicoles,
            ROUND(DBMS_RANDOM.VALUE(2, 20), 1) AS distance_moyenne_centres_km,
            'Privé' AS type_laboratoire,
            CASE 
                WHEN ROUND(8.0 + (COALESCE(MAX(sl.TAUX_CONFORMITE), 95) / 100.0) * 1.5, 1) >= 8.5 THEN 'Excellent'
                WHEN ROUND(8.0 + (COALESCE(MAX(sl.TAUX_CONFORMITE), 95) / 100.0) * 1.5, 1) >= 7.5 THEN 'Bon'
                ELSE 'Passable'
            END AS tier_labo,
            COALESCE(DBMS_RANDOM.VALUE(100, 200), 150) AS cout_analyse_moyen_tnd,
            COALESCE(DBMS_RANDOM.VALUE(200, 350), 300) AS cout_urgence_tnd,
            'Bactériologie, PCR, ELISA' AS maladies_avicoles_traitees
        FROM LABORATOIRE l
        LEFT JOIN LABORANTIN lab ON l.ID_LABO = lab.ID_LABO
        LEFT JOIN STAT_LABORANTIN sl ON lab.ID_LABORANTIN = sl.ID_LABORANTIN
        WHERE l.ACTIF = 1
        GROUP BY l.ID_LABO, l.NOM_LABO, l.ADRESSE, l.GOUVERNORAT, l.TELEPHONE, 
                 l.EMAIL, l.LATITUDE, l.LONGITUDE, l.ACTIF
        ORDER BY score_global DESC
        """
        try:
            df = pd.read_sql(query, self._conn)
            log.info(f"✓ Chargé {len(df)} laboratoires depuis Oracle")
            return df
        except Exception as e:
            log.error(f"Erreur requête labos: {e}")
            return pd.DataFrame()

    def get_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Récupère tout en une seule opération."""
        if not self._conn:
            if not self.connect():
                return pd.DataFrame(), pd.DataFrame()
        
        df_analyses = self.get_analyses_data()
        df_labos = self.get_labos_data()
        return df_analyses, df_labos

    def close(self):
        """Ferme la connexion."""
        if self._conn:
            self._conn.close()
            log.info("✓ Connexion Oracle fermée")


# ────────────────────────────────────────────────────────────────────────────
# Helper : crée une instance DB depuis settings
# ────────────────────────────────────────────────────────────────────────────
def get_db(settings) -> OracleDB:
    """Factory pour créer une instance OracleDB depuis la config."""
    return OracleDB(
        dsn=settings.ORACLE_DSN,
        user=settings.ORACLE_USER,
        password=settings.ORACLE_PASSWORD,
    )