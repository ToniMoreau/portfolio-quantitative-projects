import pygame

class UIState:
    def __init__(self):
        self.update_affichage = False
        self.plateau_owner = [] #qui a construit ou en dernier (gestion image des blocs)
        
        self.screen_width =0
        self.screen_height = 0
        self.taille_case = 150
        self.taille_pion = 20
        self.nb_cases = 5
        self.mouse_pos = None
        
        self.couleurs_joueurs = None
        self.selected_worker = None
        self.allowed_cells = None
        
        self.SABLE = 230, 212, 194
        self.title_font = pygame.font.SysFont(None,36)
        self.BLUE_SANTORINI = "#2F6FAF"

        self.match_infos = ""