from repositories.repositories import CompteBancaireRepository, RecetteRepository, DepenseRepository
from domain import Banque, CompteBancaire

class CompteBancaireService:
    def __init__(self, cb_repo: CompteBancaireRepository, recette_repo : RecetteRepository, depense_repo : DepenseRepository):
        self.cb_repo = cb_repo
        self.depense_repo = depense_repo
        self.recette_repo = recette_repo
        self.cb_actif = None
    
    def update_cb(self, cb_id, data):
        cb = self.cb_repo.get_by_ID(cb_id)
        if cb is None:
            cb = self.cb_repo.create(data)

        else :self.cb_repo.update(cb.id, data)
        fresh_cb = self.cb_repo.get_by_ID(cb.id)
        if fresh_cb is None:
            raise ValueError("Metier introuvable après update")
        return fresh_cb
    
    def set_cb_actif(self, new_actif : CompteBancaire | None = None):
        self.cb_actif = new_actif
        
    def get_all_cb_from_user(self, user_id) -> list[CompteBancaire]:
        liste = self.cb_repo.get_by_userID(user_id)
        if liste is None:
            return []
        return liste
    
    def get_cb_by_id(self, cb_id):
        return self.cb_repo.get_by_ID(cb_id)
    
    def delete_cb(self, cb : CompteBancaire):
        self.cb_repo.delete(cb.id)
        
    def all_userCB_from_banque(self, user_id, banque_id):
        cb_user = self.get_all_cb_from_user(user_id)
        from_this_banque = []
        for cb in cb_user:
            if cb.id_banque == banque_id:
                from_this_banque.append(cb)
                
        return from_this_banque
    
    def all_userCB_from_(self, dict_str_id : dict[str,int]):
        return self.cb_repo.get_by_(dict_str_id)
        
    def all_userCB_from_scenario(self, scenario_id):
        cbs = self.cb_repo.get_by_({"ID SCENARIO": scenario_id})
        return cbs

    def montant_total_cb_from_scenario(self, scenario_id):
        cbs = self.all_userCB_from_scenario(scenario_id)
        somme = 0
        for cb in cbs:
            somme += self.solde_from_cb(cb.id)
        return somme
    
    def solde_from_cb(self, cb_id, date_valide : int = None):
        depenses = self.depense_repo.get_by_({"ID COMPTE": cb_id})
        recettes = self.recette_repo.get_by_({"ID COMPTE": cb_id})
        solde = 0 
        if date_valide is None:
            date_valide = 0
            
        for recette in recettes:
            date_out = recette.date_out 
            date_in = recette.date_in
            if date_valide > date_out:
                etendu =date_out - date_in +1
            elif date_valide < date_in:
                etendu = 0
            else:
                etendu = date_valide - date_in +1
            total_recette = recette.montant * etendu
            solde += total_recette
            
        for depense in depenses:
            date_out = depense.date_out 
            date_in = depense.date_in
            if date_valide > date_out:
                etendu =date_out - date_in +1
            elif date_valide < date_in:
                etendu = 0
            else:
                etendu = date_valide - date_in +1
            total_depense = depense.montant * etendu
            solde -= total_depense
            
        return solde
        