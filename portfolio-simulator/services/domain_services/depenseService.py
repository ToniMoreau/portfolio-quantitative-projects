from repositories import DepenseRepository
from domain.entities import Depense
from domain.errors import (
    DepenseNotFoundError,
    IntegrityError,
    MissingColumnError,
)
from datetime import date

class DepenseService:
    def __init__(self, depense_repo: DepenseRepository):
        self.depense_repo = depense_repo
        self.natures_customs = ["", "Charges", "Autres"]
        self.depense_active_id = None
        
    def update_depense(self, depense_id, data, is_transaction : bool | None = None):
        try:
            depense = self.depense_repo.get_by_ID(depense_id)
            if depense is None:
                depense = self.depense_repo.create(data, is_transaction)
            else:
                self.depense_repo.update(depense.id, data)
            fresh_depense = self.depense_repo.get_by_ID(depense.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Depense") from e

        if fresh_depense is None:
            raise IntegrityError("Depense introuvable après update")
        return fresh_depense
    def set_depense_active(self, depense_id):
        self.depense_active_id = depense_id
    
    def get_by_criterias(self, dict_bys):
        try:
            return self.depense_repo.get_by_(dict_bys)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Depense") from e

    def get_by_scenario(self, id_scenario):
        try:
            depenses = self.depense_repo.get_by_({"ID SCENARIO": id_scenario})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Depense") from e

        if depenses is not None:
            return depenses
        return None
    def get_by_transaction(self, transaction_id):
        try:
            depense = self.depense_repo.get_by_({"ID TRANSACTION": transaction_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Depense") from e

        if depense is not None:
            return depense[0]
        return None

    def get_all_depense_from_cb(self, cbs_id : list[int], date_valide : date | None = None) -> list[Depense]:
        if isinstance(cbs_id, int):
            cbs_id = [cbs_id]

        depenses_totales = []
        for cb_id in cbs_id:
            try:
                depenses = self.depense_repo.get_by_({"ID COMPTE": cb_id})
            except KeyError as e:
                raise MissingColumnError(str(e), feuille="Depense") from e

            if not(depenses):
                pass
            elif date_valide is None:
                depenses_totales.extend(depenses)
            else:
                new_depenses = []
                for depense in depenses:
                    if (depense.frequence == "Annuel"):
                        if (depense.date_in.year < date_valide.year <= depense.date_out.year 
                            and date_valide.month == depense.date_in.month):
                            new_depenses.append(depense)
                    else:
                        if (depense.date_in <= date_valide <= depense.date_out):
                            new_depenses.append(depense)
                depenses_totales.extend(new_depenses)
        return depenses_totales
    
    def get_depense_by_id(self, depense_id):
        try:
            return self.depense_repo.get_by_ID(depense_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Depense") from e
    
    def delete_depense(self, depense_id):
        depense = self.depense_repo.get_by_ID(depense_id)
        if depense is None:
            raise DepenseNotFoundError(depense_id)
        try:
            self.depense_repo.delete(depense.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Depense") from e
    
    def get_loyers_from_scenario(self, scenario_id : int):
        try:
            return self.depense_repo.get_by_({"NATURE": "Loyers", "ID SCENARIO":scenario_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Depense") from e
    
    def all_userdepense_from_scenario(self, scenario_id) -> list[Depense]:
        try:
            depenses = self.depense_repo.get_by_({"ID SCENARIO": scenario_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Depense") from e

        if depenses is None:
            return []
        return depenses

    def montant_total_depense_from_scenario(self, scenario_id):
        depenses = self.all_userdepense_from_scenario(scenario_id)
        somme = 0
        for depense in depenses:
            somme += depense.montant
        return somme