from repositories.repositories import DepenseRepository
from domain import Depense

class DepenseService:
    def __init__(self, depense_repo: DepenseRepository):
        self.depense_repo = depense_repo
    
    def update_depense(self, depense_id, data):
        depense = self.depense_repo.get_by_ID(depense_id)
        if depense is None:
            depense = self.depense_repo.create(data)
        else : self.depense_repo.update(depense.id, data)
        
        fresh_depense = self.depense_repo.get_by_ID(depense.id)
        if fresh_depense is None:
            raise ValueError("Metier introuvable après update")
        return fresh_depense
        
    def get_all_depense_from_cb(self, cb_id : int, date_valide : int = None):
        depenses = self.depense_repo.get_by_({"ID COMPTE": cb_id})
        if not(depenses):
            return []
        if date_valide is None:
            return depenses
        
        new_depenses = []
        for depense in depenses:
            if (depense.date_in <= date_valide <= depense.date_out):
                new_depenses.append(depense)
        return new_depenses
    
    def get_depense_by_id(self, depense_id):
        return self.depense_repo.get_by_ID(depense_id)
    
    def delete_depense(self, depense : Depense):
        self.depense_repo.delete(depense.id)
        
    
    def all_userdepense_from_scenario(self, scenario_id):
        depenses = self.depense_repo.get_by_({"ID SCENARIO": scenario_id})
        if depenses is None:
            return []
        return depenses

    def montant_total_depense_from_scenario(self, scenario_id):
        depenses = self.all_userdepense_from_scenario(scenario_id)
        somme = 0
        for depense in depenses:
            somme += depense.montant
        return somme
        