from dataclasses import dataclass

@dataclass
class Recette:
    id : int
    intitule : str
    montant : float
    frequence : str
    nature : str
    
    id_scenario : int
    id_user : int
    id_compte : int

    
    