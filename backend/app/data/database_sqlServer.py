"""
Database Service pour SQL Server
"""
import logging
import pyodbc
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
            connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
            self._conn = pyodbc.connect(connection_string)
            log.info("Connexion SQL Server OK")
            return True
        except Exception as e:
            log.error(f"Erreur SQL Server: {e}")
            return False

    def get_analyses_data(self) -> pd.DataFrame:
        query = """
        SELECT
            d.id_demande,
            d.num_analyse,
            c.id_centre,
            c.nom_centre,
            c.gouvernorat as ville,
            c.gouvernorat as region,
            c.type_production,
            b.id_batiment,
            b.nom_batiment,
            s.id_souche,
            s.nom_souche as meilleure_souche,
            s.fertilite_score as fertilite_visee,
            s.taux_mortalite,
            s.resistance_maladies,
            t.code_analyse as type_analyse,
            t.libelle as libelle_analyse,
            d.type_echantillon,
            d.date_prelevement,
            d.date_analyse,
            d.date_resultat,
            d.priorite,
            d.est_conforme as conforme,
            d.pourcentage_securite,
            d.statut,
            d.resultat_souche_detectee,
            d.niveau_satisfaction
        FROM dbo.demande_analyse d
        LEFT JOIN dbo.centre_elevage c ON d.id_centre = c.id_centre
        LEFT JOIN dbo.batiment b ON d.id_batiment = b.id_batiment
        LEFT JOIN dbo.souche s ON b.id_souche = s.id_souche
        LEFT JOIN dbo.type_analyse t ON d.id_type_analyse = t.id_type_analyse
        WHERE c.actif = 1
        ORDER BY d.date_analyse DESC
        """
        try:
            df = pd.read_sql(query, self._conn)
            log.info(f"Analyses: {len(df)} lignes")
            return df
        except Exception as e:
            log.error(f"Erreur get_analyses: {e}")
            return pd.DataFrame()

    def get_labos_data(self) -> pd.DataFrame:
        query = """
        SELECT
            l.id_labo,
            l.nom_labo as nom_laboratoire,
            l.gouvernorat as ville,
            l.gouvernorat as region,
            l.latitude,
            l.longitude,
            l.telephone,
            l.email,
            l.actif,
            COUNT(DISTINCT lab.id_laborantin) as nb_laborantins,
            ISNULL(ROUND(AVG(s.taux_conformite), 1), 95) as taux_reussite_pct,
            ISNULL(ROUND(AVG(s.duree_moy_jours), 1), 3) as delai_standard_jours,
            CASE
                WHEN ISNULL(ROUND(AVG(s.duree_moy_jours), 1), 3) <= 2 THEN 12
                WHEN ISNULL(ROUND(AVG(s.duree_moy_jours), 1), 3) <= 3 THEN 18
                ELSE 24
            END as delai_urgence_heures,
            1 as accepte_urgence,
            1 as certifie_iso,
            ROUND(8.0 + (ISNULL(ROUND(AVG(s.taux_conformite), 1), 95) / 100.0) * 1.5, 1) as score_global,
            CASE
                WHEN ROUND(8.0 + (ISNULL(ROUND(AVG(s.taux_conformite), 1), 95) / 100.0) * 1.5, 1) >= 9.0 THEN 'Excellent'
                WHEN ROUND(8.0 + (ISNULL(ROUND(AVG(s.taux_conformite), 1), 95) / 100.0) * 1.5, 1) >= 8.0 THEN 'Bon'
                ELSE 'Passable'
            END as tier_labo,
            'Prive' as type_laboratoire,
            'PCR, Virologie, Bacteriologie' as specialites_principales,
            'Salmonelle, Newcastle, Gumboro' as maladies_avicoles_traitees
        FROM dbo.laboratoire l
        LEFT JOIN dbo.laborantin lab ON l.id_labo = lab.id_labo
        LEFT JOIN dbo.stat_laborantin s ON lab.id_laborantin = s.id_laborantin
        WHERE l.actif = 1
        GROUP BY l.id_labo, l.nom_labo, l.gouvernorat, l.latitude, l.longitude, l.telephone, l.email, l.actif
        ORDER BY score_global DESC
        """
        try:
            df = pd.read_sql(query, self._conn)
            log.info(f"Labos: {len(df)} lignes")
            return df
        except Exception as e:
            log.error(f"Erreur get_labos: {e}")
            return pd.DataFrame()

    def get_all_data(self):
        if not self._conn:
            if not self.connect():
                return pd.DataFrame(), pd.DataFrame()
        
        df_analyses = self.get_analyses_data()
        df_labos = self.get_labos_data()
        return df_analyses, df_labos

    def close(self):
        if self._conn:
            self._conn.close()
            log.info("Connexion SQL Server fermée")


def get_db(settings):
    return SQLServerDB(
        server=settings.SQLSERVER_SERVER,
        database=settings.SQLSERVER_DATABASE,
        driver=settings.SQLSERVER_DRIVER
    )