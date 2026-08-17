# QuantFolio
### A Quantitative, Python-powered Investment Simulation Platform

---

## What is QuantFolio?

QuantFolio is a desktop application designed to simulate, project, and compare personal investment strategies over a user-defined time horizon. It allows users to model their full financial picture — income streams, credit obligations, real estate projects, and investment vehicles — and observe how different decisions compound over time across multiple scenarios.

The core insight driving QuantFolio is simple: financial decisions are not made in isolation. A real estate acquisition financed by credit, layered on top of a volatile income profile, produces a trajectory that is difficult to reason about intuitively. QuantFolio makes that trajectory visible, comparable, and — ultimately — quantifiable.

---

## Key Features

- **Multi-scenario architecture** — users build and run as many investment scenarios as needed, each with its own financial profile, and compare them side by side on a unified visualization dashboard.
- **Granular financial modeling** — every income and expense is parameterized by start date, frequency, and amount, enabling month-level precision over multi-year horizons.
- **Real estate & credit modeling** — full support for property acquisition projects with associated credit financing, including amortization schedules and cash vs. credit decision modeling.
- **Projection engine** — balance trajectories are computed dynamically month-by-month using compound interest methods, reflecting the true time value of money.

---

## Quantitative Roadmap

The current version of QuantFolio operates deterministically — producing exact projections given a fixed set of parameters. This is deliberately the foundation layer.

The planned quantitative layer will introduce:

- **Monte Carlo simulation** — sampling across distributions of key uncertain parameters (income growth, asset returns, interest rate drift) to generate probabilistic scenario envelopes rather than single-path projections.
- **Confidence interval visualization** — projecting not just an expected trajectory but a range, giving users an intuitive grasp of downside and upside exposure.
- **Sensitivity analysis** — identifying which parameters drive outcome variance the most, enabling focused, informed decision-making.

---

## Technical Stack

Built in Python with a PySide6 desktop interface, a pandas-based data persistence layer, and matplotlib for embedded financial visualizations. Structured around clean service and repository abstractions, with Excel as a transparent, user-accessible data store.

---

*QuantFolio is an ongoing personal project, actively developed and versioned on GitHub.*