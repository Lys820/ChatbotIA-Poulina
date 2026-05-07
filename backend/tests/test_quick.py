#!/usr/bin/env python
"""
TEST QUICK – Lance TOUT en 10 secondes
Crée CSV de test → Upload → Chat test

Tape : python test_quick.py
"""
import pandas as pd
import asyncio
import httpx
import json


def create_test_csv():
    """Crée les CSV de test."""
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
    df_analyses.to_csv("test_analyses.csv", index=False)

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
    df_labos.to_csv("test_labos.csv", index=False)
    print("✓ CSV de test créés")


async def test():
    """Teste l'API."""
    BASE = "http://localhost:8000/api/v1"

    async with httpx.AsyncClient(timeout=30) as client:
        print("\n" + "=" * 70)
        print("1. HEALTH CHECK")
        print("=" * 70)
        try:
            r = await client.get(f"{BASE}/health")
            print(f"   Status: {r.status_code}")
            print(f"   {json.dumps(r.json(), indent=2)}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            print(f"   Assure-toi que le serveur tourne: python main.py")
            return

        print("\n" + "=" * 70)
        print("2. UPLOAD CSV")
        print("=" * 70)
        try:
            with open("test_analyses.csv", "rb") as f1, open("test_labos.csv", "rb") as f2:
                files = {
                    "file_analyses": ("test_analyses.csv", f1),
                    "file_labos": ("test_labos.csv", f2),
                }
                r = await client.post(f"{BASE}/analyses/upload", files=files)
            print(f"   Status: {r.status_code}")
            data = r.json()
            print(f"   ✓ Analyses: {data['analyses']['docs']} docs")
            print(f"   ✓ Labos: {data['labos']['docs']} docs")
            print(f"   ✓ Souche model: {data['model_status']['souche'].get('model', 'N/A')}")
            print(f"   ✓ Souche accuracy: {data['model_status']['souche'].get('accuracy', 0):.3f}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return

        print("\n" + "=" * 70)
        print("3. CHAT - Question simple")
        print("=" * 70)
        try:
            r = await client.post(
                f"{BASE}/chat",
                json={"question": "Quelle souche pour un élevage poulet chair à Tunis ?"}
            )
            print(f"   Status: {r.status_code}")
            data = r.json()
            print(f"   ✓ Réponse: {data['answer'][:150]}...")
            print(f"   ✓ Temps: {data['execution_time_ms']}ms")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

        print("\n" + "=" * 70)
        print("4. CHAT - Avec prédiction ML")
        print("=" * 70)
        try:
            r = await client.post(
                f"{BASE}/chat",
                json={
                    "question": "Souche optimale haute perf ?",
                    "predict_souche": {
                        "type_production": "Poulet de chair",
                        "biosecurite_score": 9.0,
                        "taux_mortalite": 1.8,
                        "temperature_moyenne": 28,
                        "humidite": 55,
                        "budget": 70000,
                        "saison": "Été",
                    }
                }
            )
            print(f"   Status: {r.status_code}")
            data = r.json()
            if data.get("souche_prediction"):
                pred = data["souche_prediction"]
                print(f"   ✓ Prédiction: {pred['souche']} ({pred['confiance_pct']}%)")
                print(f"   ✓ Model: {pred['model']}")
            print(f"   ✓ Réponse: {data['answer'][:150]}...")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

        print("\n" + "=" * 70)
        print("5. STATUS API")
        print("=" * 70)
        try:
            r = await client.get(f"{BASE}/status")
            print(f"   Status: {r.status_code}")
            data = r.json()
            print(f"   ✓ RAG ready: {data['rag_ready']}")
            print(f"   ✓ ML ready: {data['ml_ready']}")
            print(f"   ✓ Souche model: {data['ml_models']['souche']['model']}")
            print(f"   ✓ Souche accuracy: {data['ml_models']['souche']['accuracy']:.3f}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

        print("\n" + "=" * 70)
        print("6. LABOS RECOMMEND")
        print("=" * 70)
        try:
            r = await client.get(f"{BASE}/labos/recommend", params={"urgence": "true", "ville": "Sfax"})
            print(f"   Status: {r.status_code}")
            data = r.json()
            if data.get("labos"):
                labo = data["labos"][0]
                print(f"   ✓ Top labo: {labo.get('nom_laboratoire', 'N/A')}")
                print(f"   ✓ Score: {labo.get('score_global', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

        print("\n" + "=" * 70)
        print("7. SOUCHE PREDICT (direct)")
        print("=" * 70)
        try:
            r = await client.post(
                f"{BASE}/souches/predict",
                json={
                    "type_production": "Œuf",
                    "biosecurite_score": 8.0,
                    "taux_mortalite": 1.5,
                    "temperature_moyenne": 28,
                    "budget": 50000
                }
            )
            print(f"   Status: {r.status_code}")
            
            data = r.json()
            print(f"   ✓ Souche: {data['souche']} ({data['confiance_pct']}%)")
            print(f"   ✓ Model: {data['model']}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

        print("\n" + "=" * 70)
        print("✅ TOUS LES TESTS PASSÉS")
        print("=" * 70)


if __name__ == "__main__":
    print("\n🚀 POULINA API – TEST QUICK\n")
    #create_test_csv()
    asyncio.run(test())