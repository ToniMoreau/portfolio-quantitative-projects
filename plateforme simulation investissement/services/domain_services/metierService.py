from repositories.repositories import MetierRepository
from domain.profil_pro import Salarié
class MetierService:
    def __init__(self, metier_repo: MetierRepository):
        self.metier_repo = metier_repo
        self.metier_actif :Salarié | None= None
    def update_metier(self, metier_id, data):
        metier = self.metier_repo.get_by_ID(metier_ID=metier_id)
        if metier is None:
            metier = self.metier_repo.create(data)
        else : self.metier_repo.update(metier.id_metier, data)
        
        fresh_metier = self.metier_repo.get_by_ID(metier.id_metier)
        if fresh_metier is None:
            raise ValueError("Metier introuvable après update")
        return fresh_metier
    
    def get_by_(self, dict_bys):
        return self.metier_repo.get_by_(dict_bys)
    
    def get_metier_by_id(self,metier_id):
        return self.metier_repo.get_by_ID(metier_id)
    
    def get_metier_by_scenario(self, scenario_id):
        return self.metier_repo.get_by_({"ID SCENARIO": scenario_id})
    
    def revenu_net_mensuel_from_brut_annuel(self,metier_id):
        metier = self.metier_repo.get_by_ID(metier_id)
        
        if metier.privé.capitalize() == "OUI":
            taux = 0.83
        else :
            taux = 0.77
        net_mensuel = metier.annuel_brut/12 * taux
        return net_mensuel
    def set_metier_actif(self, metier):
        self.metier_actif = metier
    def delete(self, metier_id):
        self.metier_repo.delete(metier_id)