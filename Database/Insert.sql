-- ============================================================
-- CORRECTION INSERTS ORACLE
-- (tables en GENERATED ALWAYS AS IDENTITY)
-- => on supprime les colonnes ID auto
-- ============================================================


-------------------------------------------------
-- FILIALE (pas identity donc inchangé)
-------------------------------------------------
INSERT INTO filiale VALUES (1,'Poulina Avicole','Avicole');
INSERT INTO filiale VALUES (2,'Poulina Agro-Alimentaire','Agro-Alimentaire');


-------------------------------------------------
-- MARQUE
-------------------------------------------------
INSERT INTO marque (nom_marque,id_filiale) VALUES ('Dick',1);
INSERT INTO marque (nom_marque,id_filiale) VALUES ('SNA',1);
INSERT INTO marque (nom_marque,id_filiale) VALUES ('Gipa',2);
INSERT INTO marque (nom_marque,id_filiale) VALUES ('MedOil',2);


-------------------------------------------------
-- PAYS
-------------------------------------------------
INSERT INTO pays (nom_pays,code_iso) VALUES ('Tunisie','TUN');
INSERT INTO pays (nom_pays,code_iso) VALUES ('France','FRA');
INSERT INTO pays (nom_pays,code_iso) VALUES ('Belgique','BEL');
INSERT INTO pays (nom_pays,code_iso) VALUES ('Allemagne','DEU');
INSERT INTO pays (nom_pays,code_iso) VALUES ('Pays-Bas','NLD');
INSERT INTO pays (nom_pays,code_iso) VALUES ('Espagne','ESP');


-------------------------------------------------
-- SOUCHE
-------------------------------------------------
INSERT INTO souche
(nom_souche,type_produit_final,fertilite_score,taux_mortalite,resistance_maladies,cout_unitaire,id_pays_origine,notes)
VALUES
('Ross 308','Poulet',94.5,3.2,'Faible Salmonelle',2.800,5,'Croissance rapide');

INSERT INTO souche VALUES
(DEFAULT,'Cobb 500','Poulet',93.8,3.5,'Moyenne',2.650,5,'Bonne conversion');

INSERT INTO souche VALUES
(DEFAULT,'Hubbard Flex','Poulet',92.1,4.1,'Bonne',2.500,2,'Climat chaud');

INSERT INTO souche VALUES
(DEFAULT,'Lohmann Brown','Oeuf',96,1.8,'Très résistante',3.100,3,'Haute performance');


-------------------------------------------------
-- CENTRE ELEVAGE
-------------------------------------------------
INSERT INTO centre_elevage
(nom_centre,localisation,gouvernorat,id_marque,type_production,capacite_totale,date_creation,actif)
VALUES
('Centre Dick Nord','Route Mateur','Bizerte',1,'Poulet',80000,DATE '2010-03-15',1);

INSERT INTO centre_elevage
(nom_centre,localisation,gouvernorat,id_marque,type_production,capacite_totale,date_creation,actif)
VALUES
('Centre Dick Sud','Zone Industrielle','Sfax',1,'Poulet',60000,DATE '2012-07-01',1);

INSERT INTO centre_elevage
(nom_centre,localisation,gouvernorat,id_marque,type_production,capacite_totale,date_creation,actif)
VALUES
('Centre SNA Tunis','Ariana','Ariana',2,'Dinde',30000,DATE '2008-09-10',1);


-------------------------------------------------
-- BATIMENT
-------------------------------------------------
INSERT INTO batiment
(nom_batiment,id_centre,id_souche,capacite,date_mise_en_service,actif)
VALUES
('Batiment A1',1,1,15000,DATE '2010-03-15',1);

INSERT INTO batiment
(nom_batiment,id_centre,id_souche,capacite,date_mise_en_service,actif)
VALUES
('Batiment A2',1,2,15000,DATE '2011-06-01',1);

INSERT INTO batiment
(nom_batiment,id_centre,id_souche,capacite,date_mise_en_service,actif)
VALUES
('Batiment D1',3,1,12000,DATE '2008-09-10',1);


-------------------------------------------------
-- LABORATOIRE
-------------------------------------------------
INSERT INTO laboratoire
(nom_labo,adresse,gouvernorat,latitude,longitude,telephone,email,specialites,actif)
VALUES
('Labo Central Tunis','Tunis','Tunis',36.81,10.17,'+216111','labo1@tn','PCR,Virologie',1);

INSERT INTO laboratoire
(nom_labo,adresse,gouvernorat,latitude,longitude,telephone,email,specialites,actif)
VALUES
('Pasteur Tunis','Tunis','Tunis',36.82,10.18,'+216222','labo2@tn','Influenza',1);


-------------------------------------------------
-- LABORANTIN
-------------------------------------------------
INSERT INTO laborantin
(prenom,nom,id_labo,specialite,annees_experience,disponible,email,telephone)
VALUES
('Sami','Bouaziz',1,'Salmonelle',12,1,'sami@tn','221');

INSERT INTO laborantin
(prenom,nom,id_labo,specialite,annees_experience,disponible,email,telephone)
VALUES
('Nadia','Trabelsi',1,'PCR',8,1,'nadia@tn','222');


-------------------------------------------------
-- TYPE ANALYSE
-------------------------------------------------
INSERT INTO type_analyse
(code_analyse,libelle,description,duree_jours,type_echantillon)
VALUES
('BACTE-SAL','Bactériologie Salmonelle','Analyse Salmonelle',5,'Fiente');

INSERT INTO type_analyse
(code_analyse,libelle,description,duree_jours,type_echantillon)
VALUES
('PCR-ND','PCR Newcastle','Détection ND',3,'Frottis');


-------------------------------------------------
-- DEMANDE ANALYSE
-------------------------------------------------
INSERT INTO demande_analyse
(num_analyse,id_centre,id_batiment,id_type_analyse,id_labo,id_laborantin,id_pays_provenance,
type_echantillon,date_prelevement,date_decheance,date_analyse,date_resultat,
statut,priorite,est_conforme,raison_non_conformite,
resultat_souche_detectee,pourcentage_securite,niveau_satisfaction,observations)
VALUES
('ANA-001',1,1,1,1,1,1,
'Fiente',DATE '2024-01-10',DATE '2024-01-17',DATE '2024-01-12',DATE '2024-01-14',
'Terminée',1,1,NULL,
'Ross 308',98,5,NULL);


-------------------------------------------------
-- HISTORIQUE MALADIE
-------------------------------------------------
INSERT INTO historique_maladie
(id_centre,id_maladie,id_demande,date_detection,date_resolution,est_resolu,mesures_prises,centres_contamines_potentiels)
VALUES
(1,1,1,DATE '2024-06-10',NULL,0,'Quarantaine','2,3');


-------------------------------------------------
-- STAT LABORANTIN
-------------------------------------------------
INSERT INTO stat_laborantin
(id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours)
VALUES
(1,1,87,98.5,4.5);

INSERT INTO stat_laborantin
(id_laborantin,id_type_analyse,nb_analyses_effectuees,taux_conformite,duree_moy_jours)
VALUES
(2,2,64,97,2.8);


COMMIT;

-- ============================================================
-- VIEWS STANDARDES
-- ============================================================

CREATE OR REPLACE VIEW vue_batiment_complet AS
SELECT
b.id_batiment,
b.nom_batiment,
c.nom_centre,
m.nom_marque,
f.nom_filiale,
c.gouvernorat,
s.nom_souche,
s.type_produit_final,
s.fertilite_score,
s.taux_mortalite,
b.capacite
FROM batiment b
JOIN centre_elevage c ON b.id_centre=c.id_centre
JOIN marque m ON c.id_marque=m.id_marque
JOIN filiale f ON m.id_filiale=f.id_filiale
JOIN souche s ON b.id_souche=s.id_souche;


CREATE OR REPLACE VIEW vue_alertes_actives AS
SELECT
d.num_analyse,
d.statut,
d.priorite,
c.nom_centre,
b.nom_batiment,
t.libelle,
d.raison_non_conformite,
d.date_resultat
FROM demande_analyse d
JOIN centre_elevage c ON d.id_centre=c.id_centre
LEFT JOIN batiment b ON d.id_batiment=b.id_batiment
JOIN type_analyse t ON d.id_type_analyse=t.id_type_analyse
WHERE d.statut IN ('Non conforme','Critique');


CREATE OR REPLACE VIEW vue_meilleur_laborantin AS
SELECT *
FROM (
SELECT
t.libelle type_analyse,
l.prenom||' '||l.nom laborantin,
lab.nom_labo,
s.taux_conformite,
s.duree_moy_jours,
ROW_NUMBER() OVER(PARTITION BY t.id_type_analyse ORDER BY s.taux_conformite DESC,s.duree_moy_jours ASC) rn
FROM stat_laborantin s
JOIN laborantin l ON s.id_laborantin=l.id_laborantin
JOIN laboratoire lab ON l.id_labo=lab.id_labo
JOIN type_analyse t ON s.id_type_analyse=t.id_type_analyse
WHERE l.disponible=1
)
WHERE rn=1;


-- ============================================================
-- VIEWS IA CHATBOT (VERSION C)
-- ============================================================

---------------------------------------------------------------
-- Centres à risque
---------------------------------------------------------------
CREATE OR REPLACE VIEW vue_centres_risque AS
SELECT
c.nom_centre,
COUNT(*) nb_alertes,
MAX(d.date_resultat) derniere_alerte
FROM demande_analyse d
JOIN centre_elevage c ON d.id_centre=c.id_centre
WHERE d.statut IN ('Non conforme','Critique')
GROUP BY c.nom_centre
HAVING COUNT(*) >=1;

---------------------------------------------------------------
-- Laborantin recommandé automatique
---------------------------------------------------------------
CREATE OR REPLACE VIEW vue_recommandation_laborantin AS
SELECT
t.libelle,
l.prenom||' '||l.nom laborantin,
lab.nom_labo,
s.taux_conformite,
s.duree_moy_jours
FROM stat_laborantin s
JOIN laborantin l ON s.id_laborantin=l.id_laborantin
JOIN laboratoire lab ON l.id_labo=lab.id_labo
JOIN type_analyse t ON s.id_type_analyse=t.id_type_analyse
WHERE l.disponible=1
AND s.taux_conformite > 97;

---------------------------------------------------------------
-- Analyse urgente à traiter
---------------------------------------------------------------
CREATE OR REPLACE VIEW vue_urgence_analyse AS
SELECT
num_analyse,
statut,
priorite,
date_decheance,
SYSDATE - date_prelevement jours_attente
FROM demande_analyse
WHERE statut IN ('En attente','En cours')
AND priorite <=2;

---------------------------------------------------------------
-- Dashboard global IA
---------------------------------------------------------------
CREATE OR REPLACE VIEW vue_dashboard_ia AS
SELECT
(SELECT COUNT(*) FROM demande_analyse) total_analyses,
(SELECT COUNT(*) FROM demande_analyse WHERE statut='Critique') critiques,
(SELECT COUNT(*) FROM demande_analyse WHERE statut='Non conforme') non_conformes,
(SELECT COUNT(*) FROM demande_analyse WHERE statut='En attente') attente
FROM dual;

-- ============================================================
-- FIN
-- ============================================================