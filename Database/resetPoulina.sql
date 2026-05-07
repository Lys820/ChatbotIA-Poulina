-- ============================================================
-- POULINA – RESET COMPLET
-- Drop + Recreate + Insert
-- Oracle SQL (GENERATED AS IDENTITY, NUMBER(1), CLOB)
-- ============================================================


-- ============================================================
-- 1. DROP (ordre inverse des FK)
-- ============================================================

BEGIN EXECUTE IMMEDIATE 'DROP TABLE stat_laborantin    CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE historique_maladie CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE demande_analyse    CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE batiment           CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE laborantin         CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE laboratoire        CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE centre_elevage     CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE type_analyse       CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE souche             CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE maladie            CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE marque             CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE pays               CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE filiale            CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

-- Drop views
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vue_batiment_complet';        EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vue_alertes_actives';         EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vue_meilleur_laborantin';     EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vue_centres_risque';          EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vue_recommandation_laborantin'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vue_urgence_analyse';         EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vue_dashboard_ia';            EXCEPTION WHEN OTHERS THEN NULL; END;
/


-- ============================================================
-- 2. CREATE TABLES
-- ============================================================

CREATE TABLE filiale (
    id_filiale  NUMBER PRIMARY KEY,
    nom_filiale VARCHAR2(100) NOT NULL,
    secteur     VARCHAR2(50)  NOT NULL
);

CREATE TABLE marque (
    id_marque  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_marque VARCHAR2(100) NOT NULL,
    id_filiale NUMBER NOT NULL,
    CONSTRAINT fk_marque_filiale FOREIGN KEY (id_filiale) REFERENCES filiale(id_filiale)
);

CREATE TABLE pays (
    id_pays  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_pays VARCHAR2(100) NOT NULL,
    code_iso CHAR(3)       NOT NULL
);

CREATE TABLE souche (
    id_souche           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_souche          VARCHAR2(150) NOT NULL,
    type_produit_final  VARCHAR2(50)  NOT NULL,
    fertilite_score     NUMBER(5,2),
    taux_mortalite      NUMBER(5,2),
    resistance_maladies VARCHAR2(200),
    cout_unitaire       NUMBER(10,3),
    id_pays_origine     NUMBER,
    notes               CLOB,
    CONSTRAINT fk_souche_pays FOREIGN KEY (id_pays_origine) REFERENCES pays(id_pays)
);

CREATE TABLE maladie (
    id_maladie        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_maladie       VARCHAR2(150) NOT NULL,
    type_agent        VARCHAR2(50)  NOT NULL,
    taux_transmission NUMBER(5,2),
    taux_mortalite    NUMBER(5,2),
    impact_fertilite  NUMBER(5,2),
    est_critique      NUMBER(1) DEFAULT 0 CHECK (est_critique IN (0,1)),
    description       CLOB
);

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
    CONSTRAINT fk_centre_marque FOREIGN KEY (id_marque) REFERENCES marque(id_marque)
);

CREATE TABLE batiment (
    id_batiment          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_batiment         VARCHAR2(100) NOT NULL,
    id_centre            NUMBER NOT NULL,
    id_souche            NUMBER NOT NULL,
    capacite             NUMBER,
    date_mise_en_service DATE,
    actif                NUMBER(1) DEFAULT 1 CHECK (actif IN (0,1)),
    CONSTRAINT fk_batiment_centre FOREIGN KEY (id_centre) REFERENCES centre_elevage(id_centre),
    CONSTRAINT fk_batiment_souche FOREIGN KEY (id_souche) REFERENCES souche(id_souche)
);

CREATE TABLE laboratoire (
    id_labo    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom_labo   VARCHAR2(200) NOT NULL,
    adresse    VARCHAR2(300),
    gouvernorat VARCHAR2(100),
    latitude   NUMBER(9,6),
    longitude  NUMBER(9,6),
    telephone  VARCHAR2(30),
    email      VARCHAR2(150),
    specialites CLOB,
    actif      NUMBER(1) DEFAULT 1 CHECK (actif IN (0,1))
);

CREATE TABLE laborantin (
    id_laborantin     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prenom            VARCHAR2(100) NOT NULL,
    nom               VARCHAR2(100) NOT NULL,
    id_labo           NUMBER NOT NULL,
    specialite        VARCHAR2(200),
    annees_experience NUMBER,
    disponible        NUMBER(1) DEFAULT 1 CHECK (disponible IN (0,1)),
    email             VARCHAR2(150),
    telephone         VARCHAR2(30),
    CONSTRAINT fk_laborantin_labo FOREIGN KEY (id_labo) REFERENCES laboratoire(id_labo)
);

CREATE TABLE type_analyse (
    id_type_analyse  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code_analyse     VARCHAR2(30)  UNIQUE NOT NULL,
    libelle          VARCHAR2(200) NOT NULL,
    description      CLOB,
    duree_jours      NUMBER,
    type_echantillon VARCHAR2(100)
);

CREATE TABLE demande_analyse (
    id_demande               NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    num_analyse              VARCHAR2(50) UNIQUE NOT NULL,
    id_centre                NUMBER NOT NULL,
    id_batiment              NUMBER,
    id_type_analyse          NUMBER NOT NULL,
    id_labo                  NUMBER,
    id_laborantin            NUMBER,
    id_pays_provenance       NUMBER,
    type_echantillon         VARCHAR2(100),
    date_prelevement         DATE NOT NULL,
    date_decheance           DATE,
    date_analyse             DATE,
    date_resultat            DATE,
    statut                   VARCHAR2(50) DEFAULT 'En attente',
    priorite                 NUMBER CHECK (priorite BETWEEN 1 AND 5),
    est_conforme             NUMBER(1) CHECK (est_conforme IN (0,1)),
    raison_non_conformite    CLOB,
    resultat_souche_detectee VARCHAR2(200),
    pourcentage_securite     NUMBER(5,2),
    niveau_satisfaction      NUMBER CHECK (niveau_satisfaction BETWEEN 1 AND 5),
    observations             CLOB,
    CONSTRAINT fk_da_centre     FOREIGN KEY (id_centre)          REFERENCES centre_elevage(id_centre),
    CONSTRAINT fk_da_batiment   FOREIGN KEY (id_batiment)         REFERENCES batiment(id_batiment),
    CONSTRAINT fk_da_type       FOREIGN KEY (id_type_analyse)     REFERENCES type_analyse(id_type_analyse),
    CONSTRAINT fk_da_labo       FOREIGN KEY (id_labo)             REFERENCES laboratoire(id_labo),
    CONSTRAINT fk_da_laborantin FOREIGN KEY (id_laborantin)       REFERENCES laborantin(id_laborantin),
    CONSTRAINT fk_da_pays       FOREIGN KEY (id_pays_provenance)  REFERENCES pays(id_pays)
);

CREATE TABLE historique_maladie (
    id_historique                 NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_centre                     NUMBER NOT NULL,
    id_maladie                    NUMBER NOT NULL,
    id_demande                    NUMBER,
    date_detection                DATE NOT NULL,
    date_resolution               DATE,
    est_resolu                    NUMBER(1) DEFAULT 0 CHECK (est_resolu IN (0,1)),
    mesures_prises                CLOB,
    centres_contamines_potentiels VARCHAR2(200),
    CONSTRAINT fk_hist_centre  FOREIGN KEY (id_centre)  REFERENCES centre_elevage(id_centre),
    CONSTRAINT fk_hist_maladie FOREIGN KEY (id_maladie) REFERENCES maladie(id_maladie),
    CONSTRAINT fk_hist_demande FOREIGN KEY (id_demande) REFERENCES demande_analyse(id_demande)
);

CREATE TABLE stat_laborantin (
    id_stat                NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_laborantin          NUMBER NOT NULL,
    id_type_analyse        NUMBER NOT NULL,
    nb_analyses_effectuees NUMBER DEFAULT 0,
    taux_conformite        NUMBER(5,2),
    duree_moy_jours        NUMBER(4,1),
    CONSTRAINT fk_stat_laborantin FOREIGN KEY (id_laborantin)  REFERENCES laborantin(id_laborantin),
    CONSTRAINT fk_stat_type       FOREIGN KEY (id_type_analyse) REFERENCES type_analyse(id_type_analyse)
);


-- ============================================================
-- 3. INSERT DONNÉES
-- ============================================================

-- FILIALE
INSERT INTO filiale VALUES (1, 'Poulina Avicole',          'Avicole');
INSERT INTO filiale VALUES (2, 'Poulina Agro-Alimentaire', 'Agro-Alimentaire');

-- PAYS
INSERT INTO pays (nom_pays, code_iso) VALUES ('Tunisie',   'TUN');
INSERT INTO pays (nom_pays, code_iso) VALUES ('France',    'FRA');
INSERT INTO pays (nom_pays, code_iso) VALUES ('Belgique',  'BEL');
INSERT INTO pays (nom_pays, code_iso) VALUES ('Allemagne', 'DEU');
INSERT INTO pays (nom_pays, code_iso) VALUES ('Pays-Bas',  'NLD');
INSERT INTO pays (nom_pays, code_iso) VALUES ('Espagne',   'ESP');

-- MARQUE
INSERT INTO marque (nom_marque, id_filiale) VALUES ('Dick',   1);
INSERT INTO marque (nom_marque, id_filiale) VALUES ('SNA',    1);
INSERT INTO marque (nom_marque, id_filiale) VALUES ('Gipa',   2);
INSERT INTO marque (nom_marque, id_filiale) VALUES ('MedOil', 2);

-- SOUCHE  (id_pays_origine = id des pays insérés ci-dessus : NLD=5, FRA=2, BEL=3, DEU=4)
INSERT INTO souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Ross 308',      'Poulet', 94.5, 3.2, 'Faible Salmonelle',  2.800, 5, 'Croissance rapide, conversion élevée');

INSERT INTO souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Cobb 500',      'Poulet', 93.8, 3.5, 'Moyenne',            2.650, 5, 'Bonne conversion alimentaire');

INSERT INTO souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Hubbard Flex',  'Poulet', 92.1, 4.1, 'Bonne',              2.500, 2, 'Adaptée aux climats chauds');

INSERT INTO souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Lohmann Brown', 'Oeuf',   96.0, 1.8, 'Très résistante',    3.100, 3, 'Haute ponte, résistance maladies');

INSERT INTO souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Ross 708',      'Poulet', 95.2, 2.9, 'Bonne',              2.950, 5, 'Performance maximale, standard export');

INSERT INTO souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('BUT Big 6',     'Dinde',  88.0, 5.1, 'Faible',             4.200, 2, 'Dinde commerciale lourde');

INSERT INTO souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Hybro G+',      'Poulet', 93.0, 3.8, 'Moyenne',            2.700, 4, 'Polyvalente, adaptable');

-- MALADIE
INSERT INTO maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Salmonelle',           'Bactérie',  45.0, 8.0,  25.0, 1, 'Zoonose majeure, transmission par fèces et eau contaminée');

INSERT INTO maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Newcastle',            'Virus',     80.0, 60.0, 40.0, 1, 'Maladie de Newcastle, déclaration obligatoire, pandémique');

INSERT INTO maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Gumboro',              'Virus',     55.0, 20.0, 15.0, 0, 'Immunodépresseur, touche principalement les poussins 3-6 semaines');

INSERT INTO maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Mycoplasme',           'Bactérie',  35.0,  5.0, 20.0, 0, 'Maladie chronique respiratoire, impact pondeuses');

INSERT INTO maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Coccidiose',           'Parasite',  40.0, 10.0, 30.0, 0, 'Parasite intestinal fréquent, traitement antiparasitaire');

INSERT INTO maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Marek',                'Virus',     70.0, 25.0, 10.0, 0, 'Herpesvirus, lymphomes, vaccination jour 1');

INSERT INTO maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Bronchite infectieuse','Virus',     60.0, 15.0, 35.0, 0, 'IB, tropisme respiratoire et rénal, nombreux sérotypes');

-- CENTRE ELEVAGE  (id_marque : Dick=1, SNA=2)
INSERT INTO centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre Dick Nord',   'Route Mateur km 12',        'Bizerte',  1, 'Poulet', 80000, DATE '2010-03-15', 1);

INSERT INTO centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre Dick Sud',    'Zone Industrielle Sfax',    'Sfax',     1, 'Poulet', 60000, DATE '2012-07-01', 1);

INSERT INTO centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre SNA Tunis',   'Ariana Zone Nord',          'Ariana',   2, 'Dinde',  30000, DATE '2008-09-10', 1);

INSERT INTO centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre Dick Est',    'Nabeul Route Côtière',      'Nabeul',   1, 'Poulet', 50000, DATE '2015-04-20', 1);

INSERT INTO centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre SNA Sousse',  'Zone Industrielle Sousse',  'Sousse',   2, 'Oeuf',   40000, DATE '2017-01-05', 1);

INSERT INTO centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre Dick Centre', 'Kairouan Route Nationale',  'Kairouan', 1, 'Poulet', 70000, DATE '2013-06-12', 1);

-- BATIMENT  (id_centre 1-6, id_souche selon schéma Ross308=1, Cobb500=2, HubbardFlex=3, Lohmann=4, Ross708=5, BUT=6, Hybro=7)
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment A1', 1, 1, 15000, DATE '2010-03-15', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment A2', 1, 2, 15000, DATE '2011-06-01', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment B1', 2, 1, 12000, DATE '2012-07-01', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment B2', 2, 5, 12000, DATE '2013-02-15', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment C1', 3, 6, 10000, DATE '2008-09-10', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment C2', 3, 7, 10000, DATE '2010-05-20', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment D1', 4, 2, 12000, DATE '2015-04-20', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment D2', 4, 3, 12000, DATE '2016-08-10', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment E1', 5, 4, 10000, DATE '2017-01-05', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment E2', 5, 4, 10000, DATE '2018-03-01', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment F1', 6, 1, 15000, DATE '2013-06-12', 1);
INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment F2', 6, 5, 15000, DATE '2014-11-01', 1);

-- LABORATOIRE
INSERT INTO laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Labo Central Tunis',  'Rue de la Liberté, Tunis',      'Tunis',   36.819000, 10.166300, '+21671123456', 'central@labo.tn',  'PCR, Virologie, Bactériologie, ELISA', 1);

INSERT INTO laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Pasteur Tunis',        'Avenue Pasteur, Tunis',         'Tunis',   36.818500, 10.170200, '+21671987654', 'pasteur@labo.tn',  'Virologie, Immunologie, Influenza', 1);

INSERT INTO laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Labo Sfax Avicole',    'Zone Industrielle, Sfax',       'Sfax',    34.740000, 10.760000, '+21674111222', 'sfax@labo.tn',     'Bactériologie, PCR, Salmonelle', 1);

INSERT INTO laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Labo Sousse Bio',      'Avenue Mohammed V, Sousse',     'Sousse',  35.833300, 10.637800, '+21673333444', 'sousse@labo.tn',   'ELISA, Sérologie, PCR', 1);

INSERT INTO laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Institut Vét Bizerte', 'Route Mateur, Bizerte',         'Bizerte', 37.274400,  9.873900, '+21672555666', 'bizerte@labo.tn',  'PCR, Bactériologie, Parasitologie', 1);

-- LABORANTIN  (id_labo : Labo Central=1, Pasteur=2, Sfax=3, Sousse=4, Bizerte=5)
INSERT INTO laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Sami',    'Bouaziz',   1, 'Salmonelle, Bactériologie',  12, 1, 'sami.bouaziz@labo.tn',   '+216221001');

INSERT INTO laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Nadia',   'Trabelsi',  1, 'PCR, Virologie',              8, 1, 'nadia.trabelsi@labo.tn', '+216221002');

INSERT INTO laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Karim',   'Ben Ali',   2, 'Immunologie, ELISA',           6, 1, 'karim.benali@labo.tn',  '+216221003');

INSERT INTO laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Fatma',   'Mansouri',  3, 'Bactériologie, Salmonelle',   10, 1, 'fatma.mansouri@labo.tn','+216221004');

INSERT INTO laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Youssef', 'Dridi',     3, 'PCR, Newcastle',               5, 1, 'youssef.dridi@labo.tn', '+216221005');

INSERT INTO laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Amira',   'Khelifi',   4, 'Sérologie, ELISA',             7, 1, 'amira.khelifi@labo.tn', '+216221006');

INSERT INTO laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Bilel',   'Gharbi',    5, 'PCR, Parasitologie',           9, 0, 'bilel.gharbi@labo.tn',  '+216221007');

INSERT INTO laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Rania',   'Chabbi',    5, 'Bactériologie, PCR',           4, 1, 'rania.chabbi@labo.tn',  '+216221008');

-- TYPE ANALYSE
INSERT INTO type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('BACTE-SAL', 'Bactériologie Salmonelle',    'Recherche et identification Salmonella spp.',    5, 'Fiente');

INSERT INTO type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('PCR-ND',    'PCR Newcastle',               'Détection virus Newcastle par PCR temps réel',   3, 'Frottis trachéal');

INSERT INTO type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('ELISA-IBD', 'Sérologie Gumboro ELISA',    'Titrage anticorps anti-IBD',                     4, 'Sang');

INSERT INTO type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('PCR-MG',    'PCR Mycoplasme',              'Détection Mycoplasma gallisepticum',              3, 'Écouvillon trachéal');

INSERT INTO type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('PARASIT',   'Parasitologie Coccidiose',    'Examen coprologique + identification oocystes',  2, 'Fientes fraiches');

INSERT INTO type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('SERO-ND',   'Sérologie Newcastle HI',      'Inhibition hémagglutination ND',                 4, 'Sang');

INSERT INTO type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('BACTE-COL', 'Bactériologie E.coli',        'Antibiogramme E.coli pathogènes',                5, 'Organes');

-- ============================================================
-- DEMANDE ANALYSE (61 analyses)
-- id_centre 1-6 | id_batiment 1-12 | id_type_analyse 1-7
-- id_labo 1-5   | id_laborantin 1-8 | id_pays_provenance 1-6
-- ============================================================

INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-001',1,1,1,1,1,1,'Fiente',           DATE '2024-01-10',DATE '2024-01-17',DATE '2024-01-12',DATE '2024-01-14','Terminée',        1,1,NULL,'Ross 308',     98.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-002',2,3,2,3,4,1,'Frottis trachéal', DATE '2024-01-15',DATE '2024-01-22',DATE '2024-01-17',DATE '2024-01-19','Non conforme',    2,0,'Virus Newcastle identifié, abattage préventif requis','Ross 308',52.0,2,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-003',3,5,3,2,3,2,'Sang',             DATE '2024-01-20',DATE '2024-01-27',DATE '2024-01-23',DATE '2024-01-25','Terminée',        3,1,NULL,'BUT Big 6',    91.5,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-004',4,7,1,3,4,5,'Fiente',           DATE '2024-02-01',DATE '2024-02-08',DATE '2024-02-03',DATE '2024-02-05','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Cobb 500',48.5,1,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-005',5,9,4,4,6,3,'Écouvillon trachéal',DATE '2024-02-05',DATE '2024-02-12',DATE '2024-02-07',DATE '2024-02-09','Terminée',      2,1,NULL,'Lohmann Brown',93.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-006',6,11,5,5,8,1,'Fientes fraiches', DATE '2024-02-10',DATE '2024-02-17',DATE '2024-02-13',DATE '2024-02-14','Terminée',       3,1,NULL,'Ross 308',     89.0,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-007',1,2,6,1,2,5,'Sang',             DATE '2024-02-15',DATE '2024-02-22',DATE '2024-02-18',DATE '2024-02-20','Terminée',        4,1,NULL,'Cobb 500',     95.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-008',2,4,7,3,5,1,'Organes',          DATE '2024-02-20',DATE '2024-02-27',DATE '2024-02-22',DATE '2024-02-24','Non conforme',    2,0,'Résultat inférieur au seuil de sécurité (< 85%)','Hubbard Flex',71.0,2,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-009',3,6,2,2,3,2,'Frottis trachéal', DATE '2024-03-01',DATE '2024-03-08',DATE '2024-03-04',DATE '2024-03-06','Terminée',        3,1,NULL,'BUT Big 6',    90.5,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-010',4,8,3,4,6,4,'Sang',             DATE '2024-03-05',DATE '2024-03-12',DATE '2024-03-07',DATE '2024-03-09','Terminée',        1,1,NULL,'Cobb 500',     96.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-011',5,10,1,3,4,1,'Fiente',          DATE '2024-03-10',DATE '2024-03-17',DATE '2024-03-12',DATE '2024-03-14','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Lohmann Brown',55.0,1,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-012',6,12,4,5,8,1,'Écouvillon trachéal',DATE '2024-03-15',DATE '2024-03-22',DATE '2024-03-18',DATE '2024-03-20','Terminée',     2,1,NULL,'Ross 308',     88.0,3,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-013',1,1,5,1,1,3,'Fientes fraiches', DATE '2024-03-20',DATE '2024-03-27',DATE '2024-03-22',DATE '2024-03-24','Terminée',        4,1,NULL,'Ross 308',     92.0,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-014',2,3,6,3,5,5,'Sang',             DATE '2024-04-01',DATE '2024-04-08',DATE '2024-04-03',DATE '2024-04-05','Terminée',        3,1,NULL,'Ross 308',     97.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-015',3,5,7,2,3,2,'Organes',          DATE '2024-04-05',DATE '2024-04-12',DATE '2024-04-08',DATE '2024-04-10','Non conforme',    2,0,'Souche détectée ne correspond pas au bâtiment déclaré','BUT Big 6',78.0,2,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-016',4,7,1,3,4,1,'Fiente',           DATE '2024-04-10',DATE '2024-04-17',DATE '2024-04-13',DATE '2024-04-15','Terminée',        5,1,NULL,'Cobb 500',     91.0,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-017',5,9,2,4,6,4,'Frottis trachéal', DATE '2024-04-15',DATE '2024-04-22',DATE '2024-04-17',DATE '2024-04-19','Terminée',        3,1,NULL,'Lohmann Brown',94.5,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-018',6,11,3,5,8,1,'Sang',            DATE '2024-04-20',DATE '2024-04-27',DATE '2024-04-23',DATE '2024-04-25','Critique',        1,0,'Virus Newcastle identifié, abattage préventif requis','Ross 708',49.0,1,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-019',1,2,4,1,2,5,'Écouvillon trachéal',DATE '2024-05-01',DATE '2024-05-08',DATE '2024-05-03',DATE '2024-05-05','Terminée',      4,1,NULL,'Cobb 500',     87.5,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-020',2,4,5,3,4,1,'Fientes fraiches', DATE '2024-05-05',DATE '2024-05-12',DATE '2024-05-07',DATE '2024-05-09','Terminée',        2,1,NULL,'Hubbard Flex', 90.0,3,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-021',3,6,6,2,3,3,'Sang',             DATE '2024-05-10',DATE '2024-05-17',DATE '2024-05-13',DATE '2024-05-14','Terminée',        3,1,NULL,'BUT Big 6',    93.5,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-022',4,8,7,4,6,4,'Organes',          DATE '2024-05-15',DATE '2024-05-22',DATE '2024-05-18',DATE '2024-05-20','Non conforme',    1,0,'Prélèvement non conforme : délai de conservation dépassé','Cobb 500',63.0,2,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-023',5,10,1,3,5,1,'Fiente',          DATE '2024-05-20',DATE '2024-05-27',DATE '2024-05-22',DATE '2024-05-24','Terminée',        2,1,NULL,'Lohmann Brown',95.5,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-024',6,12,2,5,8,5,'Frottis trachéal',DATE '2024-06-01',DATE '2024-06-08',DATE '2024-06-03',DATE '2024-06-05','Terminée',        4,1,NULL,'Ross 308',     88.5,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-025',1,1,3,1,1,1,'Sang',             DATE '2024-06-05',DATE '2024-06-12',DATE '2024-06-08',DATE '2024-06-10','Terminée',        3,1,NULL,'Ross 308',     94.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-026',2,3,4,3,4,1,'Écouvillon trachéal',DATE '2024-06-10',DATE '2024-06-17',DATE '2024-06-12',DATE '2024-06-14','Terminée',     5,1,NULL,'Ross 308',     86.0,3,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-027',3,5,5,2,3,2,'Fientes fraiches', DATE '2024-06-15',DATE '2024-06-22',DATE '2024-06-18',DATE '2024-06-20','Non conforme',    2,0,'Résultat inférieur au seuil de sécurité (< 85%)','Hybro G+',   76.0,2,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-028',4,7,6,3,5,5,'Sang',             DATE '2024-06-20',DATE '2024-06-27',DATE '2024-06-22',DATE '2024-06-24','Terminée',        1,1,NULL,'Cobb 500',     97.5,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-029',5,9,7,4,6,3,'Organes',          DATE '2024-07-01',DATE '2024-07-08',DATE '2024-07-03',DATE '2024-07-05','Terminée',        3,1,NULL,'Lohmann Brown',91.0,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-030',6,11,1,5,8,1,'Fiente',          DATE '2024-07-05',DATE '2024-07-12',DATE '2024-07-08',DATE '2024-07-10','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Ross 708', 51.0,1,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-031',1,2,2,1,2,1,'Frottis trachéal', DATE '2024-07-10',DATE '2024-07-17',DATE '2024-07-12',DATE '2024-07-14','Terminée',        4,1,NULL,'Cobb 500',     93.0,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-032',2,4,3,3,4,5,'Sang',             DATE '2024-07-15',DATE '2024-07-22',DATE '2024-07-17',DATE '2024-07-19','Terminée',        2,1,NULL,'Hubbard Flex', 89.5,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-033',3,6,4,2,3,2,'Écouvillon trachéal',DATE '2024-07-20',DATE '2024-07-27',DATE '2024-07-22',DATE '2024-07-24','Terminée',     3,1,NULL,'BUT Big 6',    92.5,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-034',4,8,5,4,6,4,'Fientes fraiches', DATE '2024-08-01',DATE '2024-08-08',DATE '2024-08-03',DATE '2024-08-05','Non conforme',    2,0,'Souche détectée ne correspond pas au bâtiment déclaré','Ross 708', 74.0,2,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-035',5,10,6,3,5,1,'Sang',            DATE '2024-08-05',DATE '2024-08-12',DATE '2024-08-07',DATE '2024-08-09','Terminée',        5,1,NULL,'Lohmann Brown',96.5,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-036',6,12,7,5,8,1,'Organes',         DATE '2024-08-10',DATE '2024-08-17',DATE '2024-08-12',DATE '2024-08-14','Terminée',        3,1,NULL,'Ross 308',     87.0,3,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-037',1,1,1,1,1,3,'Fiente',           DATE '2024-08-15',DATE '2024-08-22',DATE '2024-08-17',DATE '2024-08-19','Terminée',        1,1,NULL,'Ross 308',     98.5,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-038',2,3,2,3,4,1,'Frottis trachéal', DATE '2024-08-20',DATE '2024-08-27',DATE '2024-08-22',DATE '2024-08-24','Terminée',        4,1,NULL,'Ross 308',     90.0,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-039',3,5,3,2,3,2,'Sang',             DATE '2024-09-01',DATE '2024-09-08',DATE '2024-09-03',DATE '2024-09-05','Critique',        1,0,'Virus Newcastle identifié, abattage préventif requis','BUT Big 6', 47.0,1,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-040',4,7,4,3,5,4,'Écouvillon trachéal',DATE '2024-09-05',DATE '2024-09-12',DATE '2024-09-07',DATE '2024-09-09','Terminée',     2,1,NULL,'Cobb 500',     88.0,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-041',5,9,5,4,6,1,'Fientes fraiches', DATE '2024-09-10',DATE '2024-09-17',DATE '2024-09-12',DATE '2024-09-14','Terminée',        3,1,NULL,'Lohmann Brown',93.5,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-042',6,11,6,5,8,5,'Sang',            DATE '2024-09-15',DATE '2024-09-22',DATE '2024-09-17',DATE '2024-09-19','Non conforme',    1,0,'Prélèvement non conforme : délai de conservation dépassé','Ross 708', 68.0,2,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-043',1,2,7,1,2,1,'Organes',          DATE '2024-09-20',DATE '2024-09-27',DATE '2024-09-22',DATE '2024-09-24','Terminée',        4,1,NULL,'Cobb 500',     91.5,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-044',2,4,1,3,4,1,'Fiente',           DATE '2024-10-01',DATE '2024-10-08',DATE '2024-10-03',DATE '2024-10-05','Terminée',        5,1,NULL,'Hubbard Flex', 89.0,3,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-045',3,6,2,2,3,2,'Frottis trachéal', DATE '2024-10-05',DATE '2024-10-12',DATE '2024-10-07',DATE '2024-10-09','Terminée',        2,1,NULL,'BUT Big 6',    94.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-046',4,8,3,4,6,4,'Sang',             DATE '2024-10-10',DATE '2024-10-17',DATE '2024-10-12',DATE '2024-10-14','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Cobb 500',  53.0,1,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-047',5,10,4,3,5,1,'Écouvillon trachéal',DATE '2024-10-15',DATE '2024-10-22',DATE '2024-10-17',DATE '2024-10-19','Terminée',    3,1,NULL,'Lohmann Brown',95.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-048',6,12,5,5,8,1,'Fientes fraiches', DATE '2024-10-20',DATE '2024-10-27',DATE '2024-10-22',DATE '2024-10-24','Non conforme',   2,0,'Résultat inférieur au seuil de sécurité (< 85%)','Ross 308',   72.0,2,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-049',1,1,6,1,1,3,'Sang',             DATE '2024-11-01',DATE '2024-11-08',DATE '2024-11-03',DATE '2024-11-05','Terminée',        4,1,NULL,'Ross 308',     96.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-050',2,3,7,3,4,5,'Organes',          DATE '2024-11-05',DATE '2024-11-12',DATE '2024-11-07',DATE '2024-11-09','Terminée',        3,1,NULL,'Ross 308',     88.5,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-051',3,5,1,2,3,2,'Fiente',           DATE '2024-11-10',DATE '2024-11-17',DATE '2024-11-12',DATE '2024-11-14','Terminée',        2,1,NULL,'BUT Big 6',    92.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-052',4,7,2,3,5,4,'Frottis trachéal', DATE '2024-11-15',DATE '2024-11-22',DATE '2024-11-17',DATE '2024-11-19','Terminée',        5,1,NULL,'Cobb 500',     90.5,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-053',5,9,3,4,6,1,'Sang',             DATE '2024-11-20',DATE '2024-11-27',DATE '2024-11-22',DATE '2024-11-24','Critique',        1,0,'Virus Newcastle identifié, abattage préventif requis','Lohmann Brown',46.5,1,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-054',6,11,4,5,8,1,'Écouvillon trachéal',DATE '2024-12-01',DATE '2024-12-08',DATE '2024-12-03',DATE '2024-12-05','Terminée',    3,1,NULL,'Ross 708',     87.5,3,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-055',1,2,5,1,2,5,'Fientes fraiches', DATE '2024-12-05',DATE '2024-12-12',DATE '2024-12-07',DATE '2024-12-09','Terminée',        4,1,NULL,'Cobb 500',     91.0,4,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-056',2,4,6,3,4,1,'Sang',             DATE '2024-12-10',DATE '2024-12-17',DATE '2024-12-12',DATE '2024-12-14','Non conforme',    2,0,'Souche détectée ne correspond pas au bâtiment déclaré','Hybro G+',  77.5,2,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-057',3,6,7,2,3,3,'Organes',          DATE '2024-12-15',DATE '2024-12-22',DATE '2024-12-17',DATE '2024-12-19','Terminée',        3,1,NULL,'BUT Big 6',    93.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-058',4,8,1,4,6,4,'Fiente',           DATE '2025-01-05',DATE '2025-01-12',DATE '2025-01-07',DATE '2025-01-09','Terminée',        1,1,NULL,'Cobb 500',     97.0,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-059',5,10,2,3,5,1,'Frottis trachéal',DATE '2025-01-10',DATE '2025-01-17',DATE '2025-01-12',DATE '2025-01-14','Terminée',        2,1,NULL,'Lohmann Brown',94.5,5,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-060',6,12,3,5,8,5,'Sang',            DATE '2025-01-15',DATE '2025-01-22',DATE '2025-01-17',DATE '2025-01-19','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Ross 308',  50.0,1,NULL);
INSERT INTO demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-061',1,1,4,1,1,1,'Écouvillon trachéal',DATE '2025-02-01',DATE '2025-02-08',DATE '2025-02-03',DATE '2025-02-05','Terminée',     3,1,NULL,'Ross 308',     95.5,5,NULL);

-- HISTORIQUE MALADIE
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (1,1,4, DATE '2024-02-01',NULL,           0,'Quarantaine + traitement antibiotique','2,3');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (2,2,2, DATE '2024-01-15',DATE '2024-02-28',1,'Abattage préventif et désinfection totale','1,3,4');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (6,2,18,DATE '2024-04-20',NULL,           0,'Vaccination de rappel, surveillance renforcée','5');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (5,1,11,DATE '2024-03-10',NULL,           0,'Isolement et antibiothérapie','4,6');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (6,1,30,DATE '2024-07-05',NULL,           0,'Quarantaine + nettoyage profond','5');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (3,2,39,DATE '2024-09-01',NULL,           0,'Abattage préventif, signalement autorités','4,5');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (4,1,46,DATE '2024-10-10',NULL,           0,'Traitement antibiotique, contrôle eau','3,5');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (5,2,53,DATE '2024-11-20',NULL,           0,'Vaccination urgente, quarantaine','4,6');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (6,1,60,DATE '2025-01-15',NULL,           0,'Isolement fientes, analyse eau','5');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (1,3,NULL,DATE '2023-09-10',DATE '2023-10-20',1,'Vaccination Gumboro + surveillance','2');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (2,4,NULL,DATE '2023-11-05',DATE '2023-12-15',1,'Antibiothérapie ciblée','3');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (3,5,NULL,DATE '2024-04-15',DATE '2024-05-10',1,'Antiparasitaire eau de boisson','4,5');
INSERT INTO historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (4,6,NULL,DATE '2023-06-20',DATE '2023-07-30',1,'Vaccination Marek renforcée','5');

-- STAT LABORANTIN
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (1,1,87, 98.5,4.5);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (1,5,45, 97.0,2.0);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (2,2,64, 97.0,2.8);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (2,6,52, 98.0,3.5);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (3,3,73, 96.5,3.8);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (3,6,38, 97.5,4.0);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (4,1,112,99.0,4.2);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (4,7,61, 95.5,4.8);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (5,2,89, 96.0,2.5);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (5,4,44, 97.0,3.0);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (6,3,95, 98.0,3.6);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (6,6,57, 96.5,4.1);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (7,2,78, 94.0,2.9);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (7,5,33, 93.5,2.2);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (8,1,101,97.5,4.6);
INSERT INTO stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (8,4,66, 96.0,3.2);

COMMIT;


-- ============================================================
-- 4. VIEWS OPÉRATIONNELLES
-- ============================================================

CREATE OR REPLACE VIEW vue_batiment_complet AS
SELECT b.id_batiment, b.nom_batiment,
       c.nom_centre, m.nom_marque, f.nom_filiale,
       c.gouvernorat, s.nom_souche, s.type_produit_final,
       s.fertilite_score, s.taux_mortalite, b.capacite
FROM batiment b
JOIN centre_elevage c ON b.id_centre = c.id_centre
JOIN marque m         ON c.id_marque = m.id_marque
JOIN filiale f        ON m.id_filiale = f.id_filiale
JOIN souche s         ON b.id_souche  = s.id_souche;

CREATE OR REPLACE VIEW vue_alertes_actives AS
SELECT d.num_analyse, d.statut, d.priorite,
       c.nom_centre, b.nom_batiment, t.libelle,
       d.raison_non_conformite, d.date_resultat
FROM demande_analyse d
JOIN centre_elevage c  ON d.id_centre       = c.id_centre
LEFT JOIN batiment b   ON d.id_batiment     = b.id_batiment
JOIN type_analyse t    ON d.id_type_analyse = t.id_type_analyse
WHERE d.statut IN ('Non conforme','Critique');

CREATE OR REPLACE VIEW vue_meilleur_laborantin AS
SELECT * FROM (
    SELECT t.libelle                   AS type_analyse,
           l.prenom || ' ' || l.nom   AS laborantin,
           lab.nom_labo,
           s.taux_conformite,
           s.duree_moy_jours,
           ROW_NUMBER() OVER (
               PARTITION BY t.id_type_analyse
               ORDER BY s.taux_conformite DESC, s.duree_moy_jours ASC
           ) rn
    FROM stat_laborantin s
    JOIN laborantin  l   ON s.id_laborantin   = l.id_laborantin
    JOIN laboratoire lab ON l.id_labo         = lab.id_labo
    JOIN type_analyse t  ON s.id_type_analyse = t.id_type_analyse
    WHERE l.disponible = 1
) WHERE rn = 1;

-- ============================================================
-- 4. VIEWS IA CHATBOT
-- ============================================================

CREATE OR REPLACE VIEW vue_centres_risque AS
SELECT c.nom_centre,
       COUNT(*)               AS nb_alertes,
       MAX(d.date_resultat)   AS derniere_alerte
FROM demande_analyse d
JOIN centre_elevage c ON d.id_centre = c.id_centre
WHERE d.statut IN ('Non conforme','Critique')
GROUP BY c.nom_centre
HAVING COUNT(*) >= 1;

CREATE OR REPLACE VIEW vue_recommandation_laborantin AS
SELECT t.libelle,
       l.prenom || ' ' || l.nom AS laborantin,
       lab.nom_labo,
       s.taux_conformite,
       s.duree_moy_jours
FROM stat_laborantin s
JOIN laborantin  l   ON s.id_laborantin   = l.id_laborantin
JOIN laboratoire lab ON l.id_labo         = lab.id_labo
JOIN type_analyse t  ON s.id_type_analyse = t.id_type_analyse
WHERE l.disponible = 1
  AND s.taux_conformite > 97;

CREATE OR REPLACE VIEW vue_urgence_analyse AS
SELECT num_analyse, statut, priorite, date_decheance,
       SYSDATE - date_prelevement AS jours_attente
FROM demande_analyse
WHERE statut IN ('En attente','En cours')
  AND priorite <= 2;

CREATE OR REPLACE VIEW vue_dashboard_ia AS
SELECT
    (SELECT COUNT(*) FROM demande_analyse)                               AS total_analyses,
    (SELECT COUNT(*) FROM demande_analyse WHERE statut = 'Critique')     AS critiques,
    (SELECT COUNT(*) FROM demande_analyse WHERE statut = 'Non conforme') AS non_conformes,
    (SELECT COUNT(*) FROM demande_analyse WHERE statut = 'En attente')   AS attente
FROM dual;

CREATE OR REPLACE VIEW vue_maladies_actives AS
SELECT m.nom_maladie, m.type_agent, m.est_critique,
       c.nom_centre, c.gouvernorat,
       hm.date_detection, hm.mesures_prises,
       hm.centres_contamines_potentiels
FROM historique_maladie hm
JOIN maladie       m ON hm.id_maladie = m.id_maladie
JOIN centre_elevage c ON hm.id_centre = c.id_centre
WHERE hm.est_resolu = 0
ORDER BY m.est_critique DESC, hm.date_detection DESC;

COMMIT;
-- ============================================================
-- FIN
-- ============================================================