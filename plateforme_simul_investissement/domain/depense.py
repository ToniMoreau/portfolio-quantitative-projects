from dataclasses import dataclass

@dataclass
class Depense:
    id : int
    intitule : str
    montant : float
    frequence : str
    nature : str
    
    id_scenario : int
    id_user : int
    id_compte : int

    
    