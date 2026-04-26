from repositories.repositories import InvestissementRepository
from datetime import date

class InvestissementService:
    def __init__(self, invest_repo: InvestissementRepository):
        self.invest_repo = invest_repo
        self.nature = ["Boursier", "Immobilier"]        
        
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
        
        
    
