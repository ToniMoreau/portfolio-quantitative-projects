# Monte Carlo Simulation of Gambler’s Ruin

## Overview

This project studies an absorbing random walk (Gambler's Ruin problem) using Monte Carlo Simulation.

We estimate: 
- The probability of absorption at state N 
- The expected absorption time

Results are compared with closed-form theoretical formulas.  

The project emphasizes theoretical validation of simulation results
and illustrates the $O(M^{-1/2})$ convergence rate of Monte Carlo methods.


## Model

We consider a Markov chain on {0,1,...,N} with absorbing states 0 and N.

For $i \in \left\{1,\dots,N-1\right\}$:  
$$
\mathbb{P}(X_{n+1} = i+1 \mid X_n = i) = p,\quad
\mathbb{P}(X_{n+1} = i-1 \mid X_n = i) = 1 - p = q
$$


The absorption time is :   
$$
\tau = \min {\left\{ n \ge 0 : X_n \in \left\{ 0,N \right\} \right\} }
$$

## Monte Carlo Estimation 
For M simulated trajectories :
**Probability estimator**  
$$
\hat\theta = \frac 1 M \sum\limits_{i=1}^M 1_{\left\{\tau_N < \tau_0 \right\}}
$$

> where $\tau_0$ and $\tau_N$ are the first hitting times of the absorbing states.
- Time estimator :   
$$
\hat\mu = \frac 1 M \sum\limits_{m=1}^M \tau^{(m)}
$$

> where m is the m-th trajectory observed

95% confidence intervals are computed using the Central Limit Theorem.

## Theoretical results 
for p = $ \frac 1 2$ :  
$$
\mathbb P_i(\tau_N < \tau_0) = \frac i N, \quad \mathbb E_i[\tau] = i(N-i)
$$

for $p \not= \frac 1 2$:  
$$
\mathbb P_i(\ \tau_N < \tau_0 ) = \frac {1 - (\frac{1-p}{p})^i}{1 - (\frac{1-p}{p})^N}
$$

Simulations confirm convergence toward theoretical values and illustrate the $\mathcal O(M^{-1/2})$ Monte Carlo error decay.

## How to run : 
> python main.py

## Project Structure 
``` 
src/  
    markov.py      # simulation engine (Markov Model)  
    monte_carlo.py # estimators + CI95  
    theory.py      # closed-form formulas 
```

## Skills Demonstrated

- Markov chain modeling
- Monte Carlo estimation
- Confidence interval construction
- Theoretical validation

- Modular scientific programming in Python








