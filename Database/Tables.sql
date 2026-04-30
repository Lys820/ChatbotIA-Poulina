-- ============================================================
-- BASE DE DONNÉES POULINA - VERSION ORACLE SQL 
-- ============================================================
-- Corrections principales :
-- 1. SERIAL remplacé par GENERATED AS IDENTITY
-- 2. BOOLEAN remplacé par NUMBER(1) CHECK (0,1)
-- 3. VARCHAR2 conservé (Oracle)
-- 4. TEXT remplacé par CLOB
-- 5. INT remplacé par NUMBER
-- 6. ARRAY[] supprimé (Oracle utilise nested table / VARRAY)
-- 7. Dates au format DATE 'YYYY-MM-DD'
-- ============================================================


-- ============================================================
-- 1. FILIALE
-- ============================================================

CREATE TABLE filiale (
    id_filiale      NUMBER PRIMARY KEY,
    nom_filiale     VARCHAR2(100) NOT NULL,
    secteur         VARCHAR2(50) NOT NULL
);

CREATE TABLE marque (
    id_marque       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_marque      VARCHAR2(100) NOT NULL,
    id_filiale      NUMBER NOT NULL,
    CONSTRAINT fk_marque_filiale FOREIGN KEY (id_filiale)
        REFERENCES filiale(id_filiale)
);

-- ============================================================
-- 2. PAYS
-- ============================================================

CREATE TABLE pays (
    id_pays         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_pays        VARCHAR2(100) NOT NULL,
    code_iso        CHAR(3) NOT NULL
);

-- ============================================================
-- 3. SOUCHE
-- ============================================================

CREATE TABLE souche (
    id_souche           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_souche          VARCHAR2(150) NOT NULL,
    type_produit_final  VARCHAR2(50) NOT NULL,
    fertilite_score     NUMBER(5,2),
    taux_mortalite      NUMBER(5,2),
    resistance_maladies VARCHAR2(200),
    cout_unitaire       NUMBER(10,3),
    id_pays_origine     NUMBER,
    notes               CLOB,
    CONSTRAINT fk_souche_pays FOREIGN KEY (id_pays_origine)
        REFERENCES pays(id_pays)
);

-- ============================================================
-- 4. MALADIE
-- ============================================================

CREATE TABLE maladie (
    id_maladie          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_maladie         VARCHAR2(150) NOT NULL,
    type_agent          VARCHAR2(50) NOT NULL,
    taux_transmission   NUMBER(5,2),
    taux_mortalite      NUMBER(5,2),
    impact_fertilite    NUMBER(5,2),
    est_critique        NUMBER(1) DEFAULT 0 CHECK (est_critique IN (0,1)),
    description         CLOB
);

-- ============================================================
-- 5. CENTRE ELEVAGE
-- ============================================================

CREATE TABLE centre_elevage (
    id_centre       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_centre      VARCHAR2(150) NOT NULL,
    localisation    VARCHAR2(200) NOT NULL,
    gouvernorat     VARCHAR2(100),
    id_marque       NUMBER NOT NULL,
    type_production VARCHAR2(50),
    capacite_totale NUMBER,
    date_creation   DATE,
    actif           NUMBER(1) DEFAULT 1 CHECK (actif IN (0,1)),
    CONSTRAINT fk_centre_marque FOREIGN KEY (id_marque)
        REFERENCES marque(id_marque)
);

-- ============================================================
-- 6. BATIMENT
-- ============================================================

CREATE TABLE batiment (
    id_batiment         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_batiment        VARCHAR2(100) NOT NULL,
    id_centre           NUMBER NOT NULL,
    id_souche           NUMBER NOT NULL,
    capacite            NUMBER,
    date_mise_en_service DATE,
    actif               NUMBER(1) DEFAULT 1 CHECK (actif IN (0,1)),

    CONSTRAINT fk_batiment_centre FOREIGN KEY (id_centre)
        REFERENCES centre_elevage(id_centre),

    CONSTRAINT fk_batiment_souche FOREIGN KEY (id_souche)
        REFERENCES souche(id_souche)
);

-- ============================================================
-- 7. LABORATOIRE
-- ============================================================

CREATE TABLE laboratoire (
    id_labo         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_labo        VARCHAR2(200) NOT NULL,
    adresse         VARCHAR2(300),
    gouvernorat     VARCHAR2(100),
    latitude        NUMBER(9,6),
    longitude       NUMBER(9,6),
    telephone       VARCHAR2(30),
    email           VARCHAR2(150),
    specialites     CLOB,
    actif           NUMBER(1) DEFAULT 1 CHECK (actif IN (0,1))
);

-- ============================================================
-- 8. LABORANTIN
-- ============================================================

CREATE TABLE laborantin (
    id_laborantin       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prenom              VARCHAR2(100) NOT NULL,
    nom                 VARCHAR2(100) NOT NULL,
    id_labo             NUMBER NOT NULL,
    specialite          VARCHAR2(200),
    annees_experience   NUMBER,
    disponible          NUMBER(1) DEFAULT 1 CHECK (disponible IN (0,1)),
    email               VARCHAR2(150),
    telephone           VARCHAR2(30),

    CONSTRAINT fk_laborantin_labo FOREIGN KEY (id_labo)
        REFERENCES laboratoire(id_labo)
);

-- ============================================================
-- 9. TYPE ANALYSE
-- ============================================================

CREATE TABLE type_analyse (
    id_type_analyse NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code_analyse    VARCHAR2(30) UNIQUE NOT NULL,
    libelle         VARCHAR2(200) NOT NULL,
    description     CLOB,
    duree_jours     NUMBER,
    type_echantillon VARCHAR2(100)
);

-- ============================================================
-- 10. DEMANDE ANALYSE
-- ============================================================

CREATE TABLE demande_analyse (
    id_demande          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    num_analyse         VARCHAR2(50) UNIQUE NOT NULL,

    id_centre           NUMBER NOT NULL,
    id_batiment         NUMBER,
    id_type_analyse     NUMBER NOT NULL,
    id_labo             NUMBER,
    id_laborantin       NUMBER,
    id_pays_provenance  NUMBER,

    type_echantillon    VARCHAR2(100),
    date_prelevement    DATE NOT NULL,
    date_decheance      DATE,
    date_analyse        DATE,
    date_resultat       DATE,

    statut              VARCHAR2(50) DEFAULT 'En attente',

    priorite            NUMBER CHECK (priorite BETWEEN 1 AND 5),

    est_conforme        NUMBER(1) CHECK (est_conforme IN (0,1)),
    raison_non_conformite CLOB,

    resultat_souche_detectee VARCHAR2(200),
    pourcentage_securite NUMBER(5,2),

    niveau_satisfaction NUMBER CHECK (niveau_satisfaction BETWEEN 1 AND 5),
    observations CLOB,

    CONSTRAINT fk_da_centre FOREIGN KEY (id_centre)
        REFERENCES centre_elevage(id_centre),

    CONSTRAINT fk_da_batiment FOREIGN KEY (id_batiment)
        REFERENCES batiment(id_batiment),

    CONSTRAINT fk_da_type FOREIGN KEY (id_type_analyse)
        REFERENCES type_analyse(id_type_analyse),

    CONSTRAINT fk_da_labo FOREIGN KEY (id_labo)
        REFERENCES laboratoire(id_labo),

    CONSTRAINT fk_da_laborantin FOREIGN KEY (id_laborantin)
        REFERENCES laborantin(id_laborantin),

    CONSTRAINT fk_da_pays FOREIGN KEY (id_pays_provenance)
        REFERENCES pays(id_pays)
);

-- ============================================================
-- 11. HISTORIQUE MALADIE
-- ============================================================

CREATE TABLE historique_maladie (
    id_historique   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_centre       NUMBER NOT NULL,
    id_maladie      NUMBER NOT NULL,
    id_demande      NUMBER,

    date_detection  DATE NOT NULL,
    date_resolution DATE,

    est_resolu      NUMBER(1) DEFAULT 0 CHECK (est_resolu IN (0,1)),
    mesures_prises  CLOB,

    centres_contamines_potentiels VARCHAR2(200),

    CONSTRAINT fk_hist_centre FOREIGN KEY (id_centre)
        REFERENCES centre_elevage(id_centre),

    CONSTRAINT fk_hist_maladie FOREIGN KEY (id_maladie)
        REFERENCES maladie(id_maladie),

    CONSTRAINT fk_hist_demande FOREIGN KEY (id_demande)
        REFERENCES demande_analyse(id_demande)
);

-- ============================================================
-- 12. STAT LABORANTIN
-- ============================================================

CREATE TABLE stat_laborantin (
    id_stat                 NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_laborantin           NUMBER NOT NULL,
    id_type_analyse         NUMBER NOT NULL,
    nb_analyses_effectuees  NUMBER DEFAULT 0,
    taux_conformite         NUMBER(5,2),
    duree_moy_jours         NUMBER(4,1),

    CONSTRAINT fk_stat_laborantin FOREIGN KEY (id_laborantin)
        REFERENCES laborantin(id_laborantin),

    CONSTRAINT fk_stat_type FOREIGN KEY (id_type_analyse)
        REFERENCES type_analyse(id_type_analyse)
);
