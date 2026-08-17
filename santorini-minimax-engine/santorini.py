
from core import GameState
from core import SantoriniRules
from joueurs import PyGameHumanPlayer, ConsoleHumanPlayer, IAPlayer, Player
from renderer import Renderer

import numpy as np

class Santorini:
    #Classe d'exécution du jeu.
    #Le jeu gère très bien l'exécution, peut import le type de rendu selectionné : (PyGame, terminal,..)
    def __init__(self, liste_players : list[Player], renderer : Renderer ):
        self.rules = SantoriniRules()   #initialisation des rêgles du jeu.
        self.renderer = renderer        #initialisation du rendu choisi (PyGame, terminal,..)
        
        self.players : dict[int, Player] = {}   #liste des joueurs
        self.init_players(liste_players)
    
    
    def __str__(self):
        pass
    
    def init_players(self,liste_players : list[Player]):
        self.players = {}
        for num, player in enumerate(liste_players):
            self.players[num] = player
            player.id_player = num
        
    def lancer_jeu(self):
        #méthode qu gère la boucle de la partie
        print("Début de partie !")
        
        ##MISE EN PLACE :
            #mélange de l'ordre de passage
        ordre_tour = list(range(len(self.players)))
        np.random.shuffle(ordre_tour)
        
            #initialisation de l'état de jeu (tout à zéro)
        state = self.rules.initial_state(ordre_tour)
            #raccourcis instance
        renderer = self.renderer
        players = self.players
        
        ##PHASE DE PLACEMENT :
        print("Phase de placement : ")
        renderer.render(state) #visuel initial sans placement
        
        state.current_phase = "PLACEMENT"
        state = self.phase_placement(state)
        print("Placement effectué.")
        
        renderer.render(state) #visuel après placement
        
        #PHASES PRINCIPALES DU JEU : boucle principale
        print("La partie peut commencer ! ")
        while not self.rules.fin_partie(state): #tant que la partie n'est pas finie (aucun vainqueur, plusieurs survivants)
            p_id = state.current_player                         #id joueur courant
            player : Player= players[p_id]                      #selection du joueur selon l'id courant
            print(f"C'est à {player} de jouer !\n")
            for phase in state.PHASES:
                #Gère les deux phases du tour pour chaque joueur, chacun son tour. Permet l'inversion des phases selon les rêgles.
                print(state.PHASES)
                state.current_phase = phase                     #récup la phase actuelle
                  
                actions = self.rules.legal_actions(state)       #récup les actions possibles du joueur courant
                
                if not actions:
                    break
                
                action = player.choose_action(actions)          #Méthode qui permet au joueur de choisir l'action qu'il veut, peut importe le format (PyGame, Terminal,...)
                state = self.rules.apply_action(state, action)  #Exécution de l'action.
                
                renderer.render(state)                          #visuel de la phase actuelle terminée 

            state.current_player = self.rules.next_player(state)#Gestion du changement de joueur
            #FIN BOUCLE WHILE
        #SORTIE DE BOUCLE == WINNER
        winner = self.rules.winner(state)
        print(f"{players[winner]} à gagné")
                
        
    def initial_tour(self, state: GameState) -> GameState:
        #Méthode utilitaire pour la phase de placement, gère les actions possible au placement, et l'exécution également
        joueur : Player = self.players[state.current_player]
        actions = self.rules.legal_actions(state)           #liste des actions autorisées
        action = joueur.choose_action(actions)              #selection par le joueur de l'action à réaliser
        state = self.rules.apply_action(state, action)      #exécution de l'action choisie
        state.current_player = self.rules.next_player(state)#changement de joueur
        return state        
        
    def phase_placement(self,state : GameState) -> GameState:
        #Méthode qui gère le placement initiale. 
        #Gestion des placements initiaux des ouvriers, en alternant un ouvrier de chaque joueur à la fois. Plus équitable
        for _ in range(state.nb_workers_per_player):
            #en gros, tout le monde place son premier ouvrier puis sont deuxième. C'est ce que permet cette double boucle.
            for _ in state.ordre_passage_joueurs_liste:
                state = self.initial_tour(state)
        return state
    
            