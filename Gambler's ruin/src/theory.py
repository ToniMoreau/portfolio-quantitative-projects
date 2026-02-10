
# Methode to check theoretical values for Theta, wether p =1/2 or not
def theta_theory(N, p, i0):
    if abs(p-0.5) < 1e-12:
        return i0/N
    else:
        q = 1-p
        return (1-(q/p)**i0)/(1-(q/p)**N)