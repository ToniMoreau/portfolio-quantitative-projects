import numpy as np

# Markov method for the simulation 
# Gambler's Ruin characteristics : 
# 2 absorbing states (0,N) | p probability for +1 | 1-p for -1
def simulate_gambler_ruin(N,p,i0, rng):
    if (type(N)!= int) or N<1:
        raise ValueError("Please enter a valid natural number")
    elif not(0 < p < 1):
        raise ValueError("Please enter a natural probability")
    elif not(0<= i0 <= N):
        raise ValueError("Please enter an valid initial state")
    
    absorbants = [0,N]
    if i0 in absorbants:
        return (i0, 0)
    tau = 0
    x = i0
    while (x not in absorbants):
        u = rng.random()
        if u < p:
            x +=1
        else:
            x -=1
        tau +=1
        
    absorbing_state = x
    
    return (absorbing_state, tau)
        
        
        
        
        
        
    
    