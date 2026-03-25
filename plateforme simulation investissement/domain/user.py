from dataclasses import dataclass, field
from typing import Optional

from .profil_pro import Salarié
from.banque import CompteBancaire
@dataclass
class User:
    id: int
    username: str
    firstname: str = ""
    lastname: str = ""
    age: int | None = None
    email: str = ""
    phone: str = ""
    password: str = ""
    
    profil_pro_id: int | None = None
    scenarios_ID : list[int] | None = None
    credits_ID : list[int] | None = None
    
     

    def public_infos(self):
        if self.age and self.firstname and self.lastname:
            txt = str(self.firstname) + " | " + str(self.lastname) + " | " + str(self.age) + "ans"
            return txt