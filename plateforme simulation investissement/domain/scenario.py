from dataclasses import dataclass
from datetime import date

@dataclass
class Scenario:
        id : int
        id_user : int
        intitule : str
        date_in : date