from repositories import ImmobilierRepository, StockOptionsRepository
from datetime import date
from domain.entities import Investissement, Immobilier, StockOption
from domain.errors import (
    InvestissementNotFoundError,
    IntegrityError,
    MissingColumnError,
    ValidationError,
    ScenarioNotFoundError,
    SoldeInsuffisantError,
    NegativeAmountError,
    InvalidNatureError,
)
from .compteBancaireService import CompteBancaireService
from services.scenarioService import ScenarioService
from .depenseService import DepenseService
from .recetteService import RecetteService
from domain.enums import investType


class InvestissementService:
    def __init__(self, depense_service : DepenseService, recette_service : RecetteService,scenario_service :ScenarioService , cb_service : CompteBancaireService, immo_repo: ImmobilierRepository, stockoption_repo: StockOptionsRepository):
        self.repos : dict[str, StockOptionsRepository | ImmobilierRepository] = {
            investType.IMMO: immo_repo,
            investType.STOCK: stockoption_repo,
        }
        
        self.invest_actif_id = None
        self.cb_service = cb_service
        self.scenario_service = scenario_service
        self.depense_service = depense_service
        self.recette_service = recette_service
        
    # ---------- internal helpers ----------
    def _find_repo_and_invest(self, invest_id):
        """Return (repo, invest) for whichever repo holds invest_id, else (None, None)."""
        try:
            for repo in self.repos.values():
                invest = repo.get_by_ID(invest_id)
                if invest is not None:
                    return repo, invest
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Investissement") from e
        return None, None

    def _update(self, repo, invest_id, data):
        """Create-or-update against a specific repo, returning the fresh object."""
        try:
            invest = repo.get_by_ID(invest_id)
            if invest is None:
                invest = repo.create(data)
            else:
                repo.update(invest.id, data)
            fresh = repo.get_by_ID(invest.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Investissement") from e

        if fresh is None:
            raise IntegrityError("Investissement introuvable après update")
        return fresh

    # ---------- type-specific writes ----------
    def save_invest(self, invest_type: str, invest_id, data: dict):
        repo = self.repos.get(invest_type)
        if repo is None:
            raise InvalidNatureError(invest_type, tuple(self.repos.keys()))

        scenario_id = data.get("ID SCENARIO")
        scenario = self.scenario_service.get_scenario_by_id(scenario_id)
        if scenario is None:
            raise ScenarioNotFoundError(scenario_id)

        montant = (data.get("PRIX ACHAT") or data.get("MONTANT")) * (data.get("COMPTANT (%)") or 1)
        if montant is not None and montant < 0:
            raise NegativeAmountError(montant, champ="montant")

        cb_id = data.get("ID COMPTE")
        date_d = data.get("DATE ACHAT")

        resultat = self.cb_service.solde_from_cb(scenario.date_in, cb_id, date_d)
        print(resultat.solde)
        if montant is not None and montant > resultat.solde:
            raise SoldeInsuffisantError(compte_id=cb_id, solde=resultat.solde, montant_demande=montant)

        return self._update(repo, invest_id, data)    
    
    def update_investissement(self, invest_id, data):
        if invest_id is None:
            raise ValidationError("update_investissement requires a valid id; use update_immo/update_stock to create")
        repo, invest = self._find_repo_and_invest(invest_id)
        if repo is None:
            raise InvestissementNotFoundError(invest_id)
        try:
            repo.update(invest.id, data)
            fresh = repo.get_by_ID(invest.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Investissement") from e

        if fresh is None:
            raise IntegrityError("Investissement introuvable après update")
        return fresh    
    # ---------- generic reads ----------            
    def get_by_id(self, invest_id):
        _, invest = self._find_repo_and_invest(invest_id)
        return invest

    def get_by_scenario(self, scenario_id) -> list[StockOption | Immobilier]:
        result = []
        try:
            for repo in self.repos.values():
                found = repo.get_by_({"ID SCENARIO": scenario_id})
                if found:
                    result.extend(found)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Investissement") from e
        return result
    
    def get_immo_by_scenario(self, scenario_id : int) -> list[Immobilier]:
        result = []
        try:
            found = self.repos['immobilier'].get_by_({"ID SCENARIO": scenario_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Immobilier") from e
        if found:
            result.extend(found)
        return result
    
    def get_immo_actif_by_scenario(self, scenario_id) -> list[Immobilier]:
        result = []
        try:
            found = self.repos['immobilier'].get_by_({"ID SCENARIO": scenario_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Immobilier") from e
        if found:
            for immo in found:
                if immo.est_actif():
                    result.append(immo)
        return result
    
    def get_immo_by_locataire(self, loyer_id):
        try:
            return self.repos["immobilier"].get_by_({"ID LOYER" : loyer_id})[0]
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Immobilier") from e    
        
    
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
        if repo is None:
            raise InvestissementNotFoundError(invest_id)
        try:
            depenses_liees = self.depense_service.get_by_criterias({"ID SOURCE": invest_id}) or []
            recettes_liees = self.recette_service.get_by_criterias({"ID SOURCE": invest_id}) or []

            for depense in depenses_liees:
                self.depense_service.delete_depense(depense.id)
            for recette in recettes_liees:
                self.recette_service.delete_recette(recette.id)
                
            repo.delete(invest_id)
            
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Investissement") from e
        
    def next_invest_from_date(self, scenario_id, date: date):
        nearest = None
        for repo in self.repos.values():
            candidats = repo.get_by_({"ID SCENARIO": scenario_id})
            for candidat in candidats:
                if candidat.date_achat < date:
                    continue  # strictly before deletion date, irrelevant
                if nearest is None or candidat.date_achat < nearest.date_achat:
                    nearest = candidat
        return nearest            