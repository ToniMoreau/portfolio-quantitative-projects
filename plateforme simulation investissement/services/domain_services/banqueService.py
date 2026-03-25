from repositories.repositories import BanqueRepository
from domain import Banque
class BanqueService:
    def __init__(self, banque_repo: BanqueRepository):
        self.banque_repo = banque_repo
        self.banque_active : Banque | None = None
    
    def update_banque(self, banque_id, data):
        if banque_id is None:
            banque = self.banque_repo.create(data)
        else:
            banque = self.banque_repo.get_by_ID(banque_id)
            
        if banque is None:
            banque = self.banque_repo.create(data)
        else : self.banque_repo.update(banque.id, data)
        
        fresh_banque = self.banque_repo.get_by_ID(banque.id)
        if fresh_banque is None:
            raise ValueError("Metier introuvable après update")
        return fresh_banque
    def get_all_banques(self):
        return self.banque_repo.get_all_banques()
    
    def get_banque_by_name(self, banque_name):
        return self.banque_repo.get_by_name(banque_name)
    
    def get_banque_by_id(self, banque_id):
        return self.banque_repo.get_by_ID(banque_id)
    def get_all_banque_names(self):
        return self.banque_repo.get_all_names().to_list()
    
    def set_banque_active(self, banque : Banque | None = None):
        self.banque_active = banque
        
    def delete_banque(self, banque : Banque):
        self.banque_repo.delete(banque.id)