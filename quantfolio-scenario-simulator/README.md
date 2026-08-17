# QuantFolio : Investment Scenario Simulator and Decision Support Tool

*QuantFolio* - a layered financial scenario simulator in Python. Models credit mechanics, banking flows and asset positions over multi-period horizons, with scenarios run in parallel to compare outcome paths under differing assumptions. The domain layer is decoupled from the computation engine, so the current deterministic model can be replaced by a stochastic one without touching the interface. A Monte Carlo pricing and valuation module is in development.

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
- Different Investment types (Real Estate, Stocks)

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
├── data/
├── domain/
├── docs/
├── utils/
└── main.py
```

---

## Data

Data is stored in a structured Excel file with multiple sheets:

- Profiles
- Accounts
- Banks
- Jobs
- Credits
- Expenses
- Income
- Scenarios
- Investments:
  - Real Estate
  - Stock Options

---

## Installation

```bash
git clone https://github.com/ToniMoreau/portfolio-quantitative-projects.git
cd portfolio-quantitative-projects
cd "quantfolio-scenario-simulator"
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
- Add accounts, jobs, credits, and transactions  
- Create investment projects  
- Visualize wealth evolution  
- Compare one scenario against others

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
- Early-stage development (~300 hours)  

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