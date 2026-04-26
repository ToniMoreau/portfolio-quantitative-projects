
from domain.fiscalité import Fiscalité
from domain.profil_pro import Salarié
from domain.scenario import Scenario
class FiscaliteService:
    def __init__(self, fiscalite : Fiscalité):
        self.fiscalite = fiscalite
        
    def imposition_salaire(self,salaire_annuel_net) -> float:
        salaire_imposable = salaire_annuel_net * 0.9 # 10% abbatement frais pro
        seuil_taux_dict = {11497 : 0,  29315 - 11497 : 11, 83823 - 29315  : 30,  salaire_imposable - 83823  : 41}
        i = 0
        impot = 0
        seuil_liste = list(seuil_taux_dict.keys())
        reste = salaire_imposable
        seuil = 0
        while seuil != reste:
            seuil = test = seuil_liste[i]

            if reste - seuil <= 0:
                seuil = reste
            else:
                reste -= seuil
            impot += (seuil * seuil_taux_dict[test]/100)
            i+=1
        print(impot)
        return impot
    
    @property
    def annuel_net_impot(self, métier : Salarié) -> float:
        return métier.annuel_net - self.imposition_salaire(métier.annuel_net)
    def annuel_net_from_brut(self,annuel_brut : float, privé : str) -> float:
        if privé.lower() == "oui":
            taux = 0.83
        else:
            taux = 0.77

        return annuel_brut * taux
    
    def imposition_from_scenario(self, scenario : Scenario):
        pass


