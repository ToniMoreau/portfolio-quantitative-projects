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