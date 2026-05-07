#!/usr/bin/env python
"""
TEST QUICK POULINA – Test complet de l'API
Tape : python test_quick.py
"""
import asyncio
import httpx
import json

BASE = "http://localhost:8000/api/v1"
TIMEOUT = 60

# ── Helpers ───────────────────────────────────────────────────────────────────

def header(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def ok(msg):  print(f"  ✓ {msg}")
def err(msg): print(f"  ❌ {msg}")

def show(data, keys):
    for k in keys:
        val = data.get(k, "N/A")
        if isinstance(val, float): val = round(val, 3)
        print(f"     {k}: {val}")

# ── Tests ─────────────────────────────────────────────────────────────────────

async def test_health(client):
    header("1. HEALTH CHECK")
    r = await client.get(f"{BASE}/health")
    d = r.json()
    if r.status_code == 200:
        ok(f"status={d['status']}  provider={d.get('llm_provider')}  embedding={d.get('embedding')}")
    else:
        err(f"HTTP {r.status_code}")
    return r.status_code == 200


async def test_train_oracle(client):
    header("2. ENTRAÎNEMENT DEPUIS ORACLE")
    print("  (peut prendre quelques secondes...)")
    try:
        r = await client.post(f"{BASE}/analyses/train-from-oracle")
        d = r.json()
        if r.status_code == 200:
            ok(f"status={d['status']}")
            ok(f"analyses indexées : {d['analyses']['docs']} docs  [{d['analyses']['embedder']}]")
            ok(f"labos indexés     : {d['labos']['docs']} docs")
            ok(f"souche model      : {d['model_status']['souche'].get('model')}  acc={d['model_status']['souche'].get('accuracy', 0):.3f}")
            ok(f"labo model        : {d['model_status']['labo'].get('model')}  acc={d['model_status']['labo'].get('accuracy', 0):.3f}")
            ok(f"entraîné à        : {d.get('trained_at')}")
            return True
        else:
            err(f"HTTP {r.status_code} – {d.get('detail', d)}")
            return False
    except Exception as e:
        err(f"Exception: {e}")
        return False


async def test_status(client):
    header("3. STATUS DÉTAILLÉ")
    r = await client.get(f"{BASE}/status")
    d = r.json()
    if r.status_code == 200:
        ok(f"rag_ready={d['rag_ready']}  ml_ready={d['ml_ready']}")
        ok(f"souche model : {d['ml_models']['souche']['model']}  acc={d['ml_models']['souche'].get('accuracy',0):.3f}")
        ok(f"labo model   : {d['ml_models']['labo']['model']}  acc={d['ml_models']['labo'].get('accuracy',0):.3f}")
    else:
        err(f"HTTP {r.status_code}")


async def test_chat_simple(client):
    header("4. CHAT – Souche par ville")
    r = await client.post(f"{BASE}/chat", json={
        "question": "Quelle est la meilleure souche pour un élevage poulet chair à Bizerte ?"
    })
    d = r.json()
    if r.status_code == 200:
        ok(f"model : {d['model_used']}")
        ok(f"temps : {d['execution_time_ms']} ms")
        ok(f"analyses récupérées : {len(d['retrieved_analyses'])}")
        print(f"\n  RÉPONSE :\n  {d['answer'][:400]}...")
    else:
        err(f"HTTP {r.status_code} – {d}")


async def test_chat_maladie(client):
    header("5. CHAT – Alerte maladie critique")
    r = await client.post(f"{BASE}/chat", json={
        "question": "Y a-t-il des centres atteints de Salmonelle ou Newcastle ? Quels centres sont à risque ?"
    })
    d = r.json()
    if r.status_code == 200:
        ok(f"model : {d['model_used']}")
        print(f"\n  RÉPONSE :\n  {d['answer'][:400]}...")
    else:
        err(f"HTTP {r.status_code}")


async def test_chat_labo(client):
    header("6. CHAT – Recommandation laboratoire urgent")
    r = await client.post(f"{BASE}/chat", json={
        "question": "Quel est le meilleur laboratoire disponible en urgence pour une analyse Salmonelle à Sfax ?"
    })
    d = r.json()
    if r.status_code == 200:
        ok(f"labos récupérés : {len(d['retrieved_labos'])}")
        ok(f"model : {d['model_used']}")
        print(f"\n  RÉPONSE :\n  {d['answer'][:400]}...")
    else:
        err(f"HTTP {r.status_code}")


async def test_chat_ml(client):
    header("7. CHAT – Avec prédiction ML souche")
    r = await client.post(f"{BASE}/chat", json={
        "question": "Quelle souche recommandes-tu pour ce profil ?",
        "predict_souche": {
            "type_production": "Poulet de chair",
            "biosecurite_score": 9.0,
            "taux_mortalite": 2.0,
            "temperature_moyenne": 28,
            "humidite": 55,
            "fertilite_visee": 94,
            "capacite": 15000,
            "surface_m2": 800,
            "experience_equipe": 8,
            "distance_labo": 10,
            "budget": 80000,
            "saison": "Ete",
            "demande_marche": "Élevé",
            "cout_aliment": 5.2
        }
    })
    d = r.json()
    if r.status_code == 200:
        pred = d.get("souche_prediction")
        if pred:
            ok(f"Prédiction ML : {pred['souche']}  ({pred['confiance_pct']}%)")
            ok(f"Alternatives  : {pred.get('alternatives', [])}")
            ok(f"Modèle        : {pred['model']}")
        else:
            print("  ⚠️  Pas de prédiction ML (modèle non entraîné ?)")
        print(f"\n  RÉPONSE :\n  {d['answer'][:300]}...")
    else:
        err(f"HTTP {r.status_code}")


async def test_chat_hors_sujet(client):
    header("8. CHAT – Hors sujet (doit refuser)")
    r = await client.post(f"{BASE}/chat", json={
        "question": "Quelle est la capitale de la France ?"
    })
    d = r.json()
    if r.status_code == 200:
        answer = d["answer"]
        if "hors" in answer.lower() or "domaine" in answer.lower():
            ok(f"Refus correct : {answer[:120]}")
        else:
            print(f"  ⚠️  Réponse inattendue : {answer[:120]}")
    else:
        err(f"HTTP {r.status_code}")


async def test_souche_predict(client):
    header("9. SOUCHE PREDICT – Direct (sans chat)")
    cas = [
        ("Poulet de chair", 9.0, 2.0, 28, 55, 80000, "Ete"),
        ("Oeuf",            8.0, 1.5, 26, 60, 50000, "Hiver"),
        ("Dinde",           7.0, 4.0, 25, 58, 35000, "Automne"),
    ]
    for prod, bio, mort, temp, hum, budget, saison in cas:
        r = await client.post(f"{BASE}/souches/predict", json={
            "type_production": prod,
            "biosecurite_score": bio,
            "taux_mortalite": mort,
            "temperature_moyenne": temp,
            "humidite": hum,
            "fertilite_visee": 92,
            "capacite": 12000,
            "surface_m2": 600,
            "experience_equipe": 5,
            "distance_labo": 15,
            "budget": budget,
            "saison": saison,
            "demande_marche": "Élevé",
            "cout_aliment": 5.2
        })
        d = r.json()
        if r.status_code == 200 and "souche" in d:
            ok(f"{prod:<20} → {d['souche']:<18} ({d['confiance_pct']}%)  [{d['model']}]")
        else:
            err(f"{prod} → {d.get('error', d)}")


async def test_labos(client):
    header("10. LABOS RECOMMEND")
    cas = [
        ("Tous",          {}),
        ("Urgence",       {"urgence": "true"}),
        ("Tunis urgence", {"urgence": "true", "ville": "Tunis"}),
        ("Sfax",          {"ville": "Sfax"}),
    ]
    for label, params in cas:
        r = await client.get(f"{BASE}/labos/recommend", params=params)
        d = r.json()
        if r.status_code == 200:
            labos = d.get("labos", [])
            if labos:
                top = labos[0]
                ok(f"{label:<18} → {top.get('nom_laboratoire','?')} | score={top.get('score_global','?')} | tier={top.get('tier_labo','?')}")
            else:
                print(f"  ⚠️  {label}: aucun labo retourné")
        else:
            err(f"{label} → HTTP {r.status_code}")


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              POULINA – TEST QUICK (API complète)                           ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:

        # Vérifie que le serveur tourne
        try:
            await client.get(f"{BASE}/health")
        except Exception:
            print("❌ Serveur inaccessible. Lance d'abord : python main.py")
            return

        ok_train = await test_health(client)
        ok_train = await test_train_oracle(client)

        if not ok_train:
            print("\n⚠️  Entraînement Oracle échoué – les tests chat/ML seront limités.")

        await test_status(client)
        await test_chat_simple(client)
        await test_chat_maladie(client)
        await test_chat_labo(client)
        await test_chat_ml(client)
        await test_chat_hors_sujet(client)
        await test_souche_predict(client)
        await test_labos(client)

    print(f"\n{'='*70}")
    print("  ✅ Tests terminés")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(main())