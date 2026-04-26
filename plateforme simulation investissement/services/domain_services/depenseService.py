from repositories.repositories import DepenseRepository
from domain import Depense
from datetime import date
class DepenseService:
    def __init__(self, depense_repo: DepenseRepository):
        self.depense_repo = depense_repo
        self.natures = ["", "Charges", "Crédit", "Autres"]
        
        
    def update_depense(self, depense_id, data, is_transaction : bool | None = None):
        depense = self.depense_repo.get_by_ID(depense_id)
        if depense is None:
            depense = self.depense_repo.create(data, is_transaction)
        else : self.depense_repo.update(depense.id, data)
        
        fresh_depense = self.depense_repo.get_by_ID(depense.id)
        if fresh_depense is None:
            raise ValueError("Metier introuvable après update")
        return fresh_depense
    
    def get_by_transaction(self, transaction_id):
        depense = self.depense_repo.get_by_({"ID TRANSACTION": transaction_id})
        if depense is not None:
            return depense[0]
        return None

    def get_all_depense_from_cb(self, cbs_id : list[int], date_valide : date | None = None) -> list[Depense]:
        if isinstance(cbs_id, int):
            cbs_id = [cbs_id]

        depenses_totales = []
        for cb_id in cbs_id:
            depenses = self.depense_repo.get_by_({"ID COMPTE": cb_id})
            if not(depenses):
                pass
            elif date_valide is None:
                depenses_totales.extend(depenses)
            else:
                new_depenses = []
                for depense in depenses:
                    print(type(depense.date_in))
                    if (depense.date_in <= date_valide <= depense.date_out):
                        new_depenses.append(depense)
                depenses_totales.extend(new_depenses)
        return depenses_totales
    
    def get_depense_by_id(self, depense_id):
        return self.depense_repo.get_by_ID(depense_id)
    
    def delete_depense(self, depense : Depense):
        if depense is not None:
            self.depense_repo.delete(depense.id)
        
    def all_userdepense_from_scenario(self, scenario_id) -> list[Depense]:
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
        