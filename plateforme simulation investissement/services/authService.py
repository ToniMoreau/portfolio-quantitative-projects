from repositories import Repositories

class AuthService:
    def __init__(self, repos : Repositories):
        self.repos = repos
        
    def login(self, username, password):
        user = self.repos.user_repo.get_by_username(username)                
        if not user:
            raise ValueError("Utilisateur inexistant")
        if user.password != password:
            raise ValueError("Mot de passe incorrect")
        return user
    
    def register(self, username, password):
        
        if self.repos.user_repo.get_by_username(username):
            raise ValueError("Utilisateur déjà existant")
        
        user = {
            "username" : username, 
            "password" : password, 
        }
        
        user = self.repos.user_repo.create(user)
        
        return user