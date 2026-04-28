# Chatbot IA Poulina — Synthèse des besoins & Questions/Réponses

## 1. Contexte du projet
Application complète destinée aux filiales Poulina pour moderniser la gestion des demandes d’analyses, laboratoires, souches avicoles et aide à la décision via IA.

### Filiales / Marques concernées
- **Dick**
- **SNA**
- **Gipa**
- **MedOil**

Répartition :
- **Dick + SNA** = Avicole
- **Gipa + MedOil** = Agro-Alimentaire

---

## 2. Objectifs métier principaux

### Chatbot IA
- Trouver la meilleure souche pour chaque élevage
- Définir la meilleure souche par centre / bâtiment
- Prévenir si maladie critique
- Identifier qui pourrait être infecté
- Définir la priorité des analyses
- Donner informations sur maladies / souches
- Recommander quoi produire (poulet / dinde / œuf) selon consommation en Tunisie
- Recommander meilleur laboratoire / laborantin
- Estimer coût du changement de souche
- Déterminer fréquence des analyses en cas de maladie

### Modernisation SI
- Remplacer application ancienne (VBA / Crystal Report)
- Interface moderne
- Gestion des rôles
- Base de données propre
- Gestion des dates limites / échéances
- Communication fluide demandeurs ↔ laboratoires

---

## 3. Données d’entrée prévues

### Demandes d’analyse
- Numéro analyse
- Type analyse
- Effectuée ou non
- Type de souche
- Pourcentage réussite / sécurité
- Type échantillon
- Date prélèvement
- Date analyse
- Date déchéance
- Centre d’élevage
- Niveau satisfaction
- Labo
- Laborantin
- Provenance poulet (pays)

### Non conforme si
- Maladie détectée
- Résultats inférieurs à la moyenne
- Souche détectée ≠ souche élevage
- Problème prélèvement
- Mauvais échantillonnage

### Critique si
- Date prélèvement dépassée
- Durée conservation dépassée

### Priorité
- Niveau de 1 à 5

---

## 4. Laboratoires / Laborantins

Critères de recommandation :
- Plus proche
- Disponible dans les délais
- Plus compétent (temps d’analyse)
- Plus habitué (historique sur type analyse)
- Spécialité

---

## 5. Gestion élevage / souches

### Structure
- Un centre d’élevage contient plusieurs bâtiments
- Un centre d’élevage contient plusieurs souches
- Un bâtiment contient **une seule souche**

### Critères meilleure souche
- Fertilité maximale
- Décès minimal
- Résistance maladies (ex: Salmonelle)
- Coût
- Localisation
- Type de produit final
- Contraintes internes éventuelles

---

## 6. Utilisateurs cibles
- Employés traitant les filiales
- Gestionnaires analyses
- Responsables laboratoires
- Administration

---

## 7. Contraintes

### Sécurité
- Authentification sécurisée
- Privilèges par rôles

### Validation projet
- Génération d’un bulletin d’analyse complet

---

## 8. IA / Technique

Préférences mentionnées :
- Claude préféré
- Tester API perso (Mistral ?)
- Démo n8n sous 2 semaines
- Intégration dans application de Lilia à définir

---

## 9. Recommandations de réalisation

### Backend
- Oracle Database
- API REST

### Frontend
- Oracle APEX ou Web App moderne

### IA
- Moteur RAG sur base interne
- Requêtes SQL + règles métier + scoring

### Dashboard
- Alertes critiques
- Centres à risque
- Délais analyses
- Performance laboratoires

---
