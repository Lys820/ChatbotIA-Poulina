#!/usr/bin/env python
"""
DEBUG : Teste juste le ML model sans passer par l'API.
"""
import pandas as pd
import sys

# Crée les CSV de test
analyses_data = {
    "id_centre": [1, 2, 3, 4, 5],
    "ville": ["Tunis", "Sfax", "Sfax", "Sousse", "Tunis"],
    "region": ["Tunisie", "Sfax", "Sfax", "Sousse", "Tunisie"],
    "type_production": ["Poulet de chair", "Œuf", "Poulet de chair", "Dinde", "Œuf"],
    "meilleure_souche": ["Cobb 500", "Lohmann", "Ross 708", "BUT Big6", "Lohmann"],
    "biosecurite_score": [8.5, 7.2, 9.0, 6.8, 8.0],
    "taux_mortalite": [2.1, 1.8, 2.5, 3.2, 1.5],
    "fertilite_visee": [92, 88, 90, 85, 90],
    "conforme": [1, 1, 0, 1, 1],
    "historique_maladie": ["Coccidiose", "Salmonelle", "Newcastle", "Mycoplasme", "Rien"],
    "temperature_moyenne": [28, 30, 29, 27, 28],
    "humidite": [55, 50, 52, 60, 58],
    "capacite": [5000, 3000, 8000, 2500, 4000],
    "surface_m2": [500, 300, 800, 250, 400],
    "experience_equipe": [5, 3, 8, 2, 6],
    "distance_labo": [15, 8, 10, 20, 12],
    "budget": [50000, 30000, 80000, 25000, 45000],
    "saison": ["Été", "Printemps", "Été", "Hiver", "Automne"],
    "demande_marche": ["Élevé", "Moyen", "Élevé", "Bas", "Moyen"],
    "cout_aliment": [5.2, 4.8, 5.5, 6.0, 5.0],
}
df_analyses = pd.DataFrame(analyses_data)

labos_data = {
    "id_labo": [101, 102, 103, 104, 105],
    "nom_laboratoire": ["Lab Tunis Central", "Lab Sfax Elite", "Lab Sousse Pro", "Lab Ariana Tech", "Lab Sfax Plus"],
    "type_laboratoire": ["Privé agréé", "Privé", "Public", "Privé agréé", "Privé"],
    "ville": ["Tunis", "Sfax", "Sousse", "Ariana", "Sfax"],
    "region": ["Tunis", "Sfax", "Sousse", "Tunis", "Sfax"],
    "specialites_principales": ["Virologie, Immunologie", "Bactériologie, PCR", "Virologie", "Sérologie, PCR", "Bactériologie"],
    "maladies_avicoles_traitees": ["Newcastle, Gumboro", "Salmonelle, E.coli", "Newcastle", "Salmonelle, Newcastle", "Salmonelle, Mycoplasme"],
    "taux_reussite_pct": [98, 95, 92, 97, 93],
    "note_satisfaction": [4.8, 4.5, 4.2, 4.7, 4.3],
    "cout_analyse_moyen_tnd": [150, 120, 100, 160, 110],
    "cout_urgence_tnd": [300, 250, 200, 320, 220],
    "delai_standard_jours": [3, 2, 4, 3, 2],
    "delai_urgence_heures": [12, 8, 24, 10, 12],
    "accepte_urgence": [1, 1, 0, 1, 1],
    "certifie_iso": [1, 0, 0, 1, 0],
    "equipement_pcr": [1, 1, 0, 1, 1],
    "equipement_elisa": [1, 1, 1, 1, 1],
    "equipement_sequencage": [1, 0, 0, 1, 0],
    "score_global": [9.2, 8.5, 7.8, 9.0, 8.2],
    "capacite_journaliere_analyses": [20, 15, 10, 18, 12],
    "charge_actuelle_pct": [60, 75, 45, 55, 70],
    "slots_disponibles_semaine": [8, 5, 12, 10, 6],
    "delai_prochain_rdv_jours": [1, 2, 5, 1, 3],
    "annees_experience_labo": [12, 8, 5, 10, 7],
    "nb_analyses_avicoles": [2000, 1500, 800, 1800, 1200],
    "distance_moyenne_centres_km": [5, 2, 15, 8, 3],
    "actif": [1, 1, 1, 1, 1],
    "tier_labo": ["Excellent", "Bon", "Passable", "Excellent", "Bon"],
}
df_labos = pd.DataFrame(labos_data)

print("\n" + "=" * 70)
print("1. Données chargées")
print("=" * 70)
print(f"✓ Analyses : {len(df_analyses)} lignes")
print(f"✓ Labos : {len(df_labos)} lignes")
print(f"\nColonnes analyses : {list(df_analyses.columns)}")
print(f"Souches uniques : {df_analyses['meilleure_souche'].unique()}")
print(f"Tiers labos uniques : {df_labos['tier_labo'].unique()}")

# Import du model factory
sys.path.insert(0, '.')
from app.ml.model_factory import create_model, SOUCHE_NUM_FEATURES, SOUCHE_CAT_FEATURES, SOUCHE_TARGET

print("\n" + "=" * 70)
print("2. Création du modèle")
print("=" * 70)

model = create_model("random_forest", SOUCHE_NUM_FEATURES, SOUCHE_CAT_FEATURES)
print(f"✓ Modèle créé : {model.name}")

print("\n" + "=" * 70)
print("3. Entraînement")
print("=" * 70)

y_souche = df_analyses[SOUCHE_TARGET].dropna()
X_souche = df_analyses.loc[y_souche.index]
print(f"Samples pour entraînement : {len(y_souche)}")
print(f"Features disponibles : {len(SOUCHE_NUM_FEATURES)} num + {len(SOUCHE_CAT_FEATURES)} cat")

acc = model.fit(X_souche, y_souche)
print(f"✓ Accuracy : {acc:.3f}")
print(f"✓ Classes trouvées : {model._classes}")

print("\n" + "=" * 70)
print("4. Prédiction test")
print("=" * 70)

test_input = pd.DataFrame([{
    "type_production": "Poulet de chair",
    "biosecurite_score": 9.0,
    "taux_mortalite": 1.8,
    "temperature_moyenne": 28,
    "humidite": 55,
    "fertilite_visee": 90,
    "capacite": 7000,
    "surface_m2": 700,
    "experience_equipe": 8,
    "distance_labo": 10,
    "budget": 70000,
    "saison": "Été",
    "demande_marche": "Élevé",
    "cout_aliment": 5.5,
}])

try:
    label, conf, alts = model.predict_proba(test_input)
    print(f"✓ Prédiction : {label} ({conf*100:.1f}%)")
    print(f"  Alternatives : {alts}")
except Exception as e:
    print(f"❌ Erreur prédiction : {e}")
    import traceback
    traceback.print_exc()

print("\n✅ DEBUG TERMINÉ")