#!/usr/bin/env python
"""
SEED ORACLE POULINA – Truncate complet + insert données réalistes
Basé sur le schéma Tables.sql (GENERATED ALWAYS AS IDENTITY)
"""
import oracledb
import random
from datetime import date, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

conn = oracledb.connect(
    user=os.getenv("ORACLE_USER"),
    password=os.getenv("ORACLE_PASSWORD"),
    dsn=os.getenv("ORACLE_DSN")
)
cur = conn.cursor()

# ══════════════════════════════════════════════════════════════════════════════
# 0. TRUNCATE (ordre inverse des FK)
# ══════════════════════════════════════════════════════════════════════════════
print("🗑️  Truncate des tables...")

tables_to_truncate = [
    "stat_laborantin",
    "historique_maladie",
    "demande_analyse",
    "batiment",
    "laborantin",
    "laboratoire",
    "centre_elevage",
    "type_analyse",
    "souche",
    "maladie",
    "marque",
    "pays",
    "filiale",
]

for t in tables_to_truncate:
    try:
        cur.execute(f"DELETE FROM {t}")
        print(f"  ✓ {t} vidée")
    except Exception as e:
        print(f"  ⚠️  {t}: {e}")

conn.commit()

# ══════════════════════════════════════════════════════════════════════════════
# 1. FILIALE (pas d'identity)
# ══════════════════════════════════════════════════════════════════════════════
cur.execute("INSERT INTO filiale VALUES (1,'Poulina Avicole','Avicole')")
cur.execute("INSERT INTO filiale VALUES (2,'Poulina Agro-Alimentaire','Agro-Alimentaire')")
print("✓ filiale")

# ══════════════════════════════════════════════════════════════════════════════
# 2. PAYS
# ══════════════════════════════════════════════════════════════════════════════
pays_data = [
    ('Tunisie', 'TUN'), ('France', 'FRA'), ('Belgique', 'BEL'),
    ('Allemagne', 'DEU'), ('Pays-Bas', 'NLD'), ('Espagne', 'ESP'),
]
cur.executemany("INSERT INTO pays (nom_pays, code_iso) VALUES (:1,:2)", pays_data)
print(f"✓ pays ({len(pays_data)})")

# Récupère IDs pays générés
cur.execute("SELECT id_pays, nom_pays FROM pays ORDER BY id_pays")
pays_map = {nom: pid for pid, nom in cur.fetchall()}

# ══════════════════════════════════════════════════════════════════════════════
# 3. MARQUE
# ══════════════════════════════════════════════════════════════════════════════
cur.executemany(
    "INSERT INTO marque (nom_marque, id_filiale) VALUES (:1,:2)",
    [('Dick', 1), ('SNA', 1), ('Gipa', 2), ('MedOil', 2)]
)
cur.execute("SELECT id_marque, nom_marque FROM marque ORDER BY id_marque")
marque_map = {nom: mid for mid, nom in cur.fetchall()}
print("✓ marque")

# ══════════════════════════════════════════════════════════════════════════════
# 4. SOUCHE
# ══════════════════════════════════════════════════════════════════════════════
souches_data = [
    ('Ross 308',      'Poulet', 94.5, 3.2, 'Faible Salmonelle',   2.800, pays_map['Pays-Bas'],  'Croissance rapide, conversion élevée'),
    ('Cobb 500',      'Poulet', 93.8, 3.5, 'Moyenne',             2.650, pays_map['Pays-Bas'],  'Bonne conversion alimentaire'),
    ('Hubbard Flex',  'Poulet', 92.1, 4.1, 'Bonne',               2.500, pays_map['France'],    'Adaptée aux climats chauds'),
    ('Lohmann Brown', 'Oeuf',   96.0, 1.8, 'Très résistante',     3.100, pays_map['Belgique'],  'Haute ponte, résistance maladies'),
    ('Ross 708',      'Poulet', 95.2, 2.9, 'Bonne',               2.950, pays_map['Pays-Bas'],  'Performance maximale, standard export'),
    ('BUT Big 6',     'Dinde',  88.0, 5.1, 'Faible',              4.200, pays_map['France'],    'Dinde commerciale lourde'),
    ('Hybro G+',      'Poulet', 93.0, 3.8, 'Moyenne',             2.700, pays_map['Allemagne'], 'Polyvalente, adaptable'),
]
cur.executemany("""
    INSERT INTO souche (nom_souche, type_produit_final, fertilite_score, taux_mortalite,
        resistance_maladies, cout_unitaire, id_pays_origine, notes)
    VALUES (:1,:2,:3,:4,:5,:6,:7,:8)
""", souches_data)

cur.execute("SELECT id_souche, nom_souche FROM souche ORDER BY id_souche")
souche_map = {nom: sid for sid, nom in cur.fetchall()}
souche_ids = list(souche_map.values())
print(f"✓ souche ({len(souches_data)})")

# ══════════════════════════════════════════════════════════════════════════════
# 5. MALADIE
# ══════════════════════════════════════════════════════════════════════════════
maladies_data = [
    ('Salmonelle',    'Bactérie',  45.0, 8.0,  25.0, 1, 'Zoonose majeure, transmission fèces-eau'),
    ('Newcastle',     'Virus',     80.0, 60.0, 40.0, 1, 'Maladie de Newcastle, pandémique'),
    ('Gumboro',       'Virus',     55.0, 20.0, 15.0, 0, 'Immunodépresseur, touche poussins'),
    ('Mycoplasme',    'Bactérie',  35.0, 5.0,  20.0, 0, 'Maladie chronique respiratoire'),
    ('Coccidiose',    'Parasite',  40.0, 10.0, 30.0, 0, 'Parasite intestinal fréquent'),
    ('Marek',         'Virus',     70.0, 25.0, 10.0, 0, 'Herpesvirus, lymphomes'),
    ('Bronchite infectieuse', 'Virus', 60.0, 15.0, 35.0, 0, 'IB, tropisme respiratoire et rénal'),
]
cur.executemany("""
    INSERT INTO maladie (nom_maladie, type_agent, taux_transmission, taux_mortalite,
        impact_fertilite, est_critique, description)
    VALUES (:1,:2,:3,:4,:5,:6,:7)
""", maladies_data)

cur.execute("SELECT id_maladie, nom_maladie FROM maladie ORDER BY id_maladie")
maladie_map = {nom: mid for mid, nom in cur.fetchall()}
maladie_ids = list(maladie_map.values())
print(f"✓ maladie ({len(maladies_data)})")

# ══════════════════════════════════════════════════════════════════════════════
# 6. CENTRE ELEVAGE
# ══════════════════════════════════════════════════════════════════════════════
centres_data = [
    ('Centre Dick Nord',    'Route Mateur, km 12',      'Bizerte',   marque_map['Dick'], 'Poulet', 80000,  date(2010,3,15)),
    ('Centre Dick Sud',     'Zone Industrielle Sfax',   'Sfax',      marque_map['Dick'], 'Poulet', 60000,  date(2012,7,1)),
    ('Centre SNA Tunis',    'Ariana, Zone Nord',        'Ariana',    marque_map['SNA'],  'Dinde',  30000,  date(2008,9,10)),
    ('Centre Dick Est',     'Nabeul Route Côtière',     'Nabeul',    marque_map['Dick'], 'Poulet', 50000,  date(2015,4,20)),
    ('Centre SNA Sousse',   'Zone Industrielle Sousse', 'Sousse',    marque_map['SNA'],  'Oeuf',   40000,  date(2017,1,5)),
    ('Centre Dick Centre',  'Kairouan Route Nationale', 'Kairouan',  marque_map['Dick'], 'Poulet', 70000,  date(2013,6,12)),
]
cur.executemany("""
    INSERT INTO centre_elevage (nom_centre, localisation, gouvernorat, id_marque,
        type_production, capacite_totale, date_creation, actif)
    VALUES (:1,:2,:3,:4,:5,:6,:7,1)
""", centres_data)

cur.execute("SELECT id_centre FROM centre_elevage ORDER BY id_centre")
centre_ids = [r[0] for r in cur.fetchall()]
print(f"✓ centre_elevage ({len(centres_data)})")

# ══════════════════════════════════════════════════════════════════════════════
# 7. BATIMENT
# ══════════════════════════════════════════════════════════════════════════════
batiments_data = []
for i, cid in enumerate(centre_ids):
    # 2 bâtiments par centre
    for j in range(1, 3):
        s_id = souche_ids[(i * 2 + j) % len(souche_ids)]
        batiments_data.append((
            f'Batiment {chr(65+i)}{j}',
            cid, s_id,
            random.randint(10000, 20000),
            date(2010, 1, 1) + timedelta(days=i*365 + j*180)
        ))

cur.executemany("""
    INSERT INTO batiment (nom_batiment, id_centre, id_souche, capacite, date_mise_en_service, actif)
    VALUES (:1,:2,:3,:4,:5,1)
""", batiments_data)

cur.execute("SELECT id_batiment, id_centre FROM batiment ORDER BY id_batiment")
batiments = cur.fetchall()
bat_ids = [r[0] for r in batiments]
bat_by_centre = {}
for bid, cid in batiments:
    bat_by_centre.setdefault(cid, []).append(bid)
print(f"✓ batiment ({len(batiments_data)})")

# ══════════════════════════════════════════════════════════════════════════════
# 8. LABORATOIRE
# ══════════════════════════════════════════════════════════════════════════════
labos_data = [
    ('Labo Central Tunis', 'Rue de la Liberté, Tunis',   'Tunis',   36.8190, 10.1663, '+21671123456', 'central@labo.tn',   'PCR, Virologie, Bactériologie, ELISA'),
    ('Pasteur Tunis',      'Avenue Pasteur, Tunis',       'Tunis',   36.8185, 10.1702, '+21671987654', 'pasteur@labo.tn',   'Virologie, Immunologie, Influenza'),
    ('Labo Sfax Avicole',  'Zone Industrielle, Sfax',     'Sfax',    34.7400, 10.7600, '+21674111222', 'sfax@labo.tn',      'Bactériologie, PCR, Salmonelle'),
    ('Labo Sousse Bio',    'Avenue Mohammed V, Sousse',   'Sousse',  35.8333, 10.6378, '+21673333444', 'sousse@labo.tn',    'ELISA, Sérologie, PCR'),
    ('InstitutVet Bizerte','Route Mateur, Bizerte',       'Bizerte', 37.2744, 9.8739,  '+21672555666', 'bizerte@labo.tn',   'PCR, Bactériologie, Parasitologie'),
]
cur.executemany("""
    INSERT INTO laboratoire (nom_labo, adresse, gouvernorat, latitude, longitude,
        telephone, email, specialites, actif)
    VALUES (:1,:2,:3,:4,:5,:6,:7,:8,1)
""", labos_data)

cur.execute("SELECT id_labo FROM laboratoire ORDER BY id_labo")
labo_ids = [r[0] for r in cur.fetchall()]
print(f"✓ laboratoire ({len(labos_data)})")

# ══════════════════════════════════════════════════════════════════════════════
# 9. LABORANTIN
# ══════════════════════════════════════════════════════════════════════════════
laborantins_data = [
    ('Sami',    'Bouaziz',   labo_ids[0], 'Salmonelle, Bactériologie', 12, 1, 'sami.bouaziz@labo.tn',    '+216221001'),
    ('Nadia',   'Trabelsi',  labo_ids[0], 'PCR, Virologie',             8, 1, 'nadia.trabelsi@labo.tn',  '+216221002'),
    ('Karim',   'Ben Ali',   labo_ids[1], 'Immunologie, ELISA',         6, 1, 'karim.benali@labo.tn',    '+216221003'),
    ('Fatma',   'Mansouri',  labo_ids[2], 'Bactériologie, Salmonelle', 10, 1, 'fatma.mansouri@labo.tn',  '+216221004'),
    ('Youssef', 'Dridi',     labo_ids[2], 'PCR, Newcastle',              5, 1, 'youssef.dridi@labo.tn',  '+216221005'),
    ('Amira',   'Khelifi',   labo_ids[3], 'Sérologie, ELISA',            7, 1, 'amira.khelifi@labo.tn',  '+216221006'),
    ('Bilel',   'Gharbi',    labo_ids[4], 'PCR, Parasitologie',          9, 0, 'bilel.gharbi@labo.tn',   '+216221007'),
    ('Rania',   'Chabbi',    labo_ids[4], 'Bactériologie, PCR',          4, 1, 'rania.chabbi@labo.tn',   '+216221008'),
]
cur.executemany("""
    INSERT INTO laborantin (prenom, nom, id_labo, specialite, annees_experience, disponible, email, telephone)
    VALUES (:1,:2,:3,:4,:5,:6,:7,:8)
""", laborantins_data)

cur.execute("SELECT id_laborantin, id_labo FROM laborantin ORDER BY id_laborantin")
laborantins = cur.fetchall()
lab_ids_all = [r[0] for r in laborantins]
lab_by_labo = {}
for lid, laboid in laborantins:
    lab_by_labo.setdefault(laboid, []).append(lid)
print(f"✓ laborantin ({len(laborantins_data)})")

# ══════════════════════════════════════════════════════════════════════════════
# 10. TYPE ANALYSE
# ══════════════════════════════════════════════════════════════════════════════
types_data = [
    ('BACTE-SAL', 'Bactériologie Salmonelle',  'Recherche et identification Salmonella spp.',   5, 'Fiente'),
    ('PCR-ND',    'PCR Newcastle',              'Détection virus Newcastle par PCR temps réel',  3, 'Frottis trachéal'),
    ('ELISA-IBD', 'Sérologie Gumboro ELISA',   'Titrage anticorps anti-IBD',                    4, 'Sang'),
    ('PCR-MG',    'PCR Mycoplasme',             'Détection Mycoplasma gallisepticum',             3, 'Écouvillon trachéal'),
    ('PARASIT',   'Parasitologie Coccidiose',   'Examen coprologique + identification oocystes', 2, 'Fientes fraiches'),
    ('SERO-ND',   'Sérologie Newcastle HI',     'Inhibition hémagglutination ND',               4, 'Sang'),
    ('BACTE-COL', 'Bactériologie E.coli',       'Antibiogramme E.coli pathogènes',              5, 'Organes'),
]
cur.executemany("""
    INSERT INTO type_analyse (code_analyse, libelle, description, duree_jours, type_echantillon)
    VALUES (:1,:2,:3,:4,:5)
""", types_data)

cur.execute("SELECT id_type_analyse FROM type_analyse ORDER BY id_type_analyse")
type_ids = [r[0] for r in cur.fetchall()]
print(f"✓ type_analyse ({len(types_data)})")

# ══════════════════════════════════════════════════════════════════════════════
# 11. DEMANDE ANALYSE (60 analyses réalistes)
# ══════════════════════════════════════════════════════════════════════════════
souches_noms = list(souche_map.keys())
echantillons = ['Fiente', 'Sang', 'Écouvillon trachéal', 'Organes', 'Frottis trachéal', 'Fientes fraiches']
statuts_conformes = ['Terminée', 'Terminée', 'Terminée']
statuts_non_conformes = ['Non conforme', 'Critique']
raisons_nc = [
    'Salmonelle détectée au-delà du seuil réglementaire',
    'Virus Newcastle identifié, abattage préventif requis',
    'Souche détectée ne correspond pas au bâtiment déclaré',
    'Prélèvement non conforme : délai de conservation dépassé',
    'Résultat inférieur au seuil de sécurité (< 85%)',
]

pays_provenance = list(pays_map.values())
analyses_rows = []

random.seed(42)
for i in range(2, 62):  # 60 analyses (ANA-001 déjà dans Insert.sql)
    cid = random.choice(centre_ids)
    bats = bat_by_centre.get(cid, bat_ids[:1])
    bid = random.choice(bats)
    tid = random.choice(type_ids)
    lid = random.choice(labo_ids)
    lant_ids = lab_by_labo.get(lid, lab_ids_all[:1])
    lantid = random.choice(lant_ids)

    d_prel = date(2023, 6, 1) + timedelta(days=random.randint(0, 550))
    d_dec  = d_prel + timedelta(days=random.randint(5, 10))
    d_ana  = d_prel + timedelta(days=random.randint(1, 4))
    d_res  = d_ana  + timedelta(days=random.randint(1, 3))

    # 70% conformes
    is_conforme = 1 if random.random() < 0.70 else 0
    if is_conforme:
        statut  = random.choice(statuts_conformes)
        raison  = None
        pct_sec = round(random.uniform(87, 99), 1)
    else:
        statut  = random.choice(statuts_non_conformes)
        raison  = random.choice(raisons_nc)
        pct_sec = round(random.uniform(50, 84), 1)

    analyses_rows.append((
        f'ANA-{i:03d}',
        cid, bid, tid, lid, lantid,
        random.choice(pays_provenance),
        random.choice(echantillons),
        d_prel, d_dec, d_ana, d_res,
        statut,
        random.randint(1, 5),
        is_conforme, raison,
        random.choice(souches_noms),
        pct_sec,
        random.randint(1, 5),
        None  # observations
    ))

cur.executemany("""
    INSERT INTO demande_analyse (
        num_analyse, id_centre, id_batiment, id_type_analyse,
        id_labo, id_laborantin, id_pays_provenance,
        type_echantillon, date_prelevement, date_decheance,
        date_analyse, date_resultat,
        statut, priorite, est_conforme, raison_non_conformite,
        resultat_souche_detectee, pourcentage_securite,
        niveau_satisfaction, observations
    ) VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20)
""", analyses_rows)

# Récupère tous les IDs demandes (y compris ANA-001)
cur.execute("SELECT id_demande FROM demande_analyse ORDER BY id_demande")
demande_ids = [r[0] for r in cur.fetchall()]
print(f"✓ demande_analyse ({len(analyses_rows) + 1})")

# ══════════════════════════════════════════════════════════════════════════════
# 12. HISTORIQUE MALADIE (20 événements)
# ══════════════════════════════════════════════════════════════════════════════
mesures = [
    'Quarantaine + traitement antibiotique',
    'Abattage préventif et désinfection totale',
    'Vaccination de rappel, surveillance renforcée',
    'Isolation des sujets malades, antiparasitaire',
    'Nettoyage et désinfection profonde du bâtiment',
]
historiques = []
for i in range(20):
    cid = random.choice(centre_ids)
    mid = random.choice(maladie_ids)
    did = random.choice(demande_ids) if random.random() > 0.3 else None
    d_det = date(2023, 1, 1) + timedelta(days=random.randint(0, 700))
    est_resolu = random.choice([0, 0, 1])
    d_res = d_det + timedelta(days=random.randint(10, 60)) if est_resolu else None
    # centres potentiellement contaminés (IDs voisins)
    contamines = ','.join(str(x) for x in random.sample(centre_ids, k=random.randint(1, 2)) if x != cid)
    historiques.append((
        cid, mid, did,
        d_det, d_res, est_resolu,
        random.choice(mesures),
        contamines or None
    ))

cur.executemany("""
    INSERT INTO historique_maladie (
        id_centre, id_maladie, id_demande,
        date_detection, date_resolution, est_resolu,
        mesures_prises, centres_contamines_potentiels
    ) VALUES (:1,:2,:3,:4,:5,:6,:7,:8)
""", historiques)
print(f"✓ historique_maladie ({len(historiques)})")

# ══════════════════════════════════════════════════════════════════════════════
# 13. STAT LABORANTIN
# ══════════════════════════════════════════════════════════════════════════════
stats = []
for lid in lab_ids_all:
    nb_types = random.randint(1, 3)
    chosen_types = random.sample(type_ids, k=min(nb_types, len(type_ids)))
    for tid in chosen_types:
        stats.append((
            lid, tid,
            random.randint(20, 200),
            round(random.uniform(90, 99.5), 1),
            round(random.uniform(1.5, 6.0), 1),
        ))

cur.executemany("""
    INSERT INTO stat_laborantin (id_laborantin, id_type_analyse,
        nb_analyses_effectuees, taux_conformite, duree_moy_jours)
    VALUES (:1,:2,:3,:4,:5)
""", stats)
print(f"✓ stat_laborantin ({len(stats)})")

# ══════════════════════════════════════════════════════════════════════════════
# COMMIT
# ══════════════════════════════════════════════════════════════════════════════
conn.commit()
cur.close()
conn.close()

print("""
════════════════════════════════════════════════════════
✅ Seed terminé avec succès !

Résumé :
  - 6 centres d'élevage (Bizerte, Sfax, Ariana, Nabeul, Sousse, Kairouan)
  - 7 souches (Ross 308, Cobb 500, Hubbard Flex, Lohmann Brown…)
  - 7 maladies (Salmonelle + Newcastle critiques)
  - 5 laboratoires (Tunis, Sfax, Sousse, Bizerte)
  - 8 laborantins
  - 7 types d'analyse
  - 61 demandes d'analyse (70% conformes)
  - 20 historiques de maladies

Prochaine étape :
  POST http://localhost:8000/api/v1/analyses/train-from-oracle
════════════════════════════════════════════════════════
""")