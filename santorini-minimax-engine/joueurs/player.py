

class Player:
    def __init__(self, nom : str, prenom : str):
        self.nom = nom
        self.prenom = prenom
        self.id_player = None
    def __str__(self):
        return self.prenom + self.nom
    
    def choose_action(self, actions):
        pass