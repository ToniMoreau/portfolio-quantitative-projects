
from repositories.banqueRepository import BanqueRepository
from repositories.compteBancaireRepository import CompteBancaireRepository
from repositories.userRepository import UserRepository
from repositories.metier_repository import MetierRepository
from repositories.InvestissementRepository import InvestissementRepository
from repositories.creditRepository import CreditcRepository
from repositories.scenarioRepository import ScenarioRepository
from repositories.recetteRepository import RecetteRepository
from repositories.depenseRepository import DepenseRepository

class Repositories:
    def __init__(self, excel_path):
        self.user_repo = UserRepository(excel_path)
        self.banque_repo = BanqueRepository(excel_path)
        self.compte_repo = CompteBancaireRepository(excel_path)
        self.metier_repo = MetierRepository(excel_path)
        self.project_repo = InvestissementRepository(excel_path)
        self.credit_repo = CreditcRepository(excel_path)
        self.scenario_repo = ScenarioRepository(excel_path)
        self.depense_repo = DepenseRepository(excel_path)
        self.recette_repo = RecetteRepository(excel_path)