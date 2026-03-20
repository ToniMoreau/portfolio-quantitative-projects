

from domain.user import User

class Session:
    def __init__(self):
        self.current_user : User | None = None
        
    def login(self, user):
        self.current_user = user
        
    def logout(self):
        self.current_user = None
    
    def is_authenticated(self):
        return self.current_user is not None