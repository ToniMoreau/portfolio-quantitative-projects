from joueurs.player import Player

class ConsoleHumanPlayer(Player):
    def __init__(self, nom, prenom):
        super().__init__(nom, prenom)
        self.nom = nom
        self.prenom = prenom
    
    def choose_action(self, actions):
        for  i, action in enumerate(actions):
            print(f"action {i} : {action}")
            
        while True:
            try:
                choix = int(input("choisissez parmis les actions possibles : "))
                
                if 0<=choix< len(actions):
                    return actions[choix]
                else:
                    print(f"erreur de saisie : tapper un numéro entre 0 et {len(actions)}")
            except ValueError:
                print("Entre un nombre valide")
