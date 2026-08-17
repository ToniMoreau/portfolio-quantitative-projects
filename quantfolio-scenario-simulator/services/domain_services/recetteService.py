from repositories import RecetteRepository
from domain.entities import Recette
from domain.errors import (
    RecetteNotFoundError,
    IntegrityError,
    MissingColumnError,
)
from datetime import date

class RecetteService:
    def __init__(self, recette_repo: RecetteRepository):
        self.recette_repo = recette_repo
        self.natures_customs = ["","Revenus Divers", "Autres", "Dons/Cadeaux"]

    def update_recette(self, recette_id, data, is_transaction : bool | None = None):
        try:
            recette = self.recette_repo.get_by_ID(recette_id)
            if recette is None:
                recette = self.recette_repo.create(data, is_transaction)
            else:
                self.recette_repo.update(recette.id, data)
            fresh_recette = self.recette_repo.get_by_ID(recette.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e

        if fresh_recette is None:
            raise IntegrityError("Recette introuvable après update")
        return fresh_recette
    
    def get_by_criterias(self, dict_bys):
        try:
            return self.recette_repo.get_by_(dict_bys)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e

    def get_by_transaction(self, transaction_id):
        try:
            recette = self.recette_repo.get_by_({"ID TRANSACTION": transaction_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e

        if recette is not None:
            return recette[0]
        return None
    
    def get_recette_by_id(self, recette_id):
        try:
            return self.recette_repo.get_by_ID(recette_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e


    def delete_recette(self, recette_id):
        recette = self.recette_repo.get_by_ID(recette_id)
        if recette is None:
            raise RecetteNotFoundError(recette_id)
        try:
            self.recette_repo.delete(recette.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e
        
    def all_userrecette_from_scenario(self, scenario_id) -> list[Recette]:
        try:
            recettes = self.recette_repo.get_by_({"ID SCENARIO": scenario_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e

        if recettes is None:
            return []
        return recettes

    def montant_total_recette_from_scenario(self, scenario_id):
        recettes = self.all_userrecette_from_scenario(scenario_id)
        somme = 0
        for recette in recettes:
            somme += recette.montant
        return somme
    
    def get_all_recette_from_cb(self, cbs_id : list[int], date_valide : date = None) -> list[Recette]:
        if isinstance(cbs_id, int):
            cbs_id = [cbs_id]

        recettes_totales = []
        for cb_id in cbs_id:
            try:
                recettes = self.recette_repo.get_by_({"ID COMPTE": cb_id})
            except KeyError as e:
                raise MissingColumnError(str(e), feuille="Recette") from e

            if not(recettes):
                pass
            elif date_valide is None:
                recettes_totales.extend(recettes)
            else:
                new_recettes = []
                for recette in recettes:
                    if (recette.frequence == "Annuel"):
                        if (recette.date_in.year < date_valide.year <= recette.date_out.year 
                            and date_valide.month == recette.date_in.month):
                            new_recettes.append(recette)
                    else:
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
                    
    def get_locataires_from_scenario(self, scenario_id : int):
        try:
            return self.recette_repo.get_by_({"NATURE": "Locataires", "ID SCENARIO":scenario_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e
    
    def get_locataires_from_immo(self, id_immo : int):
        try:
            return self.recette_repo.get_by_({"NATURE" : "Locataires", "ID SOURCE" : id_immo})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e
    
    def get_locataire_from_date(self, id_immo : int, date : date):
        locataires = []
        for locataire in self.get_locataires_from_immo(id_immo):
            if locataire.date_in <= date <= locataire.date_out:
                return locataire
        return None
    
    def is_immo_free_between_(self,immo_id, date_in : date, date_out : date):

        locataires = self.get_locataires_from_immo(immo_id) or []
        
        for locataires in locataires:
            if (locataires.date_in <= date_in < locataires.date_out
                or locataires.date_in < date_out <= locataires.date_out
                or date_in <= locataires.date_in <= date_out):
                    return False
        return True
    
    def update_location_from_vente_immo(self, immo_id: int, date_vente :date):
        demenagent_apres_vente = self.get_moved_out_after_date(immo_id, date_vente) or []
        emmenagent_apres_vente = self.get_moved_in_after_date(immo_id, date_vente)
        
        for locataire in demenagent_apres_vente:
            if locataire.id in {l.id for l in emmenagent_apres_vente}:                
                self.delete_recette(locataire.id)
            else:
                self.update_recette(locataire.id, {"DATE OUT" : date_vente})
    
    def get_moved_out_after_date(self, immo_id : int, date_seuil : date) -> list[Recette]:
        try:
            locataires = self.recette_repo.get_by_({"NATURE" : "Locataires", "ID SOURCE" : immo_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e
        
        result = []
        for locataire in locataires:
            if locataire.date_out >= date_seuil:
                result.append(locataire)
        return result

    def get_moved_in_after_date(self, immo_id : int, date_seuil  :date) -> list[Recette]:
        try:
            locataires = self.recette_repo.get_by_({"NATURE" : "Locataires", "ID SOURCE" : immo_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette") from e
        
        result = []
        for locataire in locataires:
            if locataire.date_in >= date_seuil:
                result.append(locataire)
        return result