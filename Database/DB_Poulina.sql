-- ============================================================
-- POULINA – RESET COMPLET POUR SQL SERVER
-- Drop + Recreate + Insert
-- SQL Server 2019+ (IDENTITY, INT, NVARCHAR(MAX))
-- ============================================================

USE [master];
GO

-- Vérifier et supprimer la BD existante
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'POULINA')
BEGIN
    ALTER DATABASE POULINA SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE POULINA;
END
GO

-- Créer la BD
CREATE DATABASE POULINA;
GO

USE POULINA;
GO

-- ============================================================
-- 1. DROP TABLES (ordre inverse des FK)
-- ============================================================

IF OBJECT_ID('dbo.stat_laborantin', 'U') IS NOT NULL
    DROP TABLE dbo.stat_laborantin;
GO

IF OBJECT_ID('dbo.historique_maladie', 'U') IS NOT NULL
    DROP TABLE dbo.historique_maladie;
GO

IF OBJECT_ID('dbo.demande_analyse', 'U') IS NOT NULL
    DROP TABLE dbo.demande_analyse;
GO

IF OBJECT_ID('dbo.batiment', 'U') IS NOT NULL
    DROP TABLE dbo.batiment;
GO

IF OBJECT_ID('dbo.laborantin', 'U') IS NOT NULL
    DROP TABLE dbo.laborantin;
GO

IF OBJECT_ID('dbo.laboratoire', 'U') IS NOT NULL
    DROP TABLE dbo.laboratoire;
GO

IF OBJECT_ID('dbo.centre_elevage', 'U') IS NOT NULL
    DROP TABLE dbo.centre_elevage;
GO

IF OBJECT_ID('dbo.type_analyse', 'U') IS NOT NULL
    DROP TABLE dbo.type_analyse;
GO

IF OBJECT_ID('dbo.souche', 'U') IS NOT NULL
    DROP TABLE dbo.souche;
GO

IF OBJECT_ID('dbo.maladie', 'U') IS NOT NULL
    DROP TABLE dbo.maladie;
GO

IF OBJECT_ID('dbo.marque', 'U') IS NOT NULL
    DROP TABLE dbo.marque;
GO

IF OBJECT_ID('dbo.pays', 'U') IS NOT NULL
    DROP TABLE dbo.pays;
GO

IF OBJECT_ID('dbo.filiale', 'U') IS NOT NULL
    DROP TABLE dbo.filiale;
GO

-- Drop views
IF OBJECT_ID('dbo.vue_batiment_complet', 'V') IS NOT NULL
    DROP VIEW dbo.vue_batiment_complet;
GO

IF OBJECT_ID('dbo.vue_alertes_actives', 'V') IS NOT NULL
    DROP VIEW dbo.vue_alertes_actives;
GO

IF OBJECT_ID('dbo.vue_meilleur_laborantin', 'V') IS NOT NULL
    DROP VIEW dbo.vue_meilleur_laborantin;
GO

IF OBJECT_ID('dbo.vue_centres_risque', 'V') IS NOT NULL
    DROP VIEW dbo.vue_centres_risque;
GO

IF OBJECT_ID('dbo.vue_recommandation_laborantin', 'V') IS NOT NULL
    DROP VIEW dbo.vue_recommandation_laborantin;
GO

IF OBJECT_ID('dbo.vue_urgence_analyse', 'V') IS NOT NULL
    DROP VIEW dbo.vue_urgence_analyse;
GO

IF OBJECT_ID('dbo.vue_dashboard_ia', 'V') IS NOT NULL
    DROP VIEW dbo.vue_dashboard_ia;
GO

IF OBJECT_ID('dbo.vue_maladies_actives', 'V') IS NOT NULL
    DROP VIEW dbo.vue_maladies_actives;
GO

-- ============================================================
-- 2. CREATE TABLES
-- ============================================================

CREATE TABLE dbo.filiale (
    id_filiale INT PRIMARY KEY,
    nom_filiale NVARCHAR(100) NOT NULL,
    secteur NVARCHAR(50) NOT NULL
);

CREATE TABLE dbo.pays (
    id_pays INT IDENTITY(1,1) PRIMARY KEY,
    nom_pays NVARCHAR(100) NOT NULL,
    code_iso CHAR(3) NOT NULL
);

CREATE TABLE dbo.marque (
    id_marque INT IDENTITY(1,1) PRIMARY KEY,
    nom_marque NVARCHAR(100) NOT NULL,
    id_filiale INT NOT NULL,
    CONSTRAINT fk_marque_filiale FOREIGN KEY (id_filiale) REFERENCES dbo.filiale(id_filiale)
);

CREATE TABLE dbo.souche (
    id_souche INT IDENTITY(1,1) PRIMARY KEY,
    nom_souche NVARCHAR(150) NOT NULL,
    type_produit_final NVARCHAR(50) NOT NULL,
    fertilite_score DECIMAL(5,2),
    taux_mortalite DECIMAL(5,2),
    resistance_maladies NVARCHAR(200),
    cout_unitaire DECIMAL(10,3),
    id_pays_origine INT,
    notes NVARCHAR(MAX),
    CONSTRAINT fk_souche_pays FOREIGN KEY (id_pays_origine) REFERENCES dbo.pays(id_pays)
);

CREATE TABLE dbo.maladie (
    id_maladie INT IDENTITY(1,1) PRIMARY KEY,
    nom_maladie NVARCHAR(150) NOT NULL,
    type_agent NVARCHAR(50) NOT NULL,
    taux_transmission DECIMAL(5,2),
    taux_mortalite DECIMAL(5,2),
    impact_fertilite DECIMAL(5,2),
    est_critique BIT DEFAULT 0,
    description NVARCHAR(MAX)
);

CREATE TABLE dbo.centre_elevage (
    id_centre INT IDENTITY(1,1) PRIMARY KEY,
    nom_centre NVARCHAR(150) NOT NULL,
    localisation NVARCHAR(200) NOT NULL,
    gouvernorat NVARCHAR(100),
    id_marque INT NOT NULL,
    type_production NVARCHAR(50),
    capacite_totale INT,
    date_creation DATE,
    actif BIT DEFAULT 1,
    CONSTRAINT fk_centre_marque FOREIGN KEY (id_marque) REFERENCES dbo.marque(id_marque)
);

CREATE TABLE dbo.batiment (
    id_batiment INT IDENTITY(1,1) PRIMARY KEY,
    nom_batiment NVARCHAR(100) NOT NULL,
    id_centre INT NOT NULL,
    id_souche INT NOT NULL,
    capacite INT,
    date_mise_en_service DATE,
    actif BIT DEFAULT 1,
    CONSTRAINT fk_batiment_centre FOREIGN KEY (id_centre) REFERENCES dbo.centre_elevage(id_centre),
    CONSTRAINT fk_batiment_souche FOREIGN KEY (id_souche) REFERENCES dbo.souche(id_souche)
);

CREATE TABLE dbo.laboratoire (
    id_labo INT IDENTITY(1,1) PRIMARY KEY,
    nom_labo NVARCHAR(200) NOT NULL,
    adresse NVARCHAR(300),
    gouvernorat NVARCHAR(100),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    telephone NVARCHAR(30),
    email NVARCHAR(150),
    specialites NVARCHAR(MAX),
    actif BIT DEFAULT 1
);

CREATE TABLE dbo.laborantin (
    id_laborantin INT IDENTITY(1,1) PRIMARY KEY,
    prenom NVARCHAR(100) NOT NULL,
    nom NVARCHAR(100) NOT NULL,
    id_labo INT NOT NULL,
    specialite NVARCHAR(200),
    annees_experience INT,
    disponible BIT DEFAULT 1,
    email NVARCHAR(150),
    telephone NVARCHAR(30),
    CONSTRAINT fk_laborantin_labo FOREIGN KEY (id_labo) REFERENCES dbo.laboratoire(id_labo)
);

CREATE TABLE dbo.type_analyse (
    id_type_analyse INT IDENTITY(1,1) PRIMARY KEY,
    code_analyse NVARCHAR(30) UNIQUE NOT NULL,
    libelle NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX),
    duree_jours INT,
    type_echantillon NVARCHAR(100)
);

CREATE TABLE dbo.demande_analyse (
    id_demande INT IDENTITY(1,1) PRIMARY KEY,
    num_analyse NVARCHAR(50) UNIQUE NOT NULL,
    id_centre INT NOT NULL,
    id_batiment INT,
    id_type_analyse INT NOT NULL,
    id_labo INT,
    id_laborantin INT,
    id_pays_provenance INT,
    type_echantillon NVARCHAR(100),
    date_prelevement DATE NOT NULL,
    date_decheance DATE,
    date_analyse DATE,
    date_resultat DATE,
    statut NVARCHAR(50) DEFAULT 'En attente',
    priorite INT CHECK (priorite BETWEEN 1 AND 5),
    est_conforme BIT,
    raison_non_conformite NVARCHAR(MAX),
    resultat_souche_detectee NVARCHAR(200),
    pourcentage_securite DECIMAL(5,2),
    niveau_satisfaction INT CHECK (niveau_satisfaction BETWEEN 1 AND 5),
    observations NVARCHAR(MAX),
    CONSTRAINT fk_da_centre FOREIGN KEY (id_centre) REFERENCES dbo.centre_elevage(id_centre),
    CONSTRAINT fk_da_batiment FOREIGN KEY (id_batiment) REFERENCES dbo.batiment(id_batiment),
    CONSTRAINT fk_da_type FOREIGN KEY (id_type_analyse) REFERENCES dbo.type_analyse(id_type_analyse),
    CONSTRAINT fk_da_labo FOREIGN KEY (id_labo) REFERENCES dbo.laboratoire(id_labo),
    CONSTRAINT fk_da_laborantin FOREIGN KEY (id_laborantin) REFERENCES dbo.laborantin(id_laborantin),
    CONSTRAINT fk_da_pays FOREIGN KEY (id_pays_provenance) REFERENCES dbo.pays(id_pays)
);

CREATE TABLE dbo.historique_maladie (
    id_historique INT IDENTITY(1,1) PRIMARY KEY,
    id_centre INT NOT NULL,
    id_maladie INT NOT NULL,
    id_demande INT,
    date_detection DATE NOT NULL,
    date_resolution DATE,
    est_resolu BIT DEFAULT 0,
    mesures_prises NVARCHAR(MAX),
    centres_contamines_potentiels NVARCHAR(200),
    CONSTRAINT fk_hist_centre FOREIGN KEY (id_centre) REFERENCES dbo.centre_elevage(id_centre),
    CONSTRAINT fk_hist_maladie FOREIGN KEY (id_maladie) REFERENCES dbo.maladie(id_maladie),
    CONSTRAINT fk_hist_demande FOREIGN KEY (id_demande) REFERENCES dbo.demande_analyse(id_demande)
);

CREATE TABLE dbo.stat_laborantin (
    id_stat INT IDENTITY(1,1) PRIMARY KEY,
    id_laborantin INT NOT NULL,
    id_type_analyse INT NOT NULL,
    nb_analyses_effectuees INT DEFAULT 0,
    taux_conformite DECIMAL(5,2),
    duree_moy_jours DECIMAL(4,1),
    CONSTRAINT fk_stat_laborantin FOREIGN KEY (id_laborantin) REFERENCES dbo.laborantin(id_laborantin),
    CONSTRAINT fk_stat_type FOREIGN KEY (id_type_analyse) REFERENCES dbo.type_analyse(id_type_analyse)
);

-- ============================================================
-- 3. INSERT DONNÉES
-- ============================================================

-- FILIALE
INSERT INTO dbo.filiale VALUES (1, 'Poulina Avicole',          'Avicole');
INSERT INTO dbo.filiale VALUES (2, 'Poulina Agro-Alimentaire', 'Agro-Alimentaire');

-- PAYS
INSERT INTO dbo.pays (nom_pays, code_iso) VALUES ('Tunisie',   'TUN');
INSERT INTO dbo.pays (nom_pays, code_iso) VALUES ('France',    'FRA');
INSERT INTO dbo.pays (nom_pays, code_iso) VALUES ('Belgique',  'BEL');
INSERT INTO dbo.pays (nom_pays, code_iso) VALUES ('Allemagne', 'DEU');
INSERT INTO dbo.pays (nom_pays, code_iso) VALUES ('Pays-Bas',  'NLD');
INSERT INTO dbo.pays (nom_pays, code_iso) VALUES ('Espagne',   'ESP');

-- MARQUE
INSERT INTO dbo.marque (nom_marque, id_filiale) VALUES ('Dick',   1);
INSERT INTO dbo.marque (nom_marque, id_filiale) VALUES ('SNA',    1);
INSERT INTO dbo.marque (nom_marque, id_filiale) VALUES ('Gipa',   2);
INSERT INTO dbo.marque (nom_marque, id_filiale) VALUES ('MedOil', 2);

-- SOUCHE
INSERT INTO dbo.souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Ross 308',      'Poulet', 94.5, 3.2, 'Faible Salmonelle',  2.800, 5, 'Croissance rapide, conversion élevée');

INSERT INTO dbo.souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Cobb 500',      'Poulet', 93.8, 3.5, 'Moyenne',            2.650, 5, 'Bonne conversion alimentaire');

INSERT INTO dbo.souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Hubbard Flex',  'Poulet', 92.1, 4.1, 'Bonne',              2.500, 2, 'Adaptée aux climats chauds');

INSERT INTO dbo.souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Lohmann Brown', 'Oeuf',   96.0, 1.8, 'Très résistante',    3.100, 3, 'Haute ponte, résistance maladies');

INSERT INTO dbo.souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Ross 708',      'Poulet', 95.2, 2.9, 'Bonne',              2.950, 5, 'Performance maximale, standard export');

INSERT INTO dbo.souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('BUT Big 6',     'Dinde',  88.0, 5.1, 'Faible',             4.200, 2, 'Dinde commerciale lourde');

INSERT INTO dbo.souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite, resistance_maladies, cout_unitaire, id_pays_origine, notes)
VALUES ('Hybro G+',      'Poulet', 93.0, 3.8, 'Moyenne',            2.700, 4, 'Polyvalente, adaptable');

-- MALADIE
INSERT INTO dbo.maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Salmonelle',           'Bactérie',  45.0, 8.0,  25.0, 1, 'Zoonose majeure, transmission par fèces et eau contaminée');

INSERT INTO dbo.maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Newcastle',            'Virus',     80.0, 60.0, 40.0, 1, 'Maladie de Newcastle, déclaration obligatoire, pandémique');

INSERT INTO dbo.maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Gumboro',              'Virus',     55.0, 20.0, 15.0, 0, 'Immunodépresseur, touche principalement les poussins 3-6 semaines');

INSERT INTO dbo.maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Mycoplasme',           'Bactérie',  35.0,  5.0, 20.0, 0, 'Maladie chronique respiratoire, impact pondeuses');

INSERT INTO dbo.maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Coccidiose',           'Parasite',  40.0, 10.0, 30.0, 0, 'Parasite intestinal fréquent, traitement antiparasitaire');

INSERT INTO dbo.maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Marek',                'Virus',     70.0, 25.0, 10.0, 0, 'Herpesvirus, lymphomes, vaccination jour 1');

INSERT INTO dbo.maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite, impact_fertilite, est_critique, description)
VALUES ('Bronchite infectieuse','Virus',     60.0, 15.0, 35.0, 0, 'IB, tropisme respiratoire et rénal, nombreux sérotypes');

-- CENTRE ELEVAGE
INSERT INTO dbo.centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre Dick Nord',   'Route Mateur km 12',        'Bizerte',  1, 'Poulet', 80000, '2010-03-15', 1);

INSERT INTO dbo.centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre Dick Sud',    'Zone Industrielle Sfax',    'Sfax',     1, 'Poulet', 60000, '2012-07-01', 1);

INSERT INTO dbo.centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre SNA Tunis',   'Ariana Zone Nord',          'Ariana',   2, 'Dinde',  30000, '2008-09-10', 1);

INSERT INTO dbo.centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre Dick Est',    'Nabeul Route Côtière',      'Nabeul',   1, 'Poulet', 50000, '2015-04-20', 1);

INSERT INTO dbo.centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre SNA Sousse',  'Zone Industrielle Sousse',  'Sousse',   2, 'Oeuf',   40000, '2017-01-05', 1);

INSERT INTO dbo.centre_elevage (nom_centre, localisation, gouvernorat, id_marque, type_production, capacite_totale, date_creation, actif)
VALUES ('Centre Dick Centre', 'Kairouan Route Nationale',  'Kairouan', 1, 'Poulet', 70000, '2013-06-12', 1);

-- BATIMENT
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment A1', 1, 1, 15000, '2010-03-15', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment A2', 1, 2, 15000, '2011-06-01', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment B1', 2, 1, 12000, '2012-07-01', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment B2', 2, 5, 12000, '2013-02-15', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment C1', 3, 6, 10000, '2008-09-10', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment C2', 3, 7, 10000, '2010-05-20', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment D1', 4, 2, 12000, '2015-04-20', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment D2', 4, 3, 12000, '2016-08-10', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment E1', 5, 4, 10000, '2017-01-05', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment E2', 5, 4, 10000, '2018-03-01', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment F1', 6, 1, 15000, '2013-06-12', 1);
INSERT INTO dbo.batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif) VALUES ('Batiment F2', 6, 5, 15000, '2014-11-01', 1);

-- LABORATOIRE
INSERT INTO dbo.laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Labo Central Tunis',  'Rue de la Liberté, Tunis',      'Tunis',   36.819000, 10.166300, '+21671123456', 'central@labo.tn',  'PCR, Virologie, Bactériologie, ELISA', 1);

INSERT INTO dbo.laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Pasteur Tunis',        'Avenue Pasteur, Tunis',         'Tunis',   36.818500, 10.170200, '+21671987654', 'pasteur@labo.tn',  'Virologie, Immunologie, Influenza', 1);

INSERT INTO dbo.laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Labo Sfax Avicole',    'Zone Industrielle, Sfax',       'Sfax',    34.740000, 10.760000, '+21674111222', 'sfax@labo.tn',     'Bactériologie, PCR, Salmonelle', 1);

INSERT INTO dbo.laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Labo Sousse Bio',      'Avenue Mohammed V, Sousse',     'Sousse',  35.833300, 10.637800, '+21673333444', 'sousse@labo.tn',   'ELISA, Sérologie, PCR', 1);

INSERT INTO dbo.laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude, telephone, email, specialites, actif)
VALUES ('Institut Vét Bizerte', 'Route Mateur, Bizerte',         'Bizerte', 37.274400,  9.873900, '+21672555666', 'bizerte@labo.tn',  'PCR, Bactériologie, Parasitologie', 1);

-- LABORANTIN
INSERT INTO dbo.laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Sami',    'Bouaziz',   1, 'Salmonelle, Bactériologie',  12, 1, 'sami.bouaziz@labo.tn',   '+216221001');

INSERT INTO dbo.laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Nadia',   'Trabelsi',  1, 'PCR, Virologie',              8, 1, 'nadia.trabelsi@labo.tn', '+216221002');

INSERT INTO dbo.laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Karim',   'Ben Ali',   2, 'Immunologie, ELISA',           6, 1, 'karim.benali@labo.tn',  '+216221003');

INSERT INTO dbo.laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Fatma',   'Mansouri',  3, 'Bactériologie, Salmonelle',   10, 1, 'fatma.mansouri@labo.tn','+216221004');

INSERT INTO dbo.laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Youssef', 'Dridi',     3, 'PCR, Newcastle',               5, 1, 'youssef.dridi@labo.tn', '+216221005');

INSERT INTO dbo.laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Amira',   'Khelifi',   4, 'Sérologie, ELISA',             7, 1, 'amira.khelifi@labo.tn', '+216221006');

INSERT INTO dbo.laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Bilel',   'Gharbi',    5, 'PCR, Parasitologie',           9, 0, 'bilel.gharbi@labo.tn',  '+216221007');

INSERT INTO dbo.laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
VALUES ('Rania',   'Chabbi',    5, 'Bactériologie, PCR',           4, 1, 'rania.chabbi@labo.tn',  '+216221008');

-- TYPE ANALYSE
INSERT INTO dbo.type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('BACTE-SAL', 'Bactériologie Salmonelle',    'Recherche et identification Salmonella spp.',    5, 'Fiente');

INSERT INTO dbo.type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('PCR-ND',    'PCR Newcastle',               'Détection virus Newcastle par PCR temps réel',   3, 'Frottis trachéal');

INSERT INTO dbo.type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('ELISA-IBD', 'Sérologie Gumboro ELISA',    'Titrage anticorps anti-IBD',                     4, 'Sang');

INSERT INTO dbo.type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('PCR-MG',    'PCR Mycoplasme',              'Détection Mycoplasma gallisepticum',              3, 'Écouvillon trachéal');

INSERT INTO dbo.type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('PARASIT',   'Parasitologie Coccidiose',    'Examen coprologique + identification oocystes',  2, 'Fientes fraiches');

INSERT INTO dbo.type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('SERO-ND',   'Sérologie Newcastle HI',      'Inhibition hémagglutination ND',                 4, 'Sang');

INSERT INTO dbo.type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
VALUES ('BACTE-COL', 'Bactériologie E.coli',        'Antibiogramme E.coli pathogènes',                5, 'Organes');

-- ============================================================
-- DEMANDE ANALYSE (61 analyses)
-- ============================================================

INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-001',1,1,1,1,1,1,'Fiente',           '2024-01-10','2024-01-17','2024-01-12','2024-01-14','Terminée',        1,1,NULL,'Ross 308',     98.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-002',2,3,2,3,4,1,'Frottis trachéal', '2024-01-15','2024-01-22','2024-01-17','2024-01-19','Non conforme',    2,0,'Virus Newcastle identifié, abattage préventif requis','Ross 308',52.0,2,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-003',3,5,3,2,3,2,'Sang',             '2024-01-20','2024-01-27','2024-01-23','2024-01-25','Terminée',        3,1,NULL,'BUT Big 6',    91.5,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-004',4,7,1,3,4,5,'Fiente',           '2024-02-01','2024-02-08','2024-02-03','2024-02-05','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Cobb 500',48.5,1,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-005',5,9,4,4,6,3,'Écouvillon trachéal','2024-02-05','2024-02-12','2024-02-07','2024-02-09','Terminée',      2,1,NULL,'Lohmann Brown',93.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-006',6,11,5,5,8,1,'Fientes fraiches', '2024-02-10','2024-02-17','2024-02-13','2024-02-14','Terminée',       3,1,NULL,'Ross 308',     89.0,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-007',1,2,6,1,2,5,'Sang',             '2024-02-15','2024-02-22','2024-02-18','2024-02-20','Terminée',        4,1,NULL,'Cobb 500',     95.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-008',2,4,7,3,5,1,'Organes',          '2024-02-20','2024-02-27','2024-02-22','2024-02-24','Non conforme',    2,0,'Résultat inférieur au seuil de sécurité (< 85%)','Hubbard Flex',71.0,2,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-009',3,6,2,2,3,2,'Frottis trachéal', '2024-03-01','2024-03-08','2024-03-04','2024-03-06','Terminée',        3,1,NULL,'BUT Big 6',    90.5,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-010',4,8,3,4,6,4,'Sang',             '2024-03-05','2024-03-12','2024-03-07','2024-03-09','Terminée',        1,1,NULL,'Cobb 500',     96.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-011',5,10,1,3,4,1,'Fiente',          '2024-03-10','2024-03-17','2024-03-12','2024-03-14','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Lohmann Brown',55.0,1,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-012',6,12,4,5,8,1,'Écouvillon trachéal','2024-03-15','2024-03-22','2024-03-18','2024-03-20','Terminée',     2,1,NULL,'Ross 308',     88.0,3,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-013',1,1,5,1,1,3,'Fientes fraiches', '2024-03-20','2024-03-27','2024-03-22','2024-03-24','Terminée',        4,1,NULL,'Ross 308',     92.0,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-014',2,3,6,3,5,5,'Sang',             '2024-04-01','2024-04-08','2024-04-03','2024-04-05','Terminée',        3,1,NULL,'Ross 308',     97.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-015',3,5,7,2,3,2,'Organes',          '2024-04-05','2024-04-12','2024-04-08','2024-04-10','Non conforme',    2,0,'Souche détectée ne correspond pas au bâtiment déclaré','BUT Big 6',78.0,2,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-016',4,7,1,3,4,1,'Fiente',           '2024-04-10','2024-04-17','2024-04-13','2024-04-15','Terminée',        5,1,NULL,'Cobb 500',     91.0,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-017',5,9,2,4,6,4,'Frottis trachéal', '2024-04-15','2024-04-22','2024-04-17','2024-04-19','Terminée',        3,1,NULL,'Lohmann Brown',94.5,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-018',6,11,3,5,8,1,'Sang',            '2024-04-20','2024-04-27','2024-04-23','2024-04-25','Critique',        1,0,'Virus Newcastle identifié, abattage préventif requis','Ross 708',49.0,1,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-019',1,2,4,1,2,5,'Écouvillon trachéal','2024-05-01','2024-05-08','2024-05-03','2024-05-05','Terminée',      4,1,NULL,'Cobb 500',     87.5,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-020',2,4,5,3,4,1,'Fientes fraiches', '2024-05-05','2024-05-12','2024-05-07','2024-05-09','Terminée',        2,1,NULL,'Hubbard Flex', 90.0,3,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-021',3,6,6,2,3,3,'Sang',             '2024-05-10','2024-05-17','2024-05-13','2024-05-14','Terminée',        3,1,NULL,'BUT Big 6',    93.5,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-022',4,8,7,4,6,4,'Organes',          '2024-05-15','2024-05-22','2024-05-18','2024-05-20','Non conforme',    1,0,'Prélèvement non conforme : délai de conservation dépassé','Cobb 500',63.0,2,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-023',5,10,1,3,5,1,'Fiente',          '2024-05-20','2024-05-27','2024-05-22','2024-05-24','Terminée',        2,1,NULL,'Lohmann Brown',95.5,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-024',6,12,2,5,8,5,'Frottis trachéal','2024-06-01','2024-06-08','2024-06-03','2024-06-05','Terminée',        4,1,NULL,'Ross 308',     88.5,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-025',1,1,3,1,1,1,'Sang',             '2024-06-05','2024-06-12','2024-06-08','2024-06-10','Terminée',        3,1,NULL,'Ross 308',     94.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-026',2,3,4,3,4,1,'Écouvillon trachéal','2024-06-10','2024-06-17','2024-06-12','2024-06-14','Terminée',     5,1,NULL,'Ross 308',     86.0,3,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-027',3,5,5,2,3,2,'Fientes fraiches', '2024-06-15','2024-06-22','2024-06-18','2024-06-20','Non conforme',    2,0,'Résultat inférieur au seuil de sécurité (< 85%)','Hybro G+',   76.0,2,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-028',4,7,6,3,5,5,'Sang',             '2024-06-20','2024-06-27','2024-06-22','2024-06-24','Terminée',        1,1,NULL,'Cobb 500',     97.5,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-029',5,9,7,4,6,3,'Organes',          '2024-07-01','2024-07-08','2024-07-03','2024-07-05','Terminée',        3,1,NULL,'Lohmann Brown',91.0,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-030',6,11,1,5,8,1,'Fiente',          '2024-07-05','2024-07-12','2024-07-08','2024-07-10','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Ross 708', 51.0,1,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-031',1,2,2,1,2,1,'Frottis trachéal', '2024-07-10','2024-07-17','2024-07-12','2024-07-14','Terminée',        4,1,NULL,'Cobb 500',     93.0,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-032',2,4,3,3,4,5,'Sang',             '2024-07-15','2024-07-22','2024-07-17','2024-07-19','Terminée',        2,1,NULL,'Hubbard Flex', 89.5,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-033',3,6,4,2,3,2,'Écouvillon trachéal','2024-07-20','2024-07-27','2024-07-22','2024-07-24','Terminée',     3,1,NULL,'BUT Big 6',    92.5,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-034',4,8,5,4,6,4,'Fientes fraiches', '2024-08-01','2024-08-08','2024-08-03','2024-08-05','Non conforme',    2,0,'Souche détectée ne correspond pas au bâtiment déclaré','Ross 708', 74.0,2,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-035',5,10,6,3,5,1,'Sang',            '2024-08-05','2024-08-12','2024-08-07','2024-08-09','Terminée',        5,1,NULL,'Lohmann Brown',96.5,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-036',6,12,7,5,8,1,'Organes',         '2024-08-10','2024-08-17','2024-08-12','2024-08-14','Terminée',        3,1,NULL,'Ross 308',     87.0,3,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-037',1,1,1,1,1,3,'Fiente',           '2024-08-15','2024-08-22','2024-08-17','2024-08-19','Terminée',        1,1,NULL,'Ross 308',     98.5,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-038',2,3,2,3,4,1,'Frottis trachéal', '2024-08-20','2024-08-27','2024-08-22','2024-08-24','Terminée',        4,1,NULL,'Ross 308',     90.0,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-039',3,5,3,2,3,2,'Sang',             '2024-09-01','2024-09-08','2024-09-03','2024-09-05','Critique',        1,0,'Virus Newcastle identifié, abattage préventif requis','BUT Big 6', 47.0,1,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-040',4,7,4,3,5,4,'Écouvillon trachéal','2024-09-05','2024-09-12','2024-09-07','2024-09-09','Terminée',     2,1,NULL,'Cobb 500',     88.0,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-041',5,9,5,4,6,1,'Fientes fraiches', '2024-09-10','2024-09-17','2024-09-12','2024-09-14','Terminée',        3,1,NULL,'Lohmann Brown',93.5,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-042',6,11,6,5,8,5,'Sang',            '2024-09-15','2024-09-22','2024-09-17','2024-09-19','Non conforme',    1,0,'Prélèvement non conforme : délai de conservation dépassé','Ross 708', 68.0,2,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-043',1,2,7,1,2,1,'Organes',          '2024-09-20','2024-09-27','2024-09-22','2024-09-24','Terminée',        4,1,NULL,'Cobb 500',     91.5,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-044',2,4,1,3,4,1,'Fiente',           '2024-10-01','2024-10-08','2024-10-03','2024-10-05','Terminée',        5,1,NULL,'Hubbard Flex', 89.0,3,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-045',3,6,2,2,3,2,'Frottis trachéal', '2024-10-05','2024-10-12','2024-10-07','2024-10-09','Terminée',        2,1,NULL,'BUT Big 6',    94.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-046',4,8,3,4,6,4,'Sang',             '2024-10-10','2024-10-17','2024-10-12','2024-10-14','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Cobb 500',  53.0,1,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-047',5,10,4,3,5,1,'Écouvillon trachéal','2024-10-15','2024-10-22','2024-10-17','2024-10-19','Terminée',    3,1,NULL,'Lohmann Brown',95.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-048',6,12,5,5,8,1,'Fintes fraiches', '2024-10-20','2024-10-27','2024-10-22','2024-10-24','Non conforme',   2,0,'Résultat inférieur au seuil de sécurité (< 85%)','Ross 308',   72.0,2,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-049',1,1,6,1,1,3,'Sang',             '2024-11-01','2024-11-08','2024-11-03','2024-11-05','Terminée',        4,1,NULL,'Ross 308',     96.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-050',2,3,7,3,4,5,'Organes',          '2024-11-05','2024-11-12','2024-11-07','2024-11-09','Terminée',        3,1,NULL,'Ross 308',     88.5,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-051',3,5,1,2,3,2,'Fiente',           '2024-11-10','2024-11-17','2024-11-12','2024-11-14','Terminée',        2,1,NULL,'BUT Big 6',    92.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-052',4,7,2,3,5,4,'Frottis trachéal', '2024-11-15','2024-11-22','2024-11-17','2024-11-19','Terminée',        5,1,NULL,'Cobb 500',     90.5,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-053',5,9,3,4,6,1,'Sang',             '2024-11-20','2024-11-27','2024-11-22','2024-11-24','Critique',        1,0,'Virus Newcastle identifié, abattage préventif requis','Lohmann Brown',46.5,1,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-054',6,11,4,5,8,1,'Écouvillon trachéal','2024-12-01','2024-12-08','2024-12-03','2024-12-05','Terminée',    3,1,NULL,'Ross 708',     87.5,3,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-055',1,2,5,1,2,5,'Fientes fraiches', '2024-12-05','2024-12-12','2024-12-07','2024-12-09','Terminée',        4,1,NULL,'Cobb 500',     91.0,4,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-056',2,4,6,3,4,1,'Sang',             '2024-12-10','2024-12-17','2024-12-12','2024-12-14','Non conforme',    2,0,'Souche détectée ne correspond pas au bâtiment déclaré','Hybro G+',  77.5,2,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-057',3,6,7,2,3,3,'Organes',          '2024-12-15','2024-12-22','2024-12-17','2024-12-19','Terminée',        3,1,NULL,'BUT Big 6',    93.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-058',4,8,1,4,6,4,'Fiente',           '2025-01-05','2025-01-12','2025-01-07','2025-01-09','Terminée',        1,1,NULL,'Cobb 500',     97.0,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-059',5,10,2,3,5,1,'Frottis trachéal','2025-01-10','2025-01-17','2025-01-12','2025-01-14','Terminée',        2,1,NULL,'Lohmann Brown',94.5,5,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-060',6,12,3,5,8,5,'Sang',            '2025-01-15','2025-01-22','2025-01-17','2025-01-19','Critique',        1,0,'Salmonelle détectée au-delà du seuil réglementaire','Ross 308',  50.0,1,NULL);
INSERT INTO dbo.demande_analyse (num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,statut,priorite,est_conforme,raison_non_conformite,resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES ('ANA-061',1,1,4,1,1,1,'Écouvillon trachéal','2025-02-01','2025-02-08','2025-02-03','2025-02-05','Terminée',     3,1,NULL,'Ross 308',     95.5,5,NULL);

-- HISTORIQUE MALADIE
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (1,1,4, '2024-02-01',NULL,           0,'Quarantaine + traitement antibiotique','2,3');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (2,2,2, '2024-01-15','2024-02-28',1,'Abattage préventif et désinfection totale','1,3,4');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (6,2,18,'2024-04-20',NULL,           0,'Vaccination de rappel, surveillance renforcée','5');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (5,1,11,'2024-03-10',NULL,           0,'Isolement et antibiothérapie','4,6');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (6,1,30,'2024-07-05',NULL,           0,'Quarantaine + nettoyage profond','5');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (3,2,39,'2024-09-01',NULL,           0,'Abattage préventif, signalement autorités','4,5');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (4,1,46,'2024-10-10',NULL,           0,'Traitement antibiotique, contrôle eau','3,5');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (5,2,53,'2024-11-20',NULL,           0,'Vaccination urgente, quarantaine','4,6');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (6,1,60,'2025-01-15',NULL,           0,'Isolement fientes, analyse eau','5');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (1,3,NULL,'2023-09-10','2023-10-20',1,'Vaccination Gumboro + surveillance','2');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (2,4,NULL,'2023-11-05','2023-12-15',1,'Antibiothérapie ciblée','3');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (3,5,NULL,'2024-04-15','2024-05-10',1,'Antiparasitaire eau de boisson','4,5');
INSERT INTO dbo.historique_maladie (id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES (4,6,NULL,'2023-06-20','2023-07-30',1,'Vaccination Marek renforcée','5');

-- STAT LABORANTIN
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (1,1,87, 98.5,4.5);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (1,5,45, 97.0,2.0);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (2,2,64, 97.0,2.8);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (2,6,52, 98.0,3.5);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (3,3,73, 96.5,3.8);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (3,6,38, 97.5,4.0);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (4,1,112,99.0,4.2);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (4,7,61, 95.5,4.8);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (5,2,89, 96.0,2.5);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (5,4,44, 97.0,3.0);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (6,3,95, 98.0,3.6);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (6,6,57, 96.5,4.1);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (7,2,78, 94.0,2.9);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (7,5,33, 93.5,2.2);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (8,1,101,97.5,4.6);
INSERT INTO dbo.stat_laborantin (id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours) VALUES (8,4,66, 96.0,3.2);

COMMIT TRANSACTION;
GO

-- ============================================================
-- 4. VIEWS OPÉRATIONNELLES
-- ============================================================

CREATE VIEW dbo.vue_batiment_complet AS
SELECT b.id_batiment, b.nom_batiment,
       c.nom_centre, m.nom_marque, f.nom_filiale,
       c.gouvernorat, s.nom_souche, s.type_produit_final,
       s.fertilite_score, s.taux_mortalite, b.capacite
FROM dbo.batiment b
JOIN dbo.centre_elevage c ON b.id_centre = c.id_centre
JOIN dbo.marque m         ON c.id_marque = m.id_marque
JOIN dbo.filiale f        ON m.id_filiale = f.id_filiale
JOIN dbo.souche s         ON b.id_souche  = s.id_souche;
GO

CREATE VIEW dbo.vue_alertes_actives AS
SELECT d.num_analyse, d.statut, d.priorite,
       c.nom_centre, b.nom_batiment, t.libelle,
       d.raison_non_conformite, d.date_resultat
FROM dbo.demande_analyse d
JOIN dbo.centre_elevage c  ON d.id_centre       = c.id_centre
LEFT JOIN dbo.batiment b   ON d.id_batiment     = b.id_batiment
JOIN dbo.type_analyse t    ON d.id_type_analyse = t.id_type_analyse
WHERE d.statut IN ('Non conforme','Critique');
GO

CREATE VIEW dbo.vue_meilleur_laborantin AS
SELECT * FROM (
    SELECT t.libelle                   AS type_analyse,
           l.prenom + ' ' + l.nom      AS laborantin,
           lab.nom_labo,
           s.taux_conformite,
           s.duree_moy_jours,
           ROW_NUMBER() OVER (
               PARTITION BY t.id_type_analyse
               ORDER BY s.taux_conformite DESC, s.duree_moy_jours ASC
           ) rn
    FROM dbo.stat_laborantin s
    JOIN dbo.laborantin  l   ON s.id_laborantin   = l.id_laborantin
    JOIN dbo.laboratoire lab ON l.id_labo         = lab.id_labo
    JOIN dbo.type_analyse t  ON s.id_type_analyse = t.id_type_analyse
    WHERE l.disponible = 1
) sq WHERE rn = 1;
GO

CREATE VIEW dbo.vue_centres_risque AS
SELECT c.nom_centre,
       COUNT(*)               AS nb_alertes,
       MAX(d.date_resultat)   AS derniere_alerte
FROM dbo.demande_analyse d
JOIN dbo.centre_elevage c ON d.id_centre = c.id_centre
WHERE d.statut IN ('Non conforme','Critique')
GROUP BY c.nom_centre
HAVING COUNT(*) >= 1;
GO

CREATE VIEW dbo.vue_recommandation_laborantin AS
SELECT t.libelle,
       l.prenom + ' ' + l.nom AS laborantin,
       lab.nom_labo,
       s.taux_conformite,
       s.duree_moy_jours
FROM dbo.stat_laborantin s
JOIN dbo.laborantin  l   ON s.id_laborantin   = l.id_laborantin
JOIN dbo.laboratoire lab ON l.id_labo         = lab.id_labo
JOIN dbo.type_analyse t  ON s.id_type_analyse = t.id_type_analyse
WHERE l.disponible = 1
  AND s.taux_conformite > 97;
GO

CREATE VIEW dbo.vue_urgence_analyse AS
SELECT num_analyse, statut, priorite, date_decheance,
       DATEDIFF(DAY, date_prelevement, GETDATE()) AS jours_attente
FROM dbo.demande_analyse
WHERE statut IN ('En attente','En cours')
  AND priorite <= 2;
GO

CREATE VIEW dbo.vue_dashboard_ia AS
SELECT
    (SELECT COUNT(*) FROM dbo.demande_analyse)                               AS total_analyses,
    (SELECT COUNT(*) FROM dbo.demande_analyse WHERE statut = 'Critique')     AS critiques,
    (SELECT COUNT(*) FROM dbo.demande_analyse WHERE statut = 'Non conforme') AS non_conformes,
    (SELECT COUNT(*) FROM dbo.demande_analyse WHERE statut = 'En attente')   AS attente;
GO

CREATE VIEW dbo.vue_maladies_actives AS
SELECT m.nom_maladie, m.type_agent, m.est_critique,
       c.nom_centre, c.gouvernorat,
       hm.date_detection, hm.mesures_prises,
       hm.centres_contamines_potentiels
FROM dbo.historique_maladie hm
JOIN dbo.maladie       m  ON hm.id_maladie = m.id_maladie
JOIN dbo.centre_elevage c ON hm.id_centre = c.id_centre
WHERE hm.est_resolu = 0
ORDER BY m.est_critique DESC, hm.date_detection DESC;
GO

-- ============================================================
-- FIN - Base POULINA pour SQL Server
-- ============================================================

PRINT 'Base de données POULINA créée avec succès!'
GO

-- Tests rapides
SELECT COUNT(*) as total_centres FROM dbo.centre_elevage;
SELECT COUNT(*) as total_analyses FROM dbo.demande_analyse;
SELECT COUNT(*) as total_maladies FROM dbo.maladie;
GO