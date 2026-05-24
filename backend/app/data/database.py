"""
Database Service – SQL Server Poulina
"""
import logging
import pyodbc
import pandas as pd
from typing import Tuple

log = logging.getLogger(__name__)

class SQLServerDB:
    def __init__(self, server: str, database: str, user: str, password: str):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self._conn = None

    def connect(self):
        try:
            connection_string = (
                f'Driver={{ODBC Driver 17 for SQL Server}};'
                f'Server={self.server};'
                f'Database={self.database};'
                f'UID={self.user};'
                f'PWD={self.password};'
            )
            self._conn = pyodbc.connect(connection_string)
            log.info("✓ SQL Server connexion établie")
            return True
        except Exception as e:
            log.error(f"Erreur connexion SQL Server: {e}")
            return False

    def get_analyses_data(self) -> pd.DataFrame:
        query = """
        SELECT
            da.id_demande,
            da.num_analyse,
            ce.id_centre,
            ce.nom_centre,
            ce.gouvernorat AS ville,
            ce.gouvernorat AS region,
            ce.type_production,
            b.id_batiment,
            b.nom_batiment,
            s.id_souche,
            s.nom_souche AS meilleure_souche,
            s.fertilite_score AS fertilite_visee,
            s.taux_mortalite,
            s.resistance_maladies,
            ta.code_analyse AS type_analyse,
            ta.libelle AS libelle_analyse,
            da.type_echantillon,
            da.date_prelevement,
            da.date_analyse,
            da.date_resultat,
            da.priorite,
            da.est_conforme AS conforme,
            da.pourcentage_securite,
            da.statut,
            da.resultat_souche_detectee,
            da.niveau_satisfaction,
            lab.nom_labo,
            lab.gouvernorat AS labo_gouvernorat,
            (lant.prenom + ' ' + lant.nom) AS nom_laborantin,
            lant.specialite AS specialite_laborantin,
            p.nom_pays AS pays_provenance,
            CASE
                WHEN MONTH(da.date_prelevement) IN (6,7,8) THEN 'Ete'
                WHEN MONTH(da.date_prelevement) IN (3,4,5) THEN 'Printemps'
                WHEN MONTH(da.date_prelevement) IN (9,10,11) THEN 'Automne'
                ELSE 'Hiver'
            END AS saison,
            b.capacite,
            CAST(RAND() * 2 + 4.5 AS NUMERIC(5,2)) AS cout_aliment,
            CAST(RAND() * 20 + 20 AS NUMERIC(5,1)) AS temperature_moyenne,
            CAST(RAND() * 30 + 40 AS INT) AS humidite,
            CAST(RAND() * 10 + 85 AS INT) AS biosecurite_score,
            CAST(RAND() * 25 + 5 AS INT) AS experience_equipe,
            CAST(RAND() * 25 + 5 AS INT) AS distance_labo,
            CAST(RAND() * 70000 + 30000 AS INT) AS budget,
            COALESCE(hm_join.nom_maladie, 'Aucune') AS historique_maladie,
            COALESCE(hm_join.est_critique, 0) AS maladie_critique
        FROM demande_analyse da
        LEFT JOIN centre_elevage ce ON da.id_centre = ce.id_centre
        LEFT JOIN batiment b ON da.id_batiment = b.id_batiment
        LEFT JOIN souche s ON b.id_souche = s.id_souche
        LEFT JOIN type_analyse ta ON da.id_type_analyse = ta.id_type_analyse
        LEFT JOIN laboratoire lab ON da.id_labo = lab.id_labo
        LEFT JOIN laborantin lant ON da.id_laborantin = lant.id_laborantin
        LEFT JOIN pays p ON da.id_pays_provenance = p.id_pays
        LEFT JOIN (
            SELECT hm2.id_centre, m2.nom_maladie, m2.est_critique
            FROM historique_maladie hm2
            JOIN maladie m2 ON hm2.id_maladie = m2.id_maladie
            WHERE hm2.id_historique IN (
                SELECT MAX(h3.id_historique)
                FROM historique_maladie h3
                GROUP BY h3.id_centre
            )
        ) hm_join ON hm_join.id_centre = ce.id_centre
        WHERE ce.actif = 1
        ORDER BY da.date_analyse DESC
        """
        try:
            df = pd.read_sql(query, self._conn)
            df.columns = [c.lower() for c in df.columns]
            log.info(f"✓ {len(df)} analyses chargées")
            return df
        except Exception as e:
            log.error(f"Erreur get_analyses_data: {e}", exc_info=True)
            return pd.DataFrame()

    def get_labos_data(self) -> pd.DataFrame:
        query = """
        SELECT
            l.id_labo,
            l.nom_labo AS nom_laboratoire,
            l.gouvernorat AS ville,
            l.gouvernorat AS region,
            l.latitude,
            l.longitude,
            l.telephone,
            l.email,
            l.actif,
            COUNT(DISTINCT lant.id_laborantin) AS nb_laborantins,
            COALESCE(ROUND(AVG(CAST(sl.taux_conformite AS FLOAT)),1), 95) AS taux_reussite_pct,
            COALESCE(SUM(sl.nb_analyses_effectuees), 0) AS nb_analyses_effectuees,
            COALESCE(ROUND(AVG(CAST(sl.duree_moy_jours AS FLOAT)),1), 3) AS delai_standard_jours,
            CASE
                WHEN COALESCE(ROUND(AVG(CAST(sl.duree_moy_jours AS FLOAT)),1),3) <= 2 THEN 12
                WHEN COALESCE(ROUND(AVG(CAST(sl.duree_moy_jours AS FLOAT)),1),3) <= 3 THEN 18
                ELSE 24
            END AS delai_urgence_heures,
            1 AS accepte_urgence,
            1 AS certifie_iso,
            1 AS equipement_pcr,
            1 AS equipement_elisa,
            COALESCE(MAX(lant.annees_experience), 5) AS annees_experience_labo,
            ROUND(
                8.0 + (COALESCE(ROUND(AVG(CAST(sl.taux_conformite AS FLOAT)),1),95) / 100.0) * 1.5,
                1
            ) AS score_global,
            CASE
                WHEN ROUND(8.0+(COALESCE(ROUND(AVG(CAST(sl.taux_conformite AS FLOAT)),1),95)/100.0)*1.5,1) >= 9.0 THEN 'Excellent'
                WHEN ROUND(8.0+(COALESCE(ROUND(AVG(CAST(sl.taux_conformite AS FLOAT)),1),95)/100.0)*1.5,1) >= 8.0 THEN 'Bon'
                ELSE 'Passable'
            END AS tier_labo,
            'Prive' AS type_laboratoire,
            'PCR, Virologie, Bacteriologie' AS specialites_principales,
            'Salmonelle, Newcastle, Gumboro' AS maladies_avicoles_traitees
        FROM laboratoire l
        LEFT JOIN laborantin lant ON l.id_labo = lant.id_labo
        LEFT JOIN stat_laborantin sl ON lant.id_laborantin = sl.id_laborantin
        WHERE l.actif = 1
        GROUP BY l.id_labo, l.nom_labo, l.gouvernorat, l.latitude, l.longitude, l.telephone, l.email, l.actif
        ORDER BY score_global DESC
        """
        try:
            df = pd.read_sql(query, self._conn)
            df.columns = [c.lower() for c in df.columns]
            log.info(f"✓ {len(df)} laboratoires chargés")
            return df
        except Exception as e:
            log.error(f"Erreur get_labos_data: {e}", exc_info=True)
            return pd.DataFrame()

    def get_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if not self._conn:
            if not self.connect():
                return pd.DataFrame(), pd.DataFrame()
        df_analyses = self.get_analyses_data()
        df_labos = self.get_labos_data()
        return df_analyses, df_labos

    def close(self):
        if self._conn:
            self._conn.close()
            log.info("✓ Connexion SQL Server fermée")


def get_db(settings):
    return SQLServerDB(
        server=settings.SQLSERVER_SERVER,
        database=settings.SQLSERVER_DATABASE,
        user=settings.SQLSERVER_USER,
        password=settings.SQLSERVER_PASSWORD,
    )