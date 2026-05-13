# Architecture Poulina – Séparation BD vs IA

## Principes fondamentaux

1. **BD est source de vérité** : Toute donnée objective vient de la BD
2. **IA justifie et recommande** : LLM ne crée pas de données, il explique
3. **ML prédit** : Modèles décident parmi options, pas de création ex-nihilo
4. **RAG contextualise** : Historique + documents enrichissent la réponse

## Flux de décision

### Couche 1 : Intent Router
Question utilisateur
↓
Analyse mots-clés (keyword matching)
↓
Décide : BD | RAG | ML | COMBINED

### Couche 2 : Exécution
BD          : Requête SQL directe → JSON brut
RAG         : BD + RAG + LLM → Réponse narratif
ML          : BD + Modèle + Métier + LLM → Recommandation
COMBINED    : Plusieurs approches → Réponse riche

### Couche 3 : LLM (optionnel)

Formatte réponses en langage naturel
Justifie recommandations
Contextualize données
N'invente JAMAIS de données


## Matrice des types de questions

| Type | Intent | Source | LLM | Exemple |
|------|--------|--------|-----|---------|
| Comptage | BD | Oracle | Non | Combien de centres ? |
| Existence | BD | Oracle | Non | Labo à Tunis existe ? |
| Historique | RAG | Oracle + RAG | Oui | Alertes Salmonelle récentes ? |
| Analyse | RAG | Oracle + RAG | Oui | Pourquoi ce labo faible ? |
| Recommandation | ML | Oracle + ML + Métier | Oui | Meilleure souche ? |
| Prédiction | ML | Oracle + ML | Oui | Centre à risque ? |
| Coût | ML | Oracle + Calcul | Oui | Coût changement ? |

## Endpoints par couche

### Couche BD (pas de LLM)
GET  /api/v1/data/centres?gouvernorat=Bizerte
GET  /api/v1/data/labos?accepte_urgence=true
GET  /api/v1/data/souches?type_produit=Poulet
GET  /api/v1/data/centre/1
GET  /api/v1/data/count

### Couche Recommandation (ML + BD + LLM)
POST /api/v1/recommend/souche
POST /api/v1/recommend/labo
POST /api/v1/recommend/analyse-frequence

### Couche Chat (RAG + LLM)
POST /api/v1/chat                    (langage naturel)
POST /api/v1/smart-chat              (routing intelligent)

### Couche Analyse (Upload + Train)
POST /api/v1/analyses/upload
POST /api/v1/analyses/train-from-oracle

## Fluxes concrets

### Exemple 1 : "Combien de centres ?"
Intent: BD
Endpoint: GET /data/count
BD Query: SELECT COUNT(*) FROM centre_elevage
Response: {"centres": 6}
LLM: Non utilisé

### Exemple 2 : "Y a-t-il eu des alertes Salmonelle ?"
Intent: RAG
Endpoint: POST /chat
BD Query: SELECT * FROM historique_maladie WHERE nom_maladie='Salmonelle'
RAG: Indexe 10 dernières alertes
LLM: "Oui, 2 alertes détectées... [détails]"

### Exemple 3 : "Quelle souche recommandes-tu ?"
Intent: ML
Endpoint: POST /recommend/souche

BD: SELECT * FROM souche WHERE type_produit='Poulet'
ML: Random Forest → "Cobb 500" (94%)
Métier: Filtre budget, région
LLM: Justification
Response: {
"principale": "Cobb 500",
"alternatives": [...],
"costs": {...},
"justification": "..."
}


## Règles d'or

1. **Jamais d'invention** : Si BD retourne rien → erreur propre, pas hallucination
2. **Traçabilité** : Chaque recommandation doit citer ses sources
3. **Confiance** : Inclure scores de confiance (ML) ou sources (BD)
4. **Fallback** : Si LLM échoue → retourner données brutes + message
5. **Audit** : Logger toutes requêtes pour traçabilité

## Structure fichiers
backend/
├── app/api/
│   ├── data.py              ← BD Direct (sans LLM)
│   ├── recommendations.py   ← ML + Métier + LLM
│   ├── chat.py              ← RAG + LLM
│   └── analyses.py          ← Upload/Train
│
├── app/services/
│   ├── intent_router.py     ← Routing décision
│   ├── recommendation_engine.py ← Logique métier
│   └── sql_generator.py     ← SQL depuis question
│
└── app/data/
├── database.py          ← Connexion Oracle
└── models.py            ← Pydantic models

## Performance attendue

| Opération | Temps | Notes |
|-----------|-------|-------|
| GET /data/centres | 50ms | BD directe |
| POST /chat (RAG) | 2-3s | Retrieve + LLM |
| POST /recommend/souche | 500ms | ML + Métier |
| POST /recommend/labo | 300ms | Scoring |

---

## Maintenance

- **Intent Router** : Ajouter keywords si questions mal routées
- **SQL Generator** : Ajouter patterns pour nouvelles questions structures
- **Recommendation Engine** : Tuner poids si recommandations mauvaises
- **LLM Prompt** : Ajuster SYSTEM_PROMPT si réponses hors domaine