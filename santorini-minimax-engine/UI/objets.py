import pygame
from .ui_state import UIState
from .bouton import BoutonByCorner, BoutonRond, BoutonImage
from core import GameState
from configs import BASE_PATH
import os


def cases_bouttons_autorisees(cells, state : GameState, ui_state : UIState, images):
    boutons = []
    plr_color = {
        0 : "bleu",
        1 : "rouge"
    }
    phases = {
        "PLACEMENT" : "move",
        "MOVE" : "move",
        "BUILD" : "build"
    }
    curr_plr_clr = plr_color[state.current_player]
    curr_phase = state.current_phase
    move_build_txt = phases[curr_phase]
    
    taille_case = ui_state.taille_case
    decalage_x = 153
    decalage_y = 427
    if cells:
        for i, j in cells:
            btn = BoutonImage(
                decalage_y + taille_case * j + taille_case/2,
                decalage_x + taille_case * i+taille_case/2,
                callback=lambda a=i, b= j: (a,b),
                image=images[f"legal {move_build_txt} {curr_plr_clr}"]
            )
            boutons.append(btn)

    return boutons
    
def pions_boutons(state : GameState, ui_state, images):
    boutons = []

    ouvrier_bleu = images["ouvrier bleu"]
    ouvrier_rouge = images["ouvrier rouge"]
    IMAGES = {
        0: ouvrier_bleu,
        1: ouvrier_rouge,
    }

    worker_to_player = {}
    for player_id, workers in state.workers_by_player.items():
        for w in workers:
            worker_to_player[w] = player_id

    for worker_id, pos in state.worker_pos_by_worker.items():
        if pos is None:
            continue

        left, top, width, height = get_case_from_pion_pos(pos, ui_state)
        center_x = left + width / 2
        center_y = top + height / 2

        player_id = worker_to_player[worker_id]
        image = IMAGES.get(player_id, ouvrier_bleu )

        btn = BoutonImage(
            center_x=center_x,
            center_y=center_y,
            callback=lambda wid=worker_id: wid,
            image=image
        )
        boutons.append(btn)

    return boutons

def dessiner_plateau(surface, ui_state : UIState):
    taille_case = ui_state.taille_case
    decalage_x = 153
    decalage_y = 427

    for i in range(ui_state.nb_cases):
        for j in range(ui_state.nb_cases):
            pygame.draw.rect(surface, (0,0,0),(decalage_y + taille_case*j,decalage_x + taille_case*i,taille_case,taille_case), 2, 2)

def dessiner_pions(surface : pygame.surface.Surface, state : GameState, ui_state : UIState):
    COLORS = {
        0: (255, 0, 0),
        1: (0, 0, 255),
    }

    for worker_id, pos in state.worker_pos_by_worker.items():
        if pos is None:
            continue

        # trouver le joueur du worker
        for player_id, workers in state.workers_by_player.items():
            if worker_id in workers:
                color = COLORS.get(player_id, (0,0,0))
                player = player_id
                break

        left, top, width, height = get_case_from_pion_pos(pos, ui_state)

        rect = pygame.draw.circle(
            surface,
            color,
            (left + width/2, top + height/2),
            ui_state.taille_pion
        )   
        if worker_id == ui_state.selected_worker:
            pygame.draw.circle(
            surface,
            "green",
            (left + width/2, top + height/2),
            ui_state.taille_pion,
            width=3,
        )   
        text = f"J{player}W{worker_id}"
        text_surf = ui_state.title_font.render(text, True, (0,0,0))
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

         
def dessiner_construction(surface : pygame.surface.Surface, state : GameState, ui_state : UIState, images):   
    ligne,col = [len(state.hauteur_plateau),len(state.hauteur_plateau[0])]
    plr_clr = {
        0 : "bleu",
        1 : "rouge"
    }
    for i in range(ligne):
        for j in range(col):
            hauteur_cases = state.hauteur_plateau[i][j]
            if hauteur_cases >0:
                owner_case = ui_state.plateau_owner[i][j]
                couleur = plr_clr[owner_case]

                left, top, width, height = get_case_from_pion_pos((i,j), ui_state)
                image  = BoutonImage(center_x= left + width/2, center_y= top + height / 2,image=images[f"bloc {hauteur_cases} {couleur}"], callback=None)    
                image.draw(surface)            
                """text_surface = ui_state.title_font.render(f"{state.hauteur_plateau[i][j]}",False, (0,0,0))
                text_rect = text_surface.get_rect(center = image.center)
                surface.blit(text_surface, text_rect)"""
        
def get_case_from_pion_pos(pion_pose, ui_state: UIState):
    taille_case = ui_state.taille_case
    decalage_x = 153
    decalage_y = 427

    ligne, col = pion_pose
    left = decalage_y + col * taille_case
    top = decalage_x + ligne * taille_case
    return (left, top, taille_case, taille_case)
    if case_pion : 
        for action in actions:
            case = get_case_from_pion_pos(action.move_to_pos, ui_state)
            pygame.draw.rect(surface, (0,255,0), case, width=5)
            
