from domain.user import User


class ProfileService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
        
    def update_profile(self, user_id, data):
        self.user_repository.update(user_id, data)
        fresh_user = self.user_repository.get_by_ID(user_id)
        if fresh_user is None:
            raise ValueError("Utilisateur introuvable après update")
        return fresh_user
    
    def get_infos(self,user : User):
        return user.public_infos()
    
    