from services.authService import AuthService
from services.profileService import ProfileService
from services.scenarioService import ScenarioService
from services import TransactionService, PatrimoineService
from services.domain_services import (FiscaliteService, 
                                      BanqueService, 
                                      MetierService, 
                                      CompteBancaireService, 
                                      CreditService, 
                                      RecetteService, 
                                      DepenseService, 
                                      InvestissementService,
                                    )
from repositories import Repositories

from services.navigator_service import NavigatorService
from domain.entities.fiscalité import Fiscalité

class AppContext:
    def __init__(self, repos : Repositories):
        self.repos = repos
        self.navigator = NavigatorService()
        
        self.auth_service = AuthService(repos)
        
        self.profile_Service = ProfileService(repos.user_repo)
        self.banque_service =  BanqueService(repos.banque_repo)
        self.scenario_service = ScenarioService(repos.scenario_repo)
        self.recette_service = RecetteService(repos.recette_repo)
        self.depense_service = DepenseService(repos.depense_repo)
        
        self.transaction_service = TransactionService(self.depense_service, self.recette_service)
        
        self.metier_service = MetierService(self.recette_service, self.depense_service,repos.metier_repo)
        self.cb_service =  CompteBancaireService(repos.compte_repo,self.recette_service,self.depense_service)
        self.credit_service = CreditService(repos.credit_repo, self.recette_service,self.depense_service)
        self.invest_service = InvestissementService(self.depense_service, self.recette_service, self.scenario_service, self.cb_service, repos.immo_repo, repos.stockoption_repo)
        
        self.patrimoine_service = PatrimoineService(self.credit_service, self.invest_service, self.cb_service, self.transaction_service, self.depense_service, self.recette_service, self.metier_service)
        
        self.fisca_service = FiscaliteService(Fiscalité())
        
        