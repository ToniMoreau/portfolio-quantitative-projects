from repositories.repositories import RecetteRepository
from domain import Recette
from datetime import date

class RecetteService:
    def __init__(self, recette_repo: RecetteRepository):
        self.recette_repo = recette_repo
        self.nature_revenus = ["Revenus", "Revenus locatifs", "Salaires"]

    def update_recette(self, recette_id, data, is_transaction : bool | None = None):
        recette = self.recette_repo.get_by_ID(recette_id)
        if recette is None:
            recette = self.recette_repo.create(data, is_transaction)
        else : self.recette_repo.update(recette.id, data)
        
        fresh_recette = self.recette_repo.get_by_ID(recette.id)
        if fresh_recette is None:
            raise ValueError("Metier introuvable après update")
        return fresh_recette
    
    def get_by_(self, dict_bys):
        return self.recette_repo.get_by_(dict_bys)
    def get_by_transaction(self, transaction_id):
        recette = self.recette_repo.get_by_({"ID TRANSACTION": transaction_id})
        if recette is not None:
            return recette[0]
        return None
    
    def get_recette_by_id(self, recette_id):
        return self.recette_repo.get_by_ID(recette_id)


    def delete_recette(self, recette : Recette):
        if recette is not None:
            self.recette_repo.delete(recette.id)
        
    def all_userrecette_from_scenario(self, scenario_id) -> list[Recette]:
        recettes = self.recette_repo.get_by_({"ID SCENARIO": scenario_id})
        if recettes is None:
            return []
        return recettes

    def montant_total_recette_from_scenario(self, scenario_id):
        recettes = self.all_userrecette_from_scenario(scenario_id)
        somme = 0
        for recette in recettes:
            somme += recette.montant
        return somme
    
    def get_all_recette_from_cb(self, cbs_id : list[int], date_valide : int = None) -> list[Recette]:
        if isinstance(cbs_id, int):
            cbs_id = [cbs_id]

        recettes_totales = []
        for cb_id in cbs_id:
            recettes = self.recette_repo.get_by_({"ID COMPTE": cb_id})
            if not(recettes):
                pass
            elif date_valide is None:
                recettes_totales.extend(recettes)
            else:
                new_recettes = []
                for recette in recettes:
                    if (recette.date_in <= date_valide <= recette.date_out):
                        new_recettes.append(recette)
                recettes_totales.extend(new_recettes)
        return recettes_totales

    def montant_entre_date(self, date_in : date, date_out : date, recettes : list[Recette]):
        date_in = date_in.month + date_in.year * 12
        date_out = date_out.month + date_out.year * 12
        
        etendu = date_out - date_in +1
        montant = 0
        for recette in recettes:
            recette_out = recette.date_out.month + recette.date_out.year * 12 
            recette_in = recette.date_in.month + recette.date_in.year * 12
            
            date = date_in
            while date <= date_out:
                if recette_in <= date <= recette_out:
                    montant += recette.montant
                date += 1
        return montant
                    
                    
                
                
        