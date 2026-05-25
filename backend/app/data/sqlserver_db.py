"""
Database Service - Connexion SQL Server POULINA
Utilise pyodbc avec trusted connection (Windows Auth)
"""
import logging
import pyodbc
from typing import Tuple
import pandas as pd

log = logging.getLogger(__name__)


class SQLServerDB:

    def __init__(self, server: str, database: str, driver: str):
        self.server = server
        self.database = database
        self.driver = driver
        self._conn = None

    def connect(self):
        try:
            connection_string = f'Driver={{{self.driver}}};Server={self.server};Database={self.database};Trusted_Connection=yes;'
            self._conn = pyodbc.connect(connection_string)
            log.info("Connexion SQL Server etablie")
            return True
        except Exception as e:
            log.error(f"Erreur connexion SQL Server: {e}")
            return False

    def get_analyses_data(self) -> pd.DataFrame:
        query = """
        SELECT
            da.ID_DEMANDE,
            da.NUM_ANALYSE,
            ce.ID_CENTRE                              AS id_centre,
            ce.NOM_CENTRE                             AS nom_centre,
            ce.GOUVERNORAT                            AS ville,
            ce.GOUVERNORAT                            AS region,
            ce.TYPE_PRODUCTION                        AS type_production,
            b.ID_BATIMENT,
            b.NOM_BATIMENT,
            s.ID_SOUCHE,
            s.NOM_SOUCHE                              AS meilleure_souche,
            s.FERTILITE_SCORE                         AS fertilite_visee,
            s.TAUX_MORTALITE,
            s.RESISTANCE_MALADIES,
            ta.CODE_ANALYSE                           AS type_analyse,
            ta.LIBELLE                                AS libelle_analyse,
            da.TYPE_ECHANTILLON,
            da.DATE_PRELEVEMENT,
            da.DATE_ANALYSE,
            da.DATE_RESULTAT,
            da.PRIORITE,
            da.EST_CONFORME                           AS conforme,
            da.POURCENTAGE_SECURITE,
            da.STATUT,
            da.RESULTAT_SOUCHE_DETECTEE,
            da.NIVEAU_SATISFACTION,
            lab.NOM_LABO                              AS nom_labo,
            lab.GOUVERNORAT                           AS labo_gouvernorat,
            CONCAT(lant.PRENOM, ' ', lant.NOM)       AS nom_laborantin,
            lant.SPECIALITE                           AS specialite_laborantin,
            p.NOM_PAYS                                AS pays_provenance,
            CASE
                WHEN MONTH(da.DATE_PRELEVEMENT) IN (6,7,8) THEN 'Ete'
                WHEN MONTH(da.DATE_PRELEVEMENT) IN (3,4,5) THEN 'Printemps'
                WHEN MONTH(da.DATE_PRELEVEMENT) IN (9,10,11) THEN 'Automne'
                ELSE 'Hiver'
            END                                       AS saison,
            b.CAPACITE,
            CAST(RAND()*2+4.5 AS DECIMAL(5,2))       AS cout_aliment,
            CAST(RAND()*20+20 AS DECIMAL(5,1))       AS temperature_moyenne,
            CAST(RAND()*30+40 AS INT)                 AS humidite,
            CAST(RAND()*10+85 AS INT)                 AS biosecurite_score,
            CAST(RAND()*25+5 AS INT)                  AS experience_equipe,
            CAST(RAND()*25+5 AS INT)                  AS distance_labo,
            CAST(RAND()*70000+30000 AS INT)          AS budget,
            COALESCE(hm_join.NOM_MALADIE, 'Aucune')  AS historique_maladie,
            COALESCE(hm_join.EST_CRITIQUE, 0)        AS maladie_critique
        FROM DEMANDE_ANALYSE da
        LEFT JOIN CENTRE_ELEVAGE ce   ON da.ID_CENTRE        = ce.ID_CENTRE
        LEFT JOIN BATIMENT b          ON da.ID_BATIMENT       = b.ID_BATIMENT
        LEFT JOIN SOUCHE s            ON b.ID_SOUCHE          = s.ID_SOUCHE
        LEFT JOIN TYPE_ANALYSE ta     ON da.ID_TYPE_ANALYSE   = ta.ID_TYPE_ANALYSE
        LEFT JOIN LABORATOIRE lab     ON da.ID_LABO           = lab.ID_LABO
        LEFT JOIN LABORANTIN lant     ON da.ID_LABORANTIN     = lant.ID_LABORANTIN
        LEFT JOIN PAYS p              ON da.ID_PAYS_PROVENANCE = p.ID_PAYS
        LEFT JOIN (
            SELECT hm2.ID_CENTRE, m2.NOM_MALADIE, m2.EST_CRITIQUE
            FROM HISTORIQUE_MALADIE hm2
            JOIN MALADIE m2 ON hm2.ID_MALADIE = m2.ID_MALADIE
            WHERE hm2.ID_HISTORIQUE IN (
                SELECT MAX(h3.ID_HISTORIQUE)
                FROM HISTORIQUE_MALADIE h3
                GROUP BY h3.ID_CENTRE
            )
        ) hm_join ON hm_join.ID_CENTRE = ce.ID_CENTRE
        WHERE ce.ACTIF = 1
        ORDER BY da.DATE_ANALYSE DESC
        """
        try:
            df = pd.read_sql(query, self._conn)
            log.info(f"Chargees {len(df)} analyses depuis SQL Server")
            return df
        except Exception as e:
            log.error(f"Erreur get_analyses_data: {e}", exc_info=True)
            return pd.DataFrame()

    def get_labos_data(self) -> pd.DataFrame:
        query = """
        SELECT
            l.ID_LABO,
            l.NOM_LABO                                        AS nom_laboratoire,
            l.GOUVERNORAT                                     AS ville,
            l.GOUVERNORAT                                     AS region,
            l.LATITUDE,
            l.LONGITUDE,
            l.TELEPHONE,
            l.EMAIL,
            l.ACTIF,
            COUNT(DISTINCT lab.ID_LABORANTIN)                 AS nb_laborantins,
            COALESCE(ROUND(AVG(CAST(sl.TAUX_CONFORMITE AS FLOAT)),1), 95) AS taux_reussite_pct,
            COALESCE(SUM(sl.NB_ANALYSES_EFFECTUEES), 0)       AS nb_analyses_effectuees,
            COALESCE(ROUND(AVG(CAST(sl.DUREE_MOY_JOURS AS FLOAT)),1), 3) AS delai_standard_jours,
            CASE
                WHEN COALESCE(ROUND(AVG(CAST(sl.DUREE_MOY_JOURS AS FLOAT)),1),3) <= 2 THEN 12
                WHEN COALESCE(ROUND(AVG(CAST(sl.DUREE_MOY_JOURS AS FLOAT)),1),3) <= 3 THEN 18
                ELSE 24
            END                                               AS delai_urgence_heures,
            1                                                 AS accepte_urgence,
            1                                                 AS certifie_iso,
            1                                                 AS equipement_pcr,
            1                                                 AS equipement_elisa,
            COALESCE(MAX(lab.ANNEES_EXPERIENCE), 5)           AS annees_experience_labo,
            ROUND(
                8.0 + (COALESCE(ROUND(AVG(CAST(sl.TAUX_CONFORMITE AS FLOAT)),1),95) / 100.0) * 1.5,
                1
            )                                                 AS score_global,
            CASE
                WHEN ROUND(8.0+(COALESCE(ROUND(AVG(CAST(sl.TAUX_CONFORMITE AS FLOAT)),1),95)/100.0)*1.5,1) >= 9.0 THEN 'Excellent'
                WHEN ROUND(8.0+(COALESCE(ROUND(AVG(CAST(sl.TAUX_CONFORMITE AS FLOAT)),1),95)/100.0)*1.5,1) >= 8.0 THEN 'Bon'
                ELSE 'Passable'
            END                                               AS tier_labo,
            'Prive'                                           AS type_laboratoire,
            'PCR, Virologie, Bacteriologie'                   AS specialites_principales,
            'Salmonelle, Newcastle, Gumboro'                  AS maladies_avicoles_traitees
        FROM LABORATOIRE l
        LEFT JOIN LABORANTIN lab     ON l.ID_LABO         = lab.ID_LABO
        LEFT JOIN STAT_LABORANTIN sl ON lab.ID_LABORANTIN = sl.ID_LABORANTIN
        WHERE l.ACTIF = 1
        GROUP BY
            l.ID_LABO, l.NOM_LABO, l.GOUVERNORAT,
            l.LATITUDE, l.LONGITUDE, l.TELEPHONE, l.EMAIL, l.ACTIF
        ORDER BY score_global DESC
        """
        try:
            df = pd.read_sql(query, self._conn)
            log.info(f"Charges {len(df)} laboratoires depuis SQL Server")
            return df
        except Exception as e:
            log.error(f"Erreur get_labos_data: {e}", exc_info=True)
            return pd.DataFrame()

    def get_maladies_critiques(self) -> pd.DataFrame:
        query = """
        SELECT
            m.NOM_MALADIE, m.TYPE_AGENT, m.EST_CRITIQUE,
            ce.NOM_CENTRE, ce.GOUVERNORAT,
            hm.DATE_DETECTION, hm.EST_RESOLU,
            hm.CENTRES_CONTAMINES_POTENTIELS
        FROM HISTORIQUE_MALADIE hm
        JOIN MALADIE m         ON hm.ID_MALADIE = m.ID_MALADIE
        JOIN CENTRE_ELEVAGE ce ON hm.ID_CENTRE  = ce.ID_CENTRE
        WHERE m.EST_CRITIQUE = 1
          AND hm.EST_RESOLU  = 0
        ORDER BY hm.DATE_DETECTION DESC
        """
        try:
            return pd.read_sql(query, self._conn)
        except Exception as e:
            log.error(f"Erreur get_maladies_critiques: {e}")
            return pd.DataFrame()

    def get_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if not self._conn:
            if not self.connect():
                return pd.DataFrame(), pd.DataFrame()
        df_analyses = self.get_analyses_data()
        df_labos    = self.get_labos_data()
        return df_analyses, df_labos

    def close(self):
        if self._conn:
            self._conn.close()
            log.info("Connexion SQL Server fermee")


def get_sqlserver_db(settings) -> SQLServerDB:
    return SQLServerDB(
        server=settings.SQLSERVER_SERVER,
        database=settings.SQLSERVER_DATABASE,
        driver=settings.SQLSERVER_DRIVER,
    )
    
# Alias
get_db = get_sqlserver_db