from repositories import ImmobilierRepository, StockOptionsRepository
from datetime import date
from domain import Investissement, Immobilier, StockOption


class InvestissementService:
    def __init__(self, immo_repo: ImmobilierRepository, stockoption_repo: StockOptionsRepository):
        self.repos : dict[str, StockOptionsRepository | ImmobilierRepository] = {
            "immobilier": immo_repo,
            "stock": stockoption_repo,
        }
        self.invest_actif_id = None

    # ---------- internal helpers ----------
    def _find_repo_and_invest(self, invest_id):
        """Return (repo, invest) for whichever repo holds invest_id, else (None, None)."""
        for repo in self.repos.values():
            invest = repo.get_by_ID(invest_id)
            if invest is not None:
                return repo, invest
        return None, None

    def _update(self, repo, invest_id, data):
        """Create-or-update against a specific repo, returning the fresh object."""
        invest = repo.get_by_ID(invest_id)
        if invest is None:
            invest = repo.create(data)
        else:
            repo.update(invest.id, data)

        fresh = repo.get_by_ID(invest.id)
        if fresh is None:
            raise ValueError("Investissement introuvable après update")
        return fresh

    # ---------- type-specific writes ----------
    def update_immo(self, invest_id, data):
        return self._update(self.repos["immobilier"], invest_id, data)

    def update_stock(self, invest_id, data):
        return self._update(self.repos["stock"], invest_id, data)
    
    def update_investissement(self, invest_id, data):
        if invest_id is None:
            raise ValueError("update_investissement requires a valid id; use update_immo/update_stock to create")
        repo, invest = self._find_repo_and_invest(invest_id)
        if repo is None:
            raise ValueError("Investissement introuvable")
        repo.update(invest.id, data)
        fresh = repo.get_by_ID(invest.id)
        if fresh is None:
            raise ValueError("Investissement introuvable après update")
        return fresh    
    # ---------- generic reads ----------            
    def get_by_id(self, invest_id):
        _, invest = self._find_repo_and_invest(invest_id)
        return invest

    def get_by_scenario(self, scenario_id) -> list[StockOption | Immobilier]:
        result = []
        for repo in self.repos.values():
            found = repo.get_by_({"ID SCENARIO": scenario_id})
            if found:
                result.extend(found)
        return result
    
    def get_immo_by_scenario(self, scenario_id : int) -> list[Immobilier]:
        result = []
        found = self.repos['immobilier'].get_by_({"ID SCENARIO": scenario_id})
        if found:
            result.extend(found)
        return result
    
    def get_immo_actif_by_scenario(self, scenario_id) -> list[Immobilier]:
        result = []
        found = self.repos['immobilier'].get_by_({"ID SCENARIO": scenario_id})
        if found:
            for immo in found:
                if immo.est_actif():
                    result.append(immo)
        return result
    
    def get_immo_by_locataire(self, loyer_id):
        return self.repos["immobilier"].get_by_({"ID LOYER" : loyer_id})[0]
    
    def vacant_immos_by_scenario(self, scenario_id) -> list[Immobilier]:
        immos = self.get_immo_by_scenario(scenario_id)
        vacants = []
        for immo in immos:
            print(immo.id_loyer, immo.is_occupied(), immo.est_actif())
            if not(immo.is_occupied()) and immo.est_actif():
                vacants.append(immo)
        return vacants
    
        
    
    def invest_actif(self): 
        if self.invest_actif_id is None:
            return None
        _, invest = self._find_repo_and_invest(self.invest_actif_id)
        return invest

    def set_invest_actif(self, invest_id: int):
        self.invest_actif_id = invest_id

    # ---------- generic delete ----------
    def delete_invest(self, invest_id):
        repo, invest = self._find_repo_and_invest(invest_id)
        if repo is not None:
            repo.delete(invest_id)