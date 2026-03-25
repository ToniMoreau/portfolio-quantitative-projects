from repositories.repositories import RecetteRepository
from domain import Recette

class RecetteService:
    def __init__(self, recette_repo: RecetteRepository):
        self.recette_repo = recette_repo
    
    def update_recette(self, recette_id, data):
        recette = self.recette_repo.get_by_ID(recette_id)
        if recette is None:
            recette = self.recette_repo.create(data)
        else : self.recette_repo.update(recette.id, data)
        
        fresh_recette = self.recette_repo.get_by_ID(recette.id)
        if fresh_recette is None:
            raise ValueError("Metier introuvable après update")
        return fresh_recette
        
    
    def get_recette_by_id(self, recette_id):
        return self.recette_repo.get_by_ID(recette_id)
    
    def delete_recette(self, recette : Recette):
        self.recette_repo.delete(recette.id)
        
    
    def all_userrecette_from_scenario(self, scenario_id):
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
    
    def get_all_recette_from_cb(self, cb_id : int, date_valide : int = None):
        recettes = self.recette_repo.get_by_({"ID COMPTE": cb_id})
        print(recettes)
        if not(recettes):
            return []
        if date_valide is None:
            return recettes
        new_recettes = []
        for recette in recettes:
            if (recette.date_in <= date_valide <= recette.date_out):
                new_recettes.append(recette)
        return new_recettes
