from core.gameState import GameState
from renderer.renderer import Renderer


class ConsoleRenderer:
    def __init__(self):
        pass
    
    def render(self, state : GameState):
        print("\nPlateau : ")
        hauteur_plateau = state.hauteur_plateau
        nb_lignes = len(hauteur_plateau)
        nb_colonne = len(hauteur_plateau[0])
        
        plateau = []
        for ligne in range(nb_lignes):
            print(ligne)
            ligne_plateau = []
            for col in range(nb_colonne):
                is_occupied, occupant = state.is_occupied((ligne, col))
                ligne_plateau.append([[ligne,col],hauteur_plateau[ligne][col], [is_occupied, occupant] ])
            plateau.append(ligne_plateau)
        
        for ligne in plateau:
            print(f"{ligne}\n")
        
        print(f"joueur courant : {state.current_player}")
        return plateau

                
        