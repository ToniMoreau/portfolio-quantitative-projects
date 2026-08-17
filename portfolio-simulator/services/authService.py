from repositories import Repositories
from domain.errors import (
    InvalidCredentialsError,
    EntiteDejaExistanteError,
    MissingColumnError,
)

class AuthService:
    def __init__(self, repos : Repositories):
        self.repos = repos
        
    def login(self, username, password):
        try:
            user = self.repos.user_repo.get_by_username(username)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="User") from e

        if not user or user.password != password:
            raise InvalidCredentialsError()
        return user
    
    def register(self, username, password):
        try:
            existing = self.repos.user_repo.get_by_username(username)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="User") from e

        if existing:
            raise EntiteDejaExistanteError("Utilisateur", username)
        
        user = {
            "username" : username, 
            "password" : password, 
        }
        
        try:
            user = self.repos.user_repo.create(user)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="User") from e
        
        return user