import numpy as np

# Markov method for the simulation 
#Gambler's Ruin characteristics : 2 absorbing states (0,N)
def simulate_gambler_ruin(N,p,i0, rng):
    if (type(N)!= int) or N<1:
        raise ValueError("Veuillez entrer un entier naturel valide")
    elif not(0 < p < 1):
        raise ValueError("Veuillez entrer une probabilité valide")
    elif not(0<= i0 <= N):
        raise ValueError("Veuillez entrer une état initial valide")
    
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
        
        
        
        
        
        
    

    
