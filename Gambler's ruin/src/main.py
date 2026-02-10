from monte_carlo import estimate_absorption_time, estimate_hit_probability, ci_95
from theory import theta_theory
import numpy as np



rng1 = np.random.default_rng(1)
rng2 = np.random.default_rng(2)
N = 10
p = 0.5
i0 = 6
M = 1000

theta_hat, se_hat1 = estimate_hit_probability(N,p,i0, M, rng1)
mu_hat, se_hat2 = estimate_absorption_time(N,p,i0, M, rng2)

print(f"theta_hat : {theta_hat} intervalle de confiance 95 : {ci_95(theta_hat, se_hat1)}\n mu_hat : {mu_hat} intervalle de confiance 95 : {ci_95(mu_hat, se_hat2)}")



# Etude sur l'estimateur mu
## Comparaison de la théorie vs l'estimation sachant que : l'espérance du temps de premier passage en N sachant i0 vaut i0*(N-i0)
Ms = np.array([100,300,1000,3000])
N = 10
p = 0.5
i0 = 6

mu_th = i0*(N-i0)
for M in Ms:
    rng100 = np.random.default_rng(100 + M)
    mu_hat, se_hat = estimate_absorption_time(N,p,i0,M,rng100)
    mu_hat = round(mu_hat, 3)
    
    print(f"M = {M} : \nmu_hat = {mu_hat}\nic 95 : {ci_95(mu_hat, se_hat)} \nerreur absolue : {round(abs(mu_hat - mu_th),3)}")

#On observe que l’erreur diminue globalement quand 𝑀 augmente, conformément à la loi 1/sqrt(M) du monte carlo
#On observe une diminution globale de l’erreur quand M augmente, compatible avec la décroissance 𝑂(𝑀−1/2)O(M−1/2) de l’erreur Monte Carlo. Les fluctuations restantes viennent de la variance élevée du temps d’absorption.

# Etude sur l'estimateur théta
## Comparaison de la théorie vs l'estimation sachant que : 
## pour p = 0.5, P(t_N < t_0) = i0/N | pour p != 0.5 P(t_N < t_0) = (1-(q/p)**i0)/(1-(q/p)**N)

p1 = 0.5
N1 =10
rng1 = np.random.default_rng(5)
i0_1 = 6

p2 = 0.55
N2 =50
rng2 = np.random.default_rng(5)
i0_2 = N2 // 2

theta_th1 = theta_theory(N1,p1,i0_1) #p = 0.5
theta_hat1,se1 = estimate_hit_probability(N1,p1, i0_1, 2000, rng1)
low95_1, high95_1 = ci_95(theta_hat1, se1)
valid95_1 = low95_1 <= theta_th1 <= high95_1

theta_th2 = theta_theory(N2,p2, i0_2) #p != 0.5
theta_hat2, se2 = estimate_hit_probability(N2, p2, i0_2, 2000, rng2)
low95_2, high95_2 = ci_95(theta_hat2, se2)
valid95_2 = low95_2 <= theta_th2 <= high95_2

print(f"theta théorique (p={p1}) : {theta_th1} | theta_hat : {theta_hat1} | ic95 : {[round(low95_1,3), round(high95_1,3)]} | theta_théorique dans ic95 : {'oui' if valid95_1 else 'non'}")
print(f"theta théorique (p={p2}) : {round(theta_th2,3)} | theta hat : {theta_hat2} | ic95 : {[round(low95_2,3), round(high95_2,3)]} | theta_théorique dans ic95 : {'oui' if valid95_2 else 'non'}")

## Vérification pratique de l'intervalle de confiance 95%

simul = 50
N = 25
p = 0.5
i0 = 12
M = 1000
theta_th = theta_theory(N,p, i0)
cpt_ic_valid = 0
for i in range(simul):
    rng = np.random.default_rng(10+i)
    
    theta_hat, se = estimate_hit_probability(N, p, i0, M, rng)
    low95, high95= ci_95(theta_hat, se)
    
    if low95 <= theta_th <= high95:
        cpt_ic_valid += 1
        
ratio_ic95_valid = 100* cpt_ic_valid/simul

print(f"dans {round(ratio_ic95_valid,1)}% des cas, theta théorique était dans l'IC 95 ")