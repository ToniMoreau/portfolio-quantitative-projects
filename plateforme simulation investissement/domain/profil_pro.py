from dataclasses import dataclass, field
from typing import ClassVar
from domain.fiscalité import * 
from datetime import date

@dataclass 
class Profil_pro:
    intitule_métier : str #✅

    def __str__(self):
        return f'{self.intitule_métier}'

@dataclass
class Salarié(Profil_pro):
    #ancienneté_mois: int #✅
    date_in :date
    date_out:date 
    
    privé : bool #✅
    id_metier : int | None = None
    id_salarié: int | None = None
    
    id_compte : int | None = None
    
    id_recette : int | None = None
    annuel_brut: float| None = None
    annuel_net : float | None = None
    
    prélèvement_source_pct : float | None = None
    
    def get_annuel_net(self) -> float:        
        if self.annuel_net:
            return self.annuel_net
        if self.privé == "Oui":
            taux = 0.83
        else:
            taux = 0.77

        return self.annuel_brut * taux

    @property
    def annuel_net_apres_ps(self) -> float:
        return self.annuel_net*(1-self.prélèvement_source_pct/100)
    
    @property
    def mensuel_brut(self) -> float:
        return self.annuel_brut/12

    def __str__(self):
        str = f"{self.intitule_métier} depuis X "
        return str