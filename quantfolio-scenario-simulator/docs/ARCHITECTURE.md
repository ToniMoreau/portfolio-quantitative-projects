# QuantFolio — Architecture Documentation

---

## Project Structure

```
portfolio-simulator/
├── data/                          # Excel-based data store (one file per user profile)
├── docs/                          # Project documentation
├── domain.entities/                        # Core domain.entities entities
├── repositories/                  # Data access layer (Excel ↔ domain.entities objects)
├── services/
│   └── domain.entities_services/           # Business logic layer
├── ui/                            # PySide6 interface
│   ├── sous_pages/                # All application pages, organized by domain.entities
│   │   ├── Auth/                  # Authentication pages
│   │   ├── banque/                # Standalone bank pages
│   │   └── Profil/                # Main profile section (post-login)
│   │       ├── actifs/            # Asset pages
│   │       ├── gestion/           # Financial management pages
│   │       │   ├── banque/        # Bank accounts & credits
│   │       │   │   ├── comptes_bancaires/
│   │       │   │   └── crédits/
│   │       │   └── transaction/   # Income, expenses & transfers
│   │       ├── investissement/    # Investment pages
│   │       ├── outils/            # Tools & calculators
│   │       └── projets/           # Real estate project pages
│   └── widgets/                   # Reusable UI components
├── utils/                         # Shared utilities
├── main.py                        # Application entry point
├── session.py                     # Active session state
├── style.qss                      # Global Qt stylesheet
└── __init__.py
```

---

## domain.entities Model

The domain.entities layer defines the core business entities of QuantFolio. Each entity maps to a dedicated sheet in the Excel data store.

> ⚠️ *Note: not all domain.entities classes are actively used in the current version. This section reflects the full intended model.*

| File | Entity | Description |
|---|---|---|
| `user.py` | `User` | Application user account |
| `scenario.py` | `Scenario` | A named investment scenario owned by a user |
| `identité.py` | `Identite` | Personal identity details |
| `profil_pro.py` | `ProfilPro` | Professional profile (income source, occupation) |
| `profil_fiscal.py` | `ProfilFiscal` | Tax profile |
| `banque.py` | `Banque` | Bank account with balance and interest rate |
| `immo.py` | `ProjetImmobilier` | Real estate project, with `mode_financement` enum (`Cash`, `Crédit`, `Indéfini`) |
| `investissement.py` | `Investissement` | Any investment vehicle |
| `recette.py` | `Recette` | Recurring or one-off income entry |
| `depense.py` | `Depense` | Recurring or one-off expense entry |
| `fiscalité.py` | `Fiscalite` | Tax computation entity |

### Key Relationship

`ProjetImmobilier` and `Credit` share an asymmetric relationship:
- A `ProjetImmobilier` exists independently.
- A `Credit` is always attached to a `ProjetImmobilier`.
- Credit finalization and `mode_financement` update are treated as a **single atomic operation** to guarantee data integrity.

---

## Repository Layer

Repositories handle all read/write operations against the Excel data store (`data/data_profil.xlsx`), one sheet per entity type. They are built on top of `pandas` and expose standard CRUD interfaces to the service layer.

| File | Responsibility |
|---|---|
| `userRepository.py` | User persistence |
| `scenarioRepository.py` | Scenario persistence |
| `banqueRepository.py` | Bank account persistence |
| `compteBancaireRepository.py` | Compte bancaire persistence |
| `creditRepository.py` | Credit persistence |
| `depenseRepository.py` | Expense persistence |
| `recetteRepository.py` | Income persistence |
| `InvestissementRepository.py` | Investment persistence |
| `metier_repository.py` | Professional profile persistence |
| `repositories.py` | Aggregator — instantiates and exposes all repositories |

---

## Service Layer

Services encapsulate business logic and sit between the UI and the repository layer. They are injected into pages via `AppContext`.

| File | Responsibility |
|---|---|
| `banqueService.py` | Bank account operations |
| `compteBancaireService.py` | Compte bancaire operations |
| `creditService.py` | Credit lifecycle, including atomic finalization |
| `depenseService.py` | Expense management |
| `recetteService.py` | Income management |
| `investissementService.py` | Investment management |
| `fiscaliteService.py` | Tax computation |
| `metierService.py` | Professional profile management |
| `scenarioService.py` | Scenario creation and management |
| `appContext.py` | Dependency injection container — holds all services and repositories |
| `authService.py` | Authentication logic |
| `profileService.py` | User profile management |
| `pdf_exporter.py` | PDF export utility |

---

## UI Architecture

The interface is built with **PySide6**, structured around a `QStackedWidget`-based navigation system. Each page is a `QWidget` subclass following a `load()` convention for lazy initialization.

### Entry Point & Window

- `main.py` — launches the application, initializes `AppContext`, creates `MainWindow`
- `main_window.py` — root window, owns the `QStackedWidget`, handles page registration and navigation
- `session.py` — holds active session state (logged-in user, active scenario)
- `style.qss` — global Qt stylesheet applied at startup

### Page Map

```
Auth/
├── auth_page.py              # Authentication entry point
├── loginWidget.py            # Login form
└── registerWidget.py         # Registration form

Profil/
├── dashboard.py              # Post-login landing page
├── profile_page.py           # User profile overview
├── visualisation_page.py     # Multi-scenario visualization dashboard

├── actifs/
│   ├── actifs_page.py
│   └── actifs_immo_page.py

├── gestion/
│   ├── add_scenario_page.py
│   ├── edit_metier_page.py
│   ├── edit_profil_page.py
│   ├── infos_hub_page.py
│   ├── banque/
│   │   ├── banque_page.py
│   │   ├── comptes_bancaires/
│   │   │   ├── comptes_bancaires_page.py
│   │   │   ├── ajouter_compte_bancaire.py
│   │   │   └── cb_visualizer_page.py
│   │   └── crédits/
│   │       ├── credits_page.py
│   │       ├── credits_immo_page.py
│   │       ├── ajouter_credit.py
│   │       ├── credit_visualizer_page.py
│   │       ├── finaliser_projet_page.py
│   │       └── liste_projets_page.py
│   └── transaction/
│       ├── transactions_page.py
│       ├── depense_page.py
│       ├── revenu_page.py
│       └── transfert_page.py

├── investissement/
│   ├── investissement_hub.py
│   ├── infos_projet_page.py
│   └── nouveau_projet_page.py

├── outils/
│   ├── outils_page.py
│   └── calcul_impot_page.py

└── projets/
    ├── projets_hub_page.py
    ├── immo_projets_page.py
    └── add_immo_projet_page.py
```

### Widgets

- `graph_widget.py` — reusable matplotlib-embedded chart widget for financial projections

---

## Key Design Decisions

### Lazy page initialization
Pages implement a `load()` method called only when the page becomes visible, avoiding unnecessary data fetches at startup.

### Dependency injection via AppContext
`AppContext` is instantiated once at startup and passed down to all pages. It holds all services and repositories, keeping pages decoupled from data access concerns.

### Dynamic projection computation
Account balances are never stored as projected values. Projections are computed dynamically month-by-month at visualization time using the equivalent monthly rate:
```
monthly_rate = (1 + annual_rate) ** (1/12) - 1
```

### Atomic credit finalization
Creating a `Credit` and updating the associated `ProjetImmobilier.mode_financement` always happen in a single operation to prevent data inconsistency.

### Excel as data store
Each entity type maps to a dedicated sheet in `data_profil.xlsx`. This keeps data human-readable and accessible outside the application, at the cost of concurrency limitations (acceptable for a single-user desktop app).

---

## Utilities

| File | Description |
|---|---|
| `utils/date.py` | Date manipulation helpers |
| `utils/finance_format.py` | Number and currency formatting helpers |

---

*This document reflects the architecture as of the current development stage. It will be updated as new features are introduced.*