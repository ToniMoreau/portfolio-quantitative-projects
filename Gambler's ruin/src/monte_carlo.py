import numpy as np
from markov import simulate_gambler_ruin

def estimate_hit_probability(N, p, i0, M, rng):
    cpt_Y=0
    for _ in range(M):
        absorbant, tau = simulate_gambler_ruin(N,p,i0,rng)
        if absorbant == N:
            cpt_Y += 1

    theta_hat = cpt_Y/M
    se = np.sqrt(theta_hat*(1-theta_hat)/M)
    
    return theta_hat, se

def estimate_absorption_time(N, p, i0, M, rng):
    taus = np.array([0 for i in range(M)])
    for i in range(M):
        absorbing, tau = simulate_gambler_ruin(N,p,i0, rng)
        taus[i] = tau
    
    mu_hat = taus.mean()
    
    s2 = taus.var(ddof=1)
    se_hat = np.sqrt(s2/M)
    
    return mu_hat, se_hat
 
 
def ci_95(estim, se):
    return (float(round(estim - 1.96 * se,3)), float(round(estim + 1.96 * se,3)))
 