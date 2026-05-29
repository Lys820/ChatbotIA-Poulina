"""
Database Service — SQL Server
Remplace la version Oracle.
Utilise pyodbc pour la connexion SQL Server.
"""
from __future__ import annotations

import logging
from typing import Tuple, Optional

import pandas as pd
import pyodbc

log = logging.getLogger(__name__)


def _query_to_df(conn: pyodbc.Connection, query: str) -> pd.DataFrame:
    """Execute une requête et retourne un DataFrame."""
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [desc[0].lower() for desc in cursor.description]
        rows = cursor.fetchall()
        clean_rows = []
        for row in rows:
            clean_rows.append(list(row))
        return pd.DataFrame(clean_rows, columns=columns)
    finally:
        cursor.close()


class SQLServerDB:

    def __init__(self, server: str, database: str, user: str, password: str, driver: str = "ODBC Driver 17 for SQL Server"):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self.driver = driver
        self._conn: Optional[pyodbc.Connection] = None

    def connect(self) -> bool:
        try:
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.user};"
                f"PWD={self.password};"
                f"TrustServerCertificate=yes;"
            )
            self._conn = pyodbc.connect(conn_str)
            log.info("Connexion SQL Server etablie sur %s/%s", self.server, self.database)
            return True
        except Exception as e:
            log.error("Erreur connexion SQL Server: %s", e)
            return False

    # ------------------------------------------------------------------
    # Requetes principales
    # ------------------------------------------------------------------

    def get_analyses_data(self) -> pd.DataFrame:
        query = """
        SELECT
            da.id_demande,
            da.num_analyse,
            ce.id_centre,
            ce.nom_centre,
            ce.gouvernorat                                      AS ville,
            ce.gouvernorat                                      AS region,
            ce.type_production,
            b.id_batiment,
            b.nom_batiment,
            s.id_souche,
            s.nom_souche                                        AS meilleure_souche,
            s.fertilite_score                                   AS fertilite_visee,
            s.taux_mortalite,
            s.resistance_maladies,
            ta.code_analyse                                     AS type_analyse,
            ta.libelle                                          AS libelle_analyse,
            da.type_echantillon,
            da.date_prelevement,
            da.date_analyse,
            da.date_resultat,
            da.priorite,
            da.est_conforme                                     AS conforme,
            da.pourcentage_securite,
            da.statut,
            da.resultat_souche_detectee,
            da.niveau_satisfaction,
            lab.nom_labo,
            lab.gouvernorat                                     AS labo_gouvernorat,
            CONCAT(lant.prenom, ' ', lant.nom)                  AS nom_laborantin,
            lant.specialite                                     AS specialite_laborantin,
            p.nom_pays                                          AS pays_provenance,
            CASE
                WHEN MONTH(da.date_prelevement) IN (6,7,8)     THEN 'Ete'
                WHEN MONTH(da.date_prelevement) IN (3,4,5)     THEN 'Printemps'
                WHEN MONTH(da.date_prelevement) IN (9,10,11)   THEN 'Automne'
                ELSE 'Hiver'
            END                                                 AS saison,
            b.capacite,
            ROUND(4.5 + (RAND(CHECKSUM(NEWID())) * 2.0), 2)    AS cout_aliment,
            ROUND(20.0 + (RAND(CHECKSUM(NEWID())) * 20.0), 1)  AS temperature_moyenne,
            ROUND(40.0 + (RAND(CHECKSUM(NEWID())) * 30.0), 0)  AS humidite,
            ROUND(85.0 + (RAND(CHECKSUM(NEWID())) * 10.0), 0)  AS biosecurite_score,
            ROUND(5.0  + (RAND(CHECKSUM(NEWID())) * 25.0), 0)  AS experience_equipe,
            ROUND(5.0  + (RAND(CHECKSUM(NEWID())) * 25.0), 0)  AS distance_labo,
            ROUND(30000 + (RAND(CHECKSUM(NEWID())) * 70000), 0) AS budget,
            COALESCE(hm_join.nom_maladie, 'Aucune')            AS historique_maladie,
            COALESCE(hm_join.est_critique, 0)                  AS maladie_critique
        FROM demande_analyse da
        LEFT JOIN centre_elevage ce     ON da.id_centre        = ce.id_centre
        LEFT JOIN batiment b            ON da.id_batiment      = b.id_batiment
        LEFT JOIN souche s              ON b.id_souche         = s.id_souche
        LEFT JOIN type_analyse ta       ON da.id_type_analyse  = ta.id_type_analyse
        LEFT JOIN laboratoire lab       ON da.id_labo          = lab.id_labo
        LEFT JOIN laborantin lant       ON da.id_laborantin    = lant.id_laborantin
        LEFT JOIN pays p                ON da.id_pays_provenance = p.id_pays
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
        OFFSET 0 ROWS FETCH NEXT 5000 ROWS ONLY
        """
        try:
            df = _query_to_df(self._conn, query)
            log.info("%d analyses chargees depuis SQL Server", len(df))
            return df
        except Exception as e:
            log.error("Erreur get_analyses_data: %s", e, exc_info=True)
            return pd.DataFrame()

    def get_labos_data(self) -> pd.DataFrame:
        query = """
        SELECT
            l.id_labo,
            l.nom_labo                                                      AS nom_laboratoire,
            l.gouvernorat                                                   AS ville,
            l.gouvernorat                                                   AS region,
            l.latitude,
            l.longitude,
            l.telephone,
            l.email,
            l.actif,
            COUNT(DISTINCT lab.id_laborantin)                               AS nb_laborantins,
            COALESCE(ROUND(AVG(sl.taux_conformite), 1), 95)                AS taux_reussite_pct,
            COALESCE(SUM(sl.nb_analyses_effectuees), 0)                    AS nb_analyses_effectuees,
            COALESCE(ROUND(AVG(sl.duree_moy_jours), 1), 3)                AS delai_standard_jours,
            CASE
                WHEN COALESCE(ROUND(AVG(sl.duree_moy_jours), 1), 3) <= 2  THEN 12
                WHEN COALESCE(ROUND(AVG(sl.duree_moy_jours), 1), 3) <= 3  THEN 18
                ELSE 24
            END                                                             AS delai_urgence_heures,
            1                                                               AS accepte_urgence,
            1                                                               AS certifie_iso,
            1                                                               AS equipement_pcr,
            1                                                               AS equipement_elisa,
            COALESCE(MAX(lab.annees_experience), 5)                        AS annees_experience_labo,
            ROUND(
                8.0 + (COALESCE(ROUND(AVG(sl.taux_conformite), 1), 95) / 100.0) * 1.5,
                1
            )                                                               AS score_global,
            CASE
                WHEN ROUND(8.0 + (COALESCE(ROUND(AVG(sl.taux_conformite),1),95)/100.0)*1.5,1) >= 9.0 THEN 'Excellent'
                WHEN ROUND(8.0 + (COALESCE(ROUND(AVG(sl.taux_conformite),1),95)/100.0)*1.5,1) >= 8.0 THEN 'Bon'
                ELSE 'Passable'
            END                                                             AS tier_labo,
            'Prive'                                                         AS type_laboratoire,
            'PCR, Virologie, Bacteriologie'                                 AS specialites_principales,
            'Salmonelle, Newcastle, Gumboro'                                AS maladies_avicoles_traitees
        FROM laboratoire l
        LEFT JOIN laborantin lab        ON l.id_labo          = lab.id_labo
        LEFT JOIN stat_laborantin sl    ON lab.id_laborantin  = sl.id_laborantin
        WHERE l.actif = 1
        GROUP BY
            l.id_labo, l.nom_labo, l.gouvernorat,
            l.latitude, l.longitude, l.telephone, l.email, l.actif
        ORDER BY score_global DESC
        """
        try:
            df = _query_to_df(self._conn, query)
            log.info("%d laboratoires charges depuis SQL Server", len(df))
            return df
        except Exception as e:
            log.error("Erreur get_labos_data: %s", e, exc_info=True)
            return pd.DataFrame()

    def get_maladies_critiques(self) -> pd.DataFrame:
        query = """
        SELECT
            m.nom_maladie,
            m.type_agent,
            m.est_critique,
            ce.nom_centre,
            ce.gouvernorat,
            hm.date_detection,
            hm.est_resolu,
            hm.centres_contamines_potentiels
        FROM historique_maladie hm
        JOIN maladie m          ON hm.id_maladie = m.id_maladie
        JOIN centre_elevage ce  ON hm.id_centre  = ce.id_centre
        WHERE m.est_critique = 1
          AND hm.est_resolu  = 0
        ORDER BY hm.date_detection DESC
        """
        try:
            return _query_to_df(self._conn, query)
        except Exception as e:
            log.error("Erreur get_maladies_critiques: %s", e)
            return pd.DataFrame()

    def get_centres(self, filters: dict = None) -> pd.DataFrame:
        where_clauses = ["ce.actif = 1"]
        if filters:
            if filters.get("gouvernorat"):
                where_clauses.append(f"ce.gouvernorat = '{filters['gouvernorat']}'")
            if filters.get("type_production"):
                where_clauses.append(f"ce.type_production = '{filters['type_production']}'")
            if filters.get("id_marque"):
                where_clauses.append(f"ce.id_marque = {filters['id_marque']}")

        where_sql = " AND ".join(where_clauses)
        query = f"""
        SELECT
            ce.id_centre, ce.nom_centre, ce.localisation,
            ce.gouvernorat, ce.type_production, ce.capacite_totale,
            ce.date_creation, ce.actif,
            m.nom_marque, f.nom_filiale
        FROM centre_elevage ce
        JOIN marque m   ON ce.id_marque  = m.id_marque
        JOIN filiale f  ON m.id_filiale  = f.id_filiale
        WHERE {where_sql}
        ORDER BY ce.nom_centre
        """
        try:
            return _query_to_df(self._conn, query)
        except Exception as e:
            log.error("Erreur get_centres: %s", e)
            return pd.DataFrame()

    def get_souches(self, filters: dict = None) -> pd.DataFrame:
        where_clauses = ["1=1"]
        if filters:
            if filters.get("type_produit_final"):
                where_clauses.append(f"s.type_produit_final = '{filters['type_produit_final']}'")
            if filters.get("fertilite_min") is not None:
                where_clauses.append(f"s.fertilite_score >= {filters['fertilite_min']}")
            if filters.get("taux_mortalite_max") is not None:
                where_clauses.append(f"s.taux_mortalite <= {filters['taux_mortalite_max']}")

        where_sql = " AND ".join(where_clauses)
        query = f"""
        SELECT
            s.id_souche, s.nom_souche, s.type_produit_final,
            s.fertilite_score, s.taux_mortalite, s.resistance_maladies,
            s.cout_unitaire, s.notes,
            p.nom_pays AS pays_origine
        FROM souche s
        LEFT JOIN pays p ON s.id_pays_origine = p.id_pays
        WHERE {where_sql}
        ORDER BY s.fertilite_score DESC
        """
        try:
            return _query_to_df(self._conn, query)
        except Exception as e:
            log.error("Erreur get_souches: %s", e)
            return pd.DataFrame()

    def get_utilisateur_par_email(self, email: str) -> Optional[dict]:
        query = """
        SELECT
            u.id_utilisateur,
            u.password_hash,
            u.nom,
            u.prenom,
            u.actif,
            r.nom_role,
            STRING_AGG(p.code, ',') AS permissions
        FROM utilisateur u
        JOIN role r                 ON u.id_role    = r.id_role
        LEFT JOIN role_permission rp ON r.id_role   = rp.id_role
        LEFT JOIN permission p      ON rp.id_permission = p.id_permission
        WHERE u.email = ?
          AND u.actif = 1
        GROUP BY
            u.id_utilisateur, u.password_hash, u.nom, u.prenom,
            u.actif, r.nom_role
        """
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            if not row:
                return None
            cols = [desc[0].lower() for desc in cursor.description]
            return dict(zip(cols, row))
        finally:
            cursor.close()

    def get_session(self, session_id: str) -> Optional[dict]:
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                "SELECT id_session, id_utilisateur, actif FROM session_chat WHERE id_session = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {"id_session": row[0], "id_utilisateur": row[1], "actif": row[2]}
        finally:
            cursor.close()

    def create_session(self, session_id: str, user_id: int) -> None:
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO session_chat (id_session, id_utilisateur, date_debut,
                    date_derniere_activite, actif, contexte_json)
                VALUES (?, ?, GETDATE(), GETDATE(), 1, '{}')
                """,
                (session_id, user_id)
            )
            self._conn.commit()
        finally:
            cursor.close()

    def get_messages(self, session_id: str, limit: int = 20) -> list[dict]:
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                """
                SELECT TOP (?) role, contenu
                FROM message_chat
                WHERE id_session = ?
                ORDER BY date_message ASC
                """,
                (limit, session_id)
            )
            rows = cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in rows]
        finally:
            cursor.close()

    def add_message(self, session_id: str, role: str, content: str) -> None:
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO message_chat (id_session, role, contenu, date_message)
                VALUES (?, ?, ?, GETDATE())
                """,
                (session_id, role, content)
            )
            cursor.execute(
                "UPDATE session_chat SET date_derniere_activite = GETDATE() WHERE id_session = ?",
                (session_id,)
            )
            self._conn.commit()
        finally:
            cursor.close()

    def update_session_inactive(self, session_id: str) -> None:
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                "UPDATE session_chat SET actif = 0 WHERE id_session = ?",
                (session_id,)
            )
            self._conn.commit()
        finally:
            cursor.close()

    def get_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if not self._conn:
            if not self.connect():
                return pd.DataFrame(), pd.DataFrame()
        return self.get_analyses_data(), self.get_labos_data()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            log.info("Connexion SQL Server fermee")


def get_db(settings) -> SQLServerDB:
    return SQLServerDB(
        server=settings.SQLSERVER_SERVER,
        database=settings.SQLSERVER_DATABASE,
        user=settings.SQLSERVER_USER,
        password=settings.SQLSERVER_PASSWORD,
        driver=getattr(settings, "SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server"),
    )