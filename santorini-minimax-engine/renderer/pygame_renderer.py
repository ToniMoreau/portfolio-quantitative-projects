from core.gameState import GameState
from renderer.renderer import Renderer
from UI.objets import *
from UI import UIState, BoutonByCenter
import pygame
import os
from configs import BASE_PATH

class PyGameRenderer(Renderer):
    def __init__(self, screen : pygame.Surface):
        super().__init__()
        self.screen = screen
        self.ui_state = UIState()
        
        self.init_images()
        self.init_boutons()
    def fit_image_in_case(self, ui_state: UIState, image : pygame.surface.Surface, ratio):
        image_width = image.get_width()
        image_height = image.get_height()
        ratio_image = self.ui_state.taille_case * ratio / max(image_height, image_width)
        size_image = (int(image_width * ratio_image),int(image_height * ratio_image))
        return pygame.transform.scale(image, size_image) 
    
    def init_images(self):
        menu_background = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "menu_background.png")).convert()
        select_joueurs_background = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "select_joueurs.png")).convert()
        plateau_background = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "plateau_background.png")).convert()
        victoire_bleu_background =  pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "victoire_bleu_background.png")).convert()
        victoire_rouge_background =  pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "victoire_rouge_background.png")).convert()
        ouvrier_rouge = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "ouvrier_rouge.png")).convert_alpha()
        ouvrier_rouge = self.fit_image_in_case(self.ui_state, ouvrier_rouge, 0.6)
        ouvrier_bleu =pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "ouvrier_bleu.png")).convert_alpha()   
        ouvrier_bleu = self.fit_image_in_case(self.ui_state, ouvrier_bleu, 0.6)
        
        legal_move_bleu = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "legal_move_bleu.png")).convert_alpha()
        legal_move_bleu = self.fit_image_in_case(self.ui_state, legal_move_bleu,0.6)
        legal_move_rouge = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "legal_move_rouge.png")).convert_alpha()
        legal_move_rouge = self.fit_image_in_case(self.ui_state, legal_move_rouge, 0.6)
        
        legal_build_bleu = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "legal_build_bleu.png")).convert_alpha()
        legal_build_bleu = self.fit_image_in_case(self.ui_state, legal_build_bleu, 0.6)
        legal_build_rouge = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "legal_build_rouge.png")).convert_alpha()
        legal_build_rouge = self.fit_image_in_case(self.ui_state, legal_build_rouge, 0.6)
        
        bloc1_bleu = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "bloc1_bleu.png")).convert_alpha()
        bloc1_bleu = self.fit_image_in_case(self.ui_state, bloc1_bleu, 0.8)
        
        bloc2_bleu = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "bloc2_bleu.png")).convert_alpha()
        bloc2_bleu = self.fit_image_in_case(self.ui_state, bloc2_bleu, 0.8)

        bloc3_bleu = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "bloc3_bleu.png")).convert_alpha()
        bloc3_bleu = self.fit_image_in_case(self.ui_state, bloc3_bleu, 0.8)
        
        bloc4_bleu = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "bloc4_bleu.png")).convert_alpha()
        bloc4_bleu = self.fit_image_in_case(self.ui_state, bloc4_bleu, 0.8)
        
        bloc1_rouge = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "bloc1_rouge.png")).convert_alpha()
        bloc1_rouge = self.fit_image_in_case(self.ui_state, bloc1_rouge, 0.8)
        
        bloc2_rouge = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "bloc2_rouge.png")).convert_alpha()
        bloc2_rouge = self.fit_image_in_case(self.ui_state, bloc2_rouge, 0.8)

        bloc3_rouge = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "bloc3_rouge.png")).convert_alpha()
        bloc3_rouge = self.fit_image_in_case(self.ui_state, bloc3_rouge, 0.8)
        
        bloc4_rouge = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "bloc4_rouge.png")).convert_alpha()
        bloc4_rouge = self.fit_image_in_case(self.ui_state, bloc4_rouge, 0.8)

        quitter_btn = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "quitter_btn.png")).convert_alpha()
        quitter_btn = self.fit_image_in_case(self.ui_state, quitter_btn, 1)
        quitter_hovered = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "quitter_hovered.png")).convert_alpha()
        quitter_hovered = self.fit_image_in_case(self.ui_state, quitter_hovered,  1)
        quitter_clicked = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "quitter_clicked.png")).convert_alpha()
        quitter_clicked = self.fit_image_in_case(self.ui_state, quitter_clicked,  1)
        
        jouer_btn = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "jouer_menu_btn.png")).convert_alpha()
        jouer_btn = self.fit_image_in_case(self.ui_state, jouer_btn, 1.5)
        jouer_hovered = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "jouer_menu_hovered.png")).convert_alpha()
        jouer_hovered = self.fit_image_in_case(self.ui_state, jouer_hovered,  1.5)
        jouer_clicked = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "jouer_menu_clicked.png")).convert_alpha()
        jouer_clicked = self.fit_image_in_case(self.ui_state, jouer_clicked,  1.5)
        
        retour_btn = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "retour_btn.png")).convert_alpha()
        retour_btn = self.fit_image_in_case(self.ui_state, retour_btn, 1.2)
        retour_hovered = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "retour_hovered.png")).convert_alpha()
        retour_hovered = self.fit_image_in_case(self.ui_state, retour_hovered,  1.2)
        retour_clicked = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "retour_clicked.png")).convert_alpha()
        retour_clicked = self.fit_image_in_case(self.ui_state, retour_clicked, 1.2)
        
        quitter_plateau_btn = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "quitter_plateau_btn.png")).convert_alpha()
        quitter_plateau_btn = self.fit_image_in_case(self.ui_state, quitter_plateau_btn,  1.5)
        quitter_plateau_hovered = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "quitter_plateau_hovered.png")).convert_alpha()
        quitter_plateau_hovered = self.fit_image_in_case(self.ui_state, quitter_plateau_hovered,  1.5)
        quitter_plateau_clicked = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "quitter_plateau_clicked.png")).convert_alpha()
        quitter_plateau_clicked = self.fit_image_in_case(self.ui_state, quitter_plateau_clicked,  1.5)

        deux_joueurs_img = pygame.image.load(os.path.join(BASE_PATH, "assets", "images", "deux_joueurs_btn.png")).convert_alpha()
        deux_joueurs_img = self.fit_image_in_case(self.ui_state, deux_joueurs_img,  1.3)

        self.images = {"menu background" : menu_background,
                       "select joueurs background" : select_joueurs_background, 
                       "plateau background":plateau_background, 
                       "victoire bleu background" : victoire_bleu_background,
                       "victoire rouge background" : victoire_rouge_background,
                       "ouvrier bleu":ouvrier_bleu,
                       "ouvrier rouge": ouvrier_rouge,
                       "legal move bleu" :legal_move_bleu,
                       "legal move rouge": legal_move_rouge,
                       "legal build bleu" : legal_build_bleu, 
                       "legal build rouge": legal_build_rouge,
                       "bloc 1 bleu" : bloc1_bleu,
                       "bloc 2 bleu" : bloc2_bleu,
                       "bloc 3 bleu" : bloc3_bleu,
                       "bloc 4 bleu" : bloc4_bleu,
                       "bloc 1 rouge" : bloc1_rouge,
                       "bloc 2 rouge" : bloc2_rouge,
                       "bloc 3 rouge" : bloc3_rouge,
                       "bloc 4 rouge" : bloc4_rouge,
                       "quitter menu btn" : quitter_btn,
                       "jouer menu btn" : jouer_btn,
                       "retour btn" : retour_btn,
                       "quitter plateau btn" : quitter_plateau_btn,
                       "quitter menu hovered" : quitter_hovered,
                       "jouer menu hovered" : jouer_hovered,
                       "retour hovered" : retour_hovered,
                       "quitter plateau hovered" : quitter_plateau_hovered,
                       "quitter menu clicked" : quitter_clicked,
                       "jouer menu clicked" : jouer_clicked,
                       "retour clicked" : retour_clicked,
                       "quitter plateau clicked" : quitter_plateau_clicked,
                       "deux joueurs btn" : deux_joueurs_img
                       }
        
    def init_boutons(self):
        self.ui_state.screen_height = self.screen.get_height()
        self.ui_state.screen_width = self.screen.get_width()
        
        
        #Bouton MENU:
        self.Mjouer_btn = BoutonImage(880, 400, callback=lambda : "SELECT_NB_JOUEURS", image=self.images["jouer menu btn"])
        self.Mquitter_btn = BoutonImage(1010, 1040, callback=lambda : "QUITTER",image= self.images["quitter menu btn"])
        self.MTournoi_btn = BoutonByCenter(880, 700,200,100, "Tournois", callback=lambda: "TOURNOI GENERATIF", FONT = self.ui_state.title_font)
        
        #Bouton SELECTION JOUEURS
        self.deux_joueurs_btn = BoutonImage(800, 185, callback=lambda : "DEUX_JOUEURS",image=self.images["deux joueurs btn"])
        self.sj_retour_btn = BoutonImage(1100, 385,callback=lambda : "MENU", image=self.images["retour btn"])
        
        #Bouton IN GAME
        self.pions_btn = []
        self.GFin_btn = BoutonImage(1795, 1010,callback=lambda : "FIN",image= self.images["quitter plateau btn"])
        self.active_case_buttons = [] 
        
        #Bouton victoire
        self.win_retour_btn = BoutonImage(100, 100,callback=lambda : "MENU", image=self.images["retour btn"])

    def render(self, state: GameState):
        phase = state.current_phase

        if phase == "MENU":
            return self.render_menu_principal(state)
        elif phase == "SELECT_NB_JOUEURS":
            return self.render_jouer_clicked(state)
        elif phase == "PLACEMENT":
            return self.render_placement(state)
        elif phase == "MOVE":
            return self.render_move(state)
        elif phase == "BUILD":
            return self.render_build(state)
        elif phase == "FIN":
            return self.render_fin(state)
        else:
            return self.render_menu_principal(state)  
    def render_fin(self, state : GameState):        
        couleur_victoire = "bleu" if state.winner == 0 else "rouge"
        background = self.images[f"victoire {couleur_victoire} background"]
        self.screen.blit(background, (0,0))
        
        self.win_retour_btn.draw(self.screen)
        
        return [self.win_retour_btn]
    def render_move(self, state : GameState):
        
        self.render_plateau(state)
        
        text_menu_surface = self.ui_state.title_font.render("Phase de Move !", True, (0, 0, 0))
        text_menu_rect = text_menu_surface.get_rect(center = (self.ui_state.screen_width* 0.75, self.ui_state.screen_height * 0.1) )
        
        self.screen.blit(text_menu_surface, text_menu_rect)
        
        current_joueur_surface = self.ui_state.title_font.render(f"Au tour de : {state.current_player} !", True, (0,0,0))
        current_joueur_rect = current_joueur_surface.get_rect(center = (self.ui_state.screen_width* 0.75, self.ui_state.screen_height* 0.2) )
        self.screen.blit(current_joueur_surface, current_joueur_rect)
        
        match_info_surface = self.ui_state.title_font.render(self.ui_state.match_infos, True, (0,0,0))
        match_info_rect = match_info_surface.get_rect(center=(self.ui_state.screen_width * 0.75, self.ui_state.screen_height * 0.3))
        self.screen.blit(match_info_surface, match_info_rect)
        
        self.GFin_btn.draw(self.screen)
        
        boutons = self.active_case_buttons.copy()
        boutons.extend(self.pions_btn)
        boutons.append(self.GFin_btn)
    
        return boutons
    def render_placement(self, state: GameState):
        
        self.render_plateau(state)
        
        text_menu_surface = self.ui_state.title_font.render("Phase de Placement !", True, (0, 0, 0))
        text_menu_rect = text_menu_surface.get_rect(center = (self.ui_state.screen_width* 0.75, self.ui_state.screen_height * 0.1) )
        
        self.screen.blit(text_menu_surface, text_menu_rect)
        
        current_joueur_surface = self.ui_state.title_font.render(f"Au tour de : {state.current_player} !", True, (0,0,0))
        current_joueur_rect = current_joueur_surface.get_rect(center = (self.ui_state.screen_width* 0.75, self.ui_state.screen_height* 0.2) )
        self.screen.blit(current_joueur_surface, current_joueur_rect)
        
        match_info_surface = self.ui_state.title_font.render(self.ui_state.match_infos, True, (0,0,0))
        match_info_rect = match_info_surface.get_rect(center=(self.ui_state.screen_width * 0.75, self.ui_state.screen_height * 0.3))
        self.screen.blit(match_info_surface, match_info_rect)

        self.GFin_btn.draw(self.screen)
        
        boutons = self.active_case_buttons.copy()
        boutons.extend(self.pions_btn)
        boutons.append(self.GFin_btn)
    
        return boutons
    def render_build(self, state : GameState):
        
        self.render_plateau(state)
        
        text_menu_surface = self.ui_state.title_font.render("Phase de Build !", True, (0, 0, 0))
        text_menu_rect = text_menu_surface.get_rect(center = (self.ui_state.screen_width* 0.75, self.ui_state.screen_height * 0.1) )
        
        self.screen.blit(text_menu_surface, text_menu_rect)
        
        current_joueur_surface = self.ui_state.title_font.render(f"Au tour de : {state.current_player} !", True, (0,0,0))
        current_joueur_rect = current_joueur_surface.get_rect(center = (self.ui_state.screen_width* 0.75, self.ui_state.screen_height* 0.2) )
        self.screen.blit(current_joueur_surface, current_joueur_rect)
        
        match_info_surface = self.ui_state.title_font.render(self.ui_state.match_infos, True, (0,0,0))
        match_info_rect = match_info_surface.get_rect(center=(self.ui_state.screen_width * 0.75, self.ui_state.screen_height * 0.3))
        self.screen.blit(match_info_surface, match_info_rect)

        self.GFin_btn.draw(self.screen)
        
        boutons = self.active_case_buttons.copy()
        boutons.extend(self.pions_btn)
        boutons.append(self.GFin_btn)
    
        return boutons

    def render_plateau(self, state : GameState):
        image = self.images['plateau background']
        self.screen.blit(image, (0,0))

        dessiner_plateau(self.screen, self.ui_state)
        dessiner_construction(self.screen,state, self.ui_state, self.images)
        

        if self.active_case_buttons:
            for case in self.active_case_buttons:
                case.draw(self.screen)
            
        for pion_btn in self.pions_btn:
            pion_btn.draw(self.screen)
        
        #dessiner_pions(self.screen,state ,self.ui_state)
        
        return []
    
    def render_menu_principal(self,state : GameState):
        image = self.images["menu background"]
        self.screen.blit(image, (0,0))
        
        self.MTournoi_btn.draw(self.screen)
        self.Mjouer_btn.draw(self.screen)
        
        self.Mquitter_btn.draw(self.screen)
        
        return [self.Mjouer_btn, self.Mquitter_btn, self.MTournoi_btn]      
    
    def render_jouer_clicked(self, state : GameState):
        image = self.images["select joueurs background"]
        self.screen.blit(image, (0,0))
        
        self.deux_joueurs_btn.draw(self.screen)
        self.sj_retour_btn.draw(self.screen)
        
        return [self.deux_joueurs_btn, self.sj_retour_btn]      
        
    def update_active_case_buttons(self, allowed_cells, state : GameState):
        self.active_case_buttons = cases_bouttons_autorisees(allowed_cells, state, self.ui_state, self.images)
    
    def update_pion_buttons(self, state: GameState):
        self.pions_btn = pions_boutons(state, self.ui_state, self.images)