from domain.entities import Scenario
from repositories import ScenarioRepository
from domain.errors import (
    ScenarioNotFoundError,
    IntegrityError,
    MissingColumnError,
    BusinessRuleError,
)
from datetime import date

    
class ScenarioService:
    def __init__(self, scenario_repo : ScenarioRepository):
        self.scenario_repo = scenario_repo
        self.scenario_actif_id : int | None = None
    
    def update_scenario(self, scenario_id, data):
        try:
            scenario = self.scenario_repo.get_by_ID(scenario_id)
            if scenario is None:
                scenario = self.scenario_repo.create(data)
            else:
                self.scenario_repo.update(scenario.id, data)
            fresh_scenario = self.scenario_repo.get_by_ID(scenario.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Scenario") from e

        if fresh_scenario is None:
            raise IntegrityError("Scénario introuvable après update")
        return fresh_scenario    
    
    def set_scenario_actif(self, new_actif_id : int | None = None):
        self.scenario_actif_id = new_actif_id
        
    def get_all_scenario_from_user(self, user_id) -> list[Scenario]:
        try:
            liste = self.scenario_repo.get_by_userID(user_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Scenario") from e

        if liste is None:
            return []
        return liste
    
    def get_scenario_by_id(self, scenario_id):
        try:
            return self.scenario_repo.get_by_ID(scenario_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Scenario") from e
    
    def delete_scenario(self, scenario_id):
        scenario = self.scenario_repo.get_by_ID(scenario_id)
        if scenario is None:
            raise ScenarioNotFoundError(scenario_id)
        try:
            self.scenario_repo.delete(scenario.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Scenario") from e
        
    def incremented_date_to_str(self, incr : int):
        if self.scenario_actif_id is None:
            raise BusinessRuleError("Aucun scénario actif sélectionné")
        scenario = self.get_scenario_by_id(self.scenario_actif_id)
        date = scenario.date_in
        total_months = date.year * 12 + (date.month - 1) + incr
        year = total_months // 12
        month = total_months % 12 + 1
        return f"{month}-{year}"