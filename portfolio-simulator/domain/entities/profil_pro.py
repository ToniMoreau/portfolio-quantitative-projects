from dataclasses import dataclass, field
from typing import ClassVar
from domain.entities.fiscalité import * 
from datetime import date
from domain.enums import DependentType
@dataclass 
class Profil_pro:
    intitule_métier : str #✅

    def __str__(self):
        return f'{self.intitule_métier}'
    
    def get_dependent_type(self):
        return DependentType.METIER

@dataclass
class Salarié(Profil_pro):
    #ancienneté_mois: int #✅
    date_in :date
    date_out:date 
    
    privé : bool #✅
    id : int | None = None
    id_salarié: int | None = None
    
    id_compte : int | None = None
    
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
    
    def mensuel_net(self) -> float:
        return self.annuel_net /12
    
    def est_actif(self, date_courante :date):
        if self.date_in <= date_courante <= self.date_out:
            return True
        
        return False
    def __str__(self):
        str = f"{self.intitule_métier} depuis X "
        return str