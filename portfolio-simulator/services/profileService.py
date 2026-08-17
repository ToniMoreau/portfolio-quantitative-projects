from domain.entities.user import User
from domain.errors import (
    UtilisateurNotFoundError,
    IntegrityError,
    MissingColumnError,
)


class ProfileService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
        
    def update_profile(self, user_id, data):
        try:
            self.user_repository.update(user_id, data)
            fresh_user = self.user_repository.get_by_ID(user_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="User") from e

        if fresh_user is None:
            raise IntegrityError("Utilisateur introuvable après update")
        return fresh_user
    
    def get_infos(self,user : User):
        return user.public_infos()