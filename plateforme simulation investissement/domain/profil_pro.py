from dataclasses import dataclass, field
from typing import ClassVar
from domain.fiscalité import * 

@dataclass 
class Profil_pro:
    intitule_métier : str #✅

    def __str__(self):
        return f'{self.intitule_métier}'

@dataclass
class Salarié(Profil_pro):
    #ancienneté_mois: int #✅
    date_in :int
    date_out:int 
    
    privé : bool #✅
    #annuel_brut : float #✅
    #prélèvement_source_pct : float #✅
    id_metier : int | None = None
    id_salarié: int | None = None
    
    id_compte : int | None = None
    annuel_brut: int| None = None
    

    #régime_fiscal : Fiscalité_salaires | None = field(default_factory=Fiscalité_salaires)
    
    @property
    def annuel_net(self) -> float:
        if self.privé == "Oui":
            taux = 0.83
        else:
            taux = 0.77

        return self.annuel_brut * taux

    @property
    def annuel_net_apres_ps(self) -> float:
        return self.annuel_net*(1-self.prélèvement_source_pct)
    @property
    def mensuel_brut(self) -> float:
        return self.annuel_brut/12
    @property
    def annuel_net_impot(self) -> float:
        return self.annuel_net - self.régime_fiscal.imposition_salaire(self.annuel_net)

    def __str__(self):
        str = f"{self.intitule_métier} depuis X "
        return str