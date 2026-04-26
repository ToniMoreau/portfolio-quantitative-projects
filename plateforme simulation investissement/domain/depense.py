from dataclasses import dataclass
from datetime import date
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
    
    date_in:date 
    date_out:date
    
    id_transaction : int | None = None


    
    