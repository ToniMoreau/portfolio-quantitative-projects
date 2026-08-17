from core.gameState import GameState
from core.action import MoveAction, BuildAction, Action

import numpy as np

class SantoriniRules:
    #L'unique classe qui s'occupe de toutes les rêgles du Santorini, de sorte à ce que la classe Santorini ne soit qu'un exécutant.
    #Permet une grande flexibilité des rêgles
    def __init__(self):
        self.taille_plateau = (5,5,3)                           #lignes/colonnes/hauteur
        self.centre = [2,2]
        self.hauteur_victoire : int = 3                         #permet de changer les regles de condition de victoire par hauteur
        self.perimetre_deplacement : int = 1                    #permet de changer les regles de perimetre de deplacement
        self.perimetre_construction : int = 1                   #permet de changer les regles de perimetre de construction
        self.nb_workers_per_player :int = 2
        self.hauteur_max_building :int = self.hauteur_victoire+1#on peut construire sur la hauteur de victoire mais pas plus haut.
        self.nb_joueur = 2
        
        # Précalcule une fois pour toutes dans __init__
        self.voisinage = [(dl, dc) for dl in range(-1, 2) for dc in range(-1, 2) if not (dl == 0 and dc == 0)]
        self.voisins_valides = {
            (l, c): [(l+dl, c+dc) for dl, dc in self.voisinage 
                    if 0 <= l+dl < 5 and 0 <= c+dc < 5]
            for l in range(5) for c in range(5)
        }
        self.distance_du_centre = [
            [max(abs(self.centre[0] - i), abs(self.centre[1] - j)) for j in range(self.taille_plateau[1])]
            for i in range(self.taille_plateau[0])
        ]

        
    def __str__(self):
        pass
    ## METHODES UTILES
    def next_player(self, state : GameState) -> int:
        state.ordre_passage_index = (state.ordre_passage_index + 1) % len(state.ordre_passage_joueurs_liste)
        return state.ordre_passage_joueurs_liste[state.ordre_passage_index]
    
    def next_phase(self, state: GameState) -> str:
        idx = state.PHASES.index(state.current_phase)
        idx = (idx + 1) % len(state.PHASES)
        state.current_phase = state.PHASES[idx]
        return state.current_phase    
    
    ## Réinitialisation de l'état de jeu
    def initial_state(self, liste_joueurs_dans_l_ordre) -> GameState:
        state = GameState()
        
        state.PHASES = ["MOVE", "BUILD"]
        state.current_phase =""
        
        state.nb_joueurs = self.nb_joueur
        state.nb_workers_per_player = self.nb_workers_per_player
        
        worker_id = 0
        for player in range(state.nb_joueurs):
            state.workers_by_player[player] = []
            for _ in range(state.nb_workers_per_player):
                state.workers_by_player[player].append(worker_id) 
                state.worker_pos_by_worker[worker_id] = None
                worker_id += 1
                
        state.occupants = {}
                
        state.hauteur_plateau = [[0]*5 for _ in range(5)]
        state.cases_hauteurs_3 = []
        state.ordre_passage_index = 0
        state.ordre_passage_joueurs_liste = liste_joueurs_dans_l_ordre
        state.current_player = liste_joueurs_dans_l_ordre[state.ordre_passage_index]
        return state
    
    ## GESTION DES ACTIONS DU JEUX : autorisation et exécution des actions
    def legal_actions(self, state: GameState, player= None, phase = None, wkr = None): 
        is_state = phase is None
        if is_state : 
            phase_choix = state.current_phase
        else : phase_choix = phase

        if phase_choix == "PLACEMENT":
            actions = self.initial_legal_move(state)
        elif phase_choix== "MOVE":
            actions = self.legal_moves(state ,player, wkr=wkr)
        elif phase_choix == "BUILD":
            actions = self.legal_builds(state, player, wkr= wkr)
        else:
            raise ValueError("La phase choisi n'est pas définie")
        return actions
            
    def apply_action(self, state : GameState, action : MoveAction | BuildAction) -> GameState:
        if state.current_phase == "BUILD":
            try:
                if action.build_to_pos:
                    ligne_build, col_build  = action.build_to_pos 
                    state.hauteur_plateau[ligne_build][col_build] +=1
                    hauteur = state.hauteur_plateau[ligne_build][col_build]
                    if state.hauteur_plateau[ligne_build][col_build] ==3:
                        state.cases_hauteurs_3.append((ligne_build, col_build))
                    elif hauteur == 4:
                        state.cases_hauteurs_3.remove((ligne_build, col_build))
                    return state
                else: 
                    return state
            except Exception as e:
                print("Exception : ",e)
                return state
        else:
            try:
                if action.move_to_pos:
                    old_pos = state.worker_pos_by_worker[action.worker_id]
                    state.occupants.pop(old_pos, None)          # nettoie l'ancienne position
                    state.worker_pos_by_worker[action.worker_id] = action.move_to_pos
                    state.occupants[action.move_to_pos] = action.worker_id
                    return state
            except Exception as e:
                print("Exception : ", e)
                return state
   
    def initial_legal_move(self,state: GameState) -> list[Action]:
        player = state.current_player
        actions= []
        for worker in state.workers_by_player[player]:
            if state.worker_pos_by_worker[worker]:
                continue
            else:
                for ligne in range(self.taille_plateau[0]):
                    for col in range(self.taille_plateau[1]): 
                        is_occupied, _ = state.is_occupied((ligne,col))
                        if is_occupied:
                            continue
                        else:
                            action = MoveAction(worker, (ligne,col))
                            actions.append(action)
        return actions
    ### Fonctions qui fais les deux en meme temps ? move + build
    def legal_moves(self, state : GameState, player=None, wkr = None):
        player = player if player else state.current_player
        move_actions = []
        occupants = state.occupants  # référence locale, évite lookup attribut répété
        hauteur = state.hauteur_plateau
        workers = [wkr] if wkr is not None else state.workers_by_player[player]
        for worker in workers:
            pos = state.worker_pos_by_worker[worker]
            if pos is None:
                continue
            lw, cw = pos
            wh = hauteur[lw][cw]
            for l_move,c_move in self.voisins_valides[(lw,cw)]:
                if occupants.get((l_move, c_move)) is not None:
                    continue
                if hauteur[l_move][c_move] - wh > 1:
                    continue
                move_actions.append(MoveAction(worker, (l_move, c_move)))
        return move_actions      

    def legal_builds(self, state : GameState, player = None, wkr : int | None = None) -> list[BuildAction]:
        player = player if player else state.current_player
        build_actions = []
        workers = [wkr] if wkr is not None else state.workers_by_player[player]
        for worker in workers:
            pos = state.worker_pos_by_worker[worker]
            if pos is None:
                continue
            ligne_worker, col_worker = pos
            # voisinage 3x3 : distance garantie par le range, pas besoin de abs()
            for l_build, c_build in self.voisins_valides[(ligne_worker, col_worker)]:
                if state.occupants.get((l_build, c_build)) is not None:
                    continue                    
                if state.hauteur_plateau[l_build][c_build] == self.hauteur_max_building:
                    continue
                build_actions.append(BuildAction(worker, (l_build, c_build)))
        return build_actions
                             
    # GESTION DE LA FIN DE PARTIE : victoire, défaite
    def winner(self, state: GameState) -> int:
        for joueur_id in state.ordre_passage_joueurs_liste:
            if self.is_winner_by_height(state, joueur_id):
                return joueur_id
        # check blocage
        for joueur_id in state.ordre_passage_joueurs_liste:
            if self.is_looser(state, joueur_id):
                return 1 - joueur_id
        return None    
    def is_winner_by_height(self, state: GameState, joueur = None) -> bool:
            player = joueur if joueur else state.current_player
            for worker in state.workers_by_player[player]:
                pos = state.worker_pos_by_worker[worker]
                if pos is None:
                    continue
                i,j = pos
                if state.hauteur_plateau[i][j] == self.hauteur_victoire:
                    return True
            return False
            
    def is_looser(self, state: GameState, joueur = None) -> bool:
        joueur = joueur if joueur else state.current_player
        if not self.legal_moves(state, joueur):
            return True
        else: return False
                     
    def fin_partie(self, state: GameState) -> bool:
        return self.winner(state) is not None