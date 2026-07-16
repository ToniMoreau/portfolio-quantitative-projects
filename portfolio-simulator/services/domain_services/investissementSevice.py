from repositories.repositories import InvestissementRepository
from datetime import date
from domain import Investissement
class InvestissementService:
    def __init__(self, invest_repo: InvestissementRepository):
        self.invest_repo = invest_repo
        self.invest_actif = None
        self.nature = ["Conso", "Immobilier"]        
        
    def update_investissement(self, invest_id, data):
        invest = self.invest_repo.get_by_ID(invest_id)
        if invest is None:
            invest = self.invest_repo.create(data)
        else : self.invest_repo.update(invest.id, data)
        
        fresh_invest = self.invest_repo.get_by_ID(invest.id)
        if fresh_invest is None:
            raise ValueError("Investissement introuvable après update")
        return fresh_invest
    def get_by_id(self, invest_id):
        invest = self.invest_repo.get_by_ID(invest_id)
        return invest
    
    def set_invest_actif(self,invest : Investissement):
        self.invest_actif = invest
        
    
