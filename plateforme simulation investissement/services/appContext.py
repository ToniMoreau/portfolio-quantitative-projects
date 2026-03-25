from services.authService import AuthService
from services.profileService import ProfileService
from services.scenarioService import ScenarioService
from services.domain_services import FiscaliteService, BanqueService, MetierService, CompteBancaireService, CreditService, RecetteService, DepenseService

from repositories.repositories import Repositories

from domain.fiscalité import Fiscalité

class AppContext:
    def __init__(self, repos : Repositories):
        self.repos = repos
        
        self.auth_service = AuthService(repos)
        
        self.profile_Service = ProfileService(repos.user_repo)
        self.metier_service = MetierService(repos.metier_repo)
        self.banque_service =  BanqueService(repos.banque_repo)
        self.cb_service =  CompteBancaireService(repos.compte_repo, repos.recette_repo, repos.depense_repo)
        self.credit_service = CreditService(repos.credit_repo, repos.recette_repo)
        self.scenario_service = ScenarioService(repos.scenario_repo)
        self.recette_service = RecetteService(repos.recette_repo)
        self.depense_service = DepenseService(repos.depense_repo)
        
        self.fisca_service = FiscaliteService(Fiscalité())
        
        