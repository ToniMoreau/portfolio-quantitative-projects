

from domain import Scenario
from repositories import ScenarioRepository
from datetime import date
class ScenarioService:
    def __init__(self, scenario_repo : ScenarioRepository):
        self.scenario_repo = scenario_repo
        scenario_actif : Scenario | None = None
    
    def update_scenario(self, scenario_id, data):
        scenario = self.scenario_repo.get_by_ID(scenario_id)
        if scenario is None:
            scenario = self.scenario_repo.create(data)
        print("scenario ==", scenario)
        fresh_scenario = self.scenario_repo.update(scenario.id, data)
        if fresh_scenario is None:
            raise ValueError("Scénario introuvable après update")
        return fresh_scenario
    
    def set_scenario_actif(self, new_actif : Scenario | None = None):
        self.scenario_actif = new_actif
        
    def get_all_scenario_from_user(self, user_id) -> list[Scenario]:
        liste = self.scenario_repo.get_by_userID(user_id)
        if liste is None:
            return []
        return liste
    
    def get_scenario_by_id(self, scenario_id):
        return self.scenario_repo.get_by_ID(scenario_id)
    
    def delete_scenario(self, scenario : Scenario):
        self.scenario_repo.delete(scenario.id)        
        
    def incremented_date_to_str(self, incr : int):
        date = self.scenario_actif.date_in
        total_months = date.year * 12 + (date.month - 1) + incr
        year = total_months // 12
        month = total_months % 12 + 1
        return f"{month}-{year}"