
# Simulateur de scénarios d’investissement et d’aide à la décision

Application PySide permettant de centraliser, modéliser et simuler l’évolution d’un patrimoine à travers différents scénarios d’investissement (immobilier, bourse, épargne).

L’objectif est de fournir aux particuliers un outil structuré et visuel pour comprendre l’impact de leurs décisions financières dans le temps.

---

## Problématique

La gestion financière personnelle repose souvent sur des décisions complexes : choix d’investissement, gestion des crédits, anticipation des revenus et des dépenses.

Ce projet vise à répondre à la question suivante :

> Comment anticiper l’évolution de son patrimoine en fonction de ses choix financiers ?

L’application permet de structurer ces informations et de simuler leur impact sur le long terme.

---

## Fonctionnalités

### Gestion des données personnelles

Un onglet dédié permet de centraliser et modifier les informations financières :

- Métier (évolution des salaires dans le temps)
- Profil utilisateur
- Comptes bancaires
- Crédits (création, suivi, visualisation)
- Transactions :
  - Dépenses
  - Revenus

---

### Outils financiers

Un espace regroupe différents outils d’aide à la décision :

- Calculateur d’imposition
- Simulation de crédit
- Outils supplémentaires en cours d’intégration

---

### Projets d’investissement

Création et gestion de scénarios d’investissement :

- Immobilier :
  - Résidence principale
  - Investissement locatif
  - Revente
  - Crédit associé
  - Paramètres temporels
- Investissements boursiers
- Autres types d’investissement (extensibles)

---

## Méthodologie

L’évolution du patrimoine est simulée de manière déterministe, sur une base mensuelle.

Le modèle prend en compte :

- Intérêts composés
- Rendements moyens selon la nature de l’investissement
- Flux financiers :
  - Revenus
  - Dépenses
- Crédits (amortissement)
- Inflation

La simulation est effectuée mois par mois afin de reproduire de manière réaliste l’évolution du patrimoine.

---

## Visualisation

L’application intègre des graphiques dynamiques (Matplotlib) permettant de visualiser :

- Solde par compte
- Patrimoine total :
  - Brut
  - Net
- Évolution dans le temps selon la période choisie

---

## Architecture du projet

```
app/
├── ui/                # Interface PySide6 (pages, widgets)
├── services/          # Logique métier (simulation, calculs financiers)
├── repositories/      # Accès aux données (Excel via pandas)
├── models/            # Structures de données
├── data/              # Fichiers Excel
└── main.py
```

---

## Données

Les données sont stockées dans un fichier Excel structuré en plusieurs feuilles :
- Profils
- Comptes
- Banques
- Crédits
- Dépenses
- Recettes
- Scénarios
- Projets

Cette organisation permet une gestion simple et extensible des données.

--- 

## Installation : 
```
git clone https://github.com/ToniMoreau/portfolio-quantitative-projects.git
cd portfolio-quantitative-projects
cd "plateforme simulation investissement"
pip install -r requirements.txt

```

---

## Utilisation : 
```
python main.py
```

---

## Étapes principales : 
Créer un profil et renseigner ses informations personnelles et financières.
Ajouter comptes , crédits, et transactions
Créer des projets d’investissement
Visualiser l’évolution du patrimoine.

---

## Objectif du projet
Ce projet a été développé dans un cadre personnel avec plusieurs objectifs :
- Mieux comprendre et anticiper ses décisions financières
- Construire un outil utile pour les particuliers
- Approfondir la modélisation financière
- Développer des compétences en visualisation et en architecture logicielle

---

## Limites actuelles
- Modèle déterministe (pas encore de simulation stochastique)
- Rendements simplifiés (moyennes fixes)
- Fiscalité partiellement modélisée
- Projet en phase initiale (développement en cours 100h de travail)

---

## Améliorations prévues
- Simulation Monte Carlo (incertitude des rendements)
- Modélisation plus fine des actifs
- Intégration avancée de la fiscalité
- Ajout de nouveaux outils financiers
- Possibilité d’intégrer des approches IA pour l’aide à la décision

---

## Technologies utilisées
- Python
- PySide6
- pandas
- matplotlib
- numpy

---

## Auteur
Toni Moreau

---

## Licence
MIT
