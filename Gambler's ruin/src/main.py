from monte_carlo import estimate_absorption_time, estimate_hit_probability, ci_95
from theory import theta_theory
import numpy as np

# This is the code to run the simulations

# First observation : Estimate theta_hat and mu_hat with parameters
rng1 = np.random.default_rng(1) #random variable for theta estimation
rng2 = np.random.default_rng(2) #random variable for mu estimation
N = 10    #maximum state {0,1...,N}
p = 0.5   #probability
i0 = 6    #initial state
M = 1000  #size of simulation (number of trajectories)

theta_hat, se_hat1 = estimate_hit_probability(N,p,i0, M, rng1)
mu_hat, se_hat2 = estimate_absorption_time(N,p,i0, M, rng2)

print(f"theta_hat: {theta_hat} 95% confidence interval: {ci_95(theta_hat, se_hat1)}\n mu_hat: {mu_hat} 95% confidence interval: {ci_95(mu_hat, se_hat2)}")



# mu estimator observations : (expected hitting time)
## Theory vs Estimator comparison knowing: 
# expected hitting time for N from initial state i0 = i0*(N-i0)
Ms = np.array([100,300,1000,3000]) #different size of observation
N = 10                             #size of space of states
p = 0.5                            #Probability
i0 = 6                             #initial state

mu_th = i0*(N-i0)                  #theoretical expression

for M in Ms:
    rng100 = np.random.default_rng(100 + M)
    mu_hat, se_hat = estimate_absorption_time(N,p,i0,M,rng100)
    mu_hat = round(mu_hat, 3)
    
    print(f"M = {M} : \nmu_hat = {mu_hat}\nci 95 : {ci_95(mu_hat, se_hat)} \nabsolute error : {round(abs(mu_hat - mu_th),3)}")

#On observe que l’erreur diminue globalement quand 𝑀 augmente, conformément à la loi 1/sqrt(M) du monte carlo
#On observe une diminution globale de l’erreur quand M augmente, compatible avec la décroissance 𝑂(𝑀−1/2)O(M−1/2) de l’erreur Monte Carlo. Les fluctuations restantes viennent de la variance élevée du temps d’absorption.

# Theta estimator observations
## Theory vs Estimator comparison knowing: 
## for p = 0.5, P(t_N < t_0) = i0/N | for p != 0.5 P(t_N < t_0) = (1-(q/p)**i0)/(1-(q/p)**N)

p1 = 0.5                          #0.5 probability case
N1 =10                            #0.5 space of states size case
rng1 = np.random.default_rng(5)   #0.5 random variable case
i0_1 = 6                          #0.5 initial state case

p2 = 0.55                         #!= 0.5 probability case
N2 =50                            #!= 0.5 space of states size case
rng2 = np.random.default_rng(5)   #!=0.5 random variable case
i0_2 = N2 // 2                    #!=0.5 initial state case

theta_th1 = theta_theory(N1,p1,i0_1) #p = 0.5, theoretical expression 
theta_hat1,se1 = estimate_hit_probability(N1,p1, i0_1, 2000, rng1)
low95_1, high95_1 = ci_95(theta_hat1, se1)
valid95_1 = low95_1 <= theta_th1 <= high95_1

theta_th2 = theta_theory(N2,p2, i0_2) #p != 0.5, theoretical expression
theta_hat2, se2 = estimate_hit_probability(N2, p2, i0_2, 2000, rng2)
low95_2, high95_2 = ci_95(theta_hat2, se2)
valid95_2 = low95_2 <= theta_th2 <= high95_2

print(f"theoretical theta (p={p1}) : {theta_th1} | theta_hat : {theta_hat1} | ci95 : {[round(low95_1,3), round(high95_1,3)]} | theoretical theta in ci95 : {'yes' if valid95_1 else 'no'}")
print(f"theoretical theta (p={p2}) : {round(theta_th2,3)} | theta hat : {theta_hat2} | ci95 : {[round(low95_2,3), round(high95_2,3)]} | theoretical theta in ci95 : {'yes' if valid95_2 else 'no'}")

## Empirical checking for the 95% confidence interval 

simul = 50 
N = 25
p = 0.5
i0 = 12
M = 1000
theta_th = theta_theory(N,p, i0)
cpt_ic_valid = 0 #counts if theoretical value hit the confidence interval

for i in range(simul):
    rng = np.random.default_rng(10+i)
    
    theta_hat, se = estimate_hit_probability(N, p, i0, M, rng)
    low95, high95= ci_95(theta_hat, se)
    
    if low95 <= theta_th <= high95:
        cpt_ic_valid += 1
        
ratio_ic95_valid = 100* cpt_ic_valid/simul

print(f"In {round(ratio_ic95_valid,1)}% of cases, theoretical theta is in ci95 ")