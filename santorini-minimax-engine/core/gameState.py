import copy
class GameState:
    def __init__(self):
        self.hauteur_plateau = [] #représentation matricielle de la hauteur du plateau (case par case)
        self.cumsum_plateau = 0
        self.workers_by_player   = {} # id player rend liste de workers
        
        self.worker_pos_by_worker = {} # id worker rend position worker (ligne, col)
        self.occupants ={}             #dictionnaire : emplacement rend None si pas dedans, ou un ouvrier si un ouvrier est sur l'emplacement
        self.current_player = None
        self.winner = None
        
        self.nb_joueurs = 0              #initialisé à 0, géré par le Santorini Rules.
        self.nb_workers_per_player = 0   #initialisé à 0, géré par le Santorini Rules.
        
        self.PHASES = ["MOVE", "BUILD"]  #Grande phases de jeu, hormis la phase de placement initial
        self.current_phase = ""          #Permet le placement initial lorsque mis sur ""
        self.ordre_passage_joueurs_liste  = []
        self.ordre_passage_index : int = 0
    
        self.cases_hauteurs_3 = []
    #Méthodes utiles
    def is_occupied(self, cell):
        occupant = self.occupants.get(cell, None)
        if occupant is not None:
            return (True, occupant)
        return (False, None)

    def cumsum_hauteurs(self):
        self.cumsum_plateau = sum([sum(ligne) for ligne in self.hauteur_plateau])
        print(self.cumsum_plateau)