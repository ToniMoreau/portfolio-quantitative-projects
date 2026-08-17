
from repositories import BanqueRepository
from repositories import CompteBancaireRepository
from repositories import UserRepository
from repositories import MetierRepository
from repositories import CreditRepository
from repositories import ScenarioRepository
from repositories import RecetteRepository
from repositories import DepenseRepository
from repositories import ImmobilierRepository, StockOptionsRepository

class Repositories:
    def __init__(self, excel_path):
        self.user_repo = UserRepository(excel_path)
        self.banque_repo = BanqueRepository(excel_path)
        self.compte_repo = CompteBancaireRepository(excel_path)
        self.metier_repo = MetierRepository(excel_path)
        self.credit_repo = CreditRepository(excel_path)
        self.scenario_repo = ScenarioRepository(excel_path)
        self.depense_repo = DepenseRepository(excel_path)
        self.recette_repo = RecetteRepository(excel_path)
        self.immo_repo = ImmobilierRepository(excel_path)
        self.stockoption_repo = StockOptionsRepository(excel_path)