from dataclasses import dataclass
from datetime import date
from domain.enums import DependentType
@dataclass
class Recette:
    id : int
    intitule : str
    montant : float
    frequence : str
    nature : str
    indexation : float
    
    id_scenario : int
    id_user : int
    id_compte : int

    date_in:date
    date_out:date
    
    id_transaction : int | None = None
    id_source : int | None = None
    
    def get_dependent_type(self):
        return DependentType.RECETTE

    