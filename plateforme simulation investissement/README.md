# Investment Scenario Simulator and Decision Support Tool

PySide application designed to centralize, model, and simulate the evolution of personal wealth across different investment scenarios (real estate, financial markets, savings).

The goal is to provide individuals with a structured and visual tool to better understand the long-term impact of their financial decisions.

---

## Problem Statement

Personal financial management involves complex decisions: investment choices, credit management, income and expense forecasting.

This project aims to answer the following question:

> How can one anticipate the evolution of their wealth based on financial decisions?

The application structures financial data and simulates its long-term impact.

---

## Features

### Personal Data Management

A dedicated interface allows users to manage financial information:

- Career (salary evolution over time)
- User profile
- Bank accounts
- Credits (creation, tracking, visualization)
- Transactions:
  - Expenses
  - Income

---

### Financial Tools

A set of tools to support financial decision-making:

- Tax calculator
- Credit simulation
- Additional tools planned

---

### Investment Projects

Creation and management of investment scenarios:

- Real estate:
  - Primary residence
  - Rental investment
  - Property resale
  - Associated credit
  - Time parameters
- Financial investments
- Other investment types (extensible)

---

## Methodology

Wealth evolution is simulated deterministically on a monthly basis.

The model includes:

- Compound interest
- Average returns depending on the investment type
- Financial flows:
  - Income
  - Expenses
- Credit amortization
- Inflation

The simulation is computed month by month to provide a realistic evolution of wealth.

---

## Visualization

The application integrates dynamic visualizations (Matplotlib):

- Account balances
- Total wealth:
  - Gross
  - Net
- Time evolution over a selected period

---

## Architecture

```
app/
├── ui/
├── services/
├── repositories/
├── models/
├── data/
└── main.py
```

---

## Data

Data is stored in a structured Excel file with multiple sheets:

- Profiles
- Accounts
- Banks
- Credits
- Expenses
- Income
- Scenarios
- Projects

---

## Installation

```bash
git clone https://github.com/ToniMoreau/portfolio-quantitative-projects.git
cd portfolio-quantitative-projects
cd "plateforme simulation investissement"
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

---

## Workflow

- Create a profile and input financial data  
- Add accounts, credits, and transactions  
- Create investment projects  
- Visualize wealth evolution  

---

## Project Objectives

This project was developed with the following goals:

- Better understand and anticipate financial decisions  
- Build a practical tool for individuals  
- Explore financial modeling  
- Develop skills in data visualization and software architecture  

---

## Current Limitations

- Deterministic model (no stochastic simulation yet)  
- Simplified return assumptions  
- Partial tax modeling  
- Early-stage development (~100 hours)  

---

## Future Improvements

- Monte Carlo simulation  
- More advanced financial modeling  
- Full tax integration  
- Additional financial tools  
- Potential integration of AI-based decision support  

---

## Technologies

- Python  
- PySide6  
- pandas  
- matplotlib  
- numpy  

---

## Author

Toni Moreau  

---

## License

MIT  


🇫🇷 Version française

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
