import pygame
import sys
import os

import numpy as np

from core import GameState, SantoriniRules
from renderer import PyGameRenderer
from joueurs import PyGameHumanPlayer, IAPlayer, IAPlayerDCenterDHauteur
from santorini import Santorini
from core import MoveAction, BuildAction
import cProfile
from time import perf_counter
from data.database import *
from tournoi import *

def handle_buttons(buttons, event):
    """
    Parcourt les boutons affichés et retourne le callback déclenché si un bouton est activé.
    """
    if not buttons:
        return None

    for btn in buttons:
        result = btn.handle_event(event)
        if result is not None:
            return result
    return None

def main():
    connection = initialise_database() #database init
    pygame.init()

    screen = pygame.display.set_mode((1920, 1080), flags=pygame.NOFRAME)    
    pygame.display.set_caption("Santorini")
    clock = pygame.time.Clock()

    renderer = PyGameRenderer(screen)
    rules = SantoriniRules()

    santorini = Santorini([], renderer)
    santorini.rules = rules
    tournoi = GestionTournoi(connection ,santorini.rules) #connecter a la database pour save les stats
    recalculer_scores(connection, tournoi.calculer_score)

    state = GameState()
    state.current_phase = "MENU"
    
    tournoi_generatif = False
    
    selected_worker = None
    allowed_cells = []
    running = True
    displayed_buttons = []
    renderer.ui_state.plateau_owner = [[None for j in range(santorini.rules.taille_plateau[1])] for i in range(santorini.rules.taille_plateau[0])]
    ia_1 = None
    ia_2 = None
    chosen_actions = []
    while running:
        chosen_actions = []
        screen.fill(renderer.ui_state.SABLE)
        # 1) RENDER SELON PHASE
        displayed_buttons = renderer.render(state) or []
       
        #tour IA:
        #if state.current_phase in ["PLACEMENT", "MOVE", "BUILD"]
        player = None if state.current_player is None else santorini.players[state.current_player]        

        if isinstance(player, IAPlayer):
            selected_worker = None
            allowed_cells = []
            renderer.ui_state.update_affichage = True
            ##-----------PROFILING/STATS CALLS---------------#
            import pstats

            """profiler = cProfile.Profile()
            profiler.enable()"""

            start_time = perf_counter()
            ##-----------END PROFILING/STATS CALLS---------------#
            #-----------FUNCTIONAL CALL ONLY--------------#
            chosen_actions, total_noeuds = player.alpha_beta(state)  # ton appel existant
            #-----------END FUNCTIONAL CALL---------------#
            ##-----------PROFILING/STATS CALLS---------------#
            end_time = perf_counter()
            player.temps_par_tour.append(end_time - start_time)
            player.noeuds_par_tour.append(total_noeuds)
            """print("total noeud du tour : ", total_noeuds)
            profiler.disable()
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # top 20 fonctions les plus coûteuses"""
            ##-----------END PROFILING/STATS CALLS---------------#
                
        # 2) EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEMOTION:
                renderer.ui_state.mouse_pos = event.pos

            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                callback_result = handle_buttons(displayed_buttons, event)
                if callback_result == "QUITTER":
                    running = False

                elif callback_result == "MENU":
                    renderer.ui_state.update_affichage = False
                    state = GameState()
                    ia_1, ia_2 = None, None
                    state.current_phase = "MENU"

                elif callback_result == "SELECT_NB_JOUEURS":
                    state.current_phase = "SELECT_NB_JOUEURS"

                elif callback_result == "DEUX_JOUEURS":
                    renderer.ui_state.update_affichage = True
                    ia_1 = PyGameHumanPlayer("Toni", "Moreau")
                    ia_2 = PyGameHumanPlayer("Thomas","Ide")
                    #tournoi.initialiser_pool()
                    #ia_1 = tournoi.pool[0]
                    #ia_2 = tournoi.pool[1]
                    santorini.init_players([ia_1,ia_2])
                    ordre_tour = list(range(len(santorini.players)))
                    np.random.shuffle(ordre_tour)
                    state = santorini.rules.initial_state(ordre_tour)
                    state.current_phase = "PLACEMENT"
                    selected_worker = state.workers_by_player[state.current_player][0]
                    if isinstance(state.current_player, IAPlayer):
                        allowed_cells = []
                    else:
                        actions = santorini.rules.legal_actions(state, wkr = selected_worker)
                        allowed_cells = [a.move_to_pos for a in actions]
                    renderer.update_pion_buttons(state)#✅
                    renderer.update_active_case_buttons(allowed_cells, state)#✅  
                    
                elif callback_result == "FIN":
                    renderer.ui_state.update_affichage = False
                    state = GameState()
                    tournoi_generatif = False
                    state.current_phase = "MENU"

                elif callback_result == "TOURNOI GENERATIF":
                    renderer.ui_state.update_affichage = True
                    tournoi_generatif = True
                    tournoi.initialiser_pool()
                    ia_1,ia_2 = tournoi.matchmaking()
                    renderer.ui_state.match_infos = f"[{tournoi.cpt_matchs}eme] {ia_1.id_database} D{ia_1.profondeur} (B) elo : {ia_1.elo} vs {ia_2.id_database} D{ia_2.profondeur} (R) elo : {ia_2.elo}"
                    santorini.init_players([ia_1, ia_2])
                    
                    ordre_tour = list(range(len(santorini.players)))
                    np.random.shuffle(ordre_tour)
                    state = santorini.rules.initial_state(ordre_tour)
                    state.current_phase = "PLACEMENT"
                       
                elif isinstance(callback_result, int) and callback_result in state.workers_by_player[state.current_player]:
                    renderer.ui_state.update_affichage = True
                    if (state.current_phase == state.PHASES[0]):
                        selected_worker = callback_result
                    elif (state.current_phase == state.PHASES[-1]):
                        selected_worker=renderer.ui_state.selected_worker 
                    actions = santorini.rules.legal_actions(state, wkr = selected_worker)
                    if state.current_phase == "MOVE":
                        allowed_cells = [a.move_to_pos for a in actions]
                    else:
                        allowed_cells = [a.build_to_pos for a in actions]                    
                elif isinstance(callback_result, tuple):
                    renderer.ui_state.update_affichage = True
                    # Cas des cases du plateau : callback_result = (ligne, col)
                    cell_choice = callback_result
                    actions = santorini.rules.legal_actions(state, wkr = renderer.ui_state.selected_worker)
        
                    chosen_actions = []
                    for action in actions:
                        if isinstance(action, BuildAction):
                            cell_test = action.build_to_pos
                        elif isinstance(action, MoveAction):
                            cell_test = action.move_to_pos
                        if cell_test == cell_choice:
                            chosen_actions = [action]
                            break
        
        for action in chosen_actions:
            if isinstance(action, MoveAction) and state.current_phase == "PLACEMENT":
                selected_worker = renderer.ui_state.selected_worker

                #----EXECUTION DE L'ACTION----------#
                state = santorini.rules.apply_action(state, action) #✅
                #----CHANGEMENT DE JOUEUR-----#
                state.current_player = santorini.rules.next_player(state)#✅
            
                #----VERIFICATION SI TOUS LES OUVRIERS SONT SUR LE PLATEAU
                all_placed = True #✅
                for worker_id, worker_pos in state.worker_pos_by_worker.items():#✅
                    if worker_pos is None:#✅
                        all_placed = False#✅
                        if worker_id in state.workers_by_player[state.current_player]:#✅
                            selected_worker =worker_id
                            allowed_cells = []
                if all_placed:#✅
                    #----CHANGEMENT DE PHASE SI TOUS LES JOUEURS SONT PLACES----#
                    state.current_phase = state.PHASES[0]#✅
                    allowed_cells = []#✅
                    ##---SELECTION DU WORKER POUR LA PHASE SUIVANTE---##
                    selected_worker = None#✅
            elif isinstance(action, MoveAction) and state.current_phase == "MOVE":                
                state = santorini.rules.apply_action(state, action)
                if state.current_phase == state.PHASES[-1]:
                    state.current_player = santorini.rules.next_player(state)
                    selected_worker = None
                allowed_cells = []
                state.current_phase = santorini.rules.next_phase(state)
            elif isinstance(action, BuildAction) and state.current_phase == "BUILD":
                state = santorini.rules.apply_action(state, action)
                state.cumsum_plateau +=1
                renderer.ui_state.plateau_owner[action.build_to_pos[0]][action.build_to_pos[1]] = state.current_player
                if state.current_phase == state.PHASES[-1]:
                    state.current_player = santorini.rules.next_player(state)
                    selected_worker = None
                allowed_cells = []
                state.current_phase = santorini.rules.next_phase(state)
            
            player = None if state.current_player is None else santorini.players[state.current_player]        
            
            if isinstance(player, PyGameHumanPlayer):
                if state.current_phase == state.PHASES[0]:
                    selected_worker = state.workers_by_player[state.current_player][0]#✅
                elif state.current_phase == state.PHASES[-1]:
                    selected_worker = renderer.ui_state.selected_worker
                actions = santorini.rules.legal_actions(state, wkr = selected_worker)#✅
                if state.current_phase == "BUILD":
                    allowed_cells = [a.build_to_pos for a in actions]#✅
                else:
                    allowed_cells = [a.move_to_pos for a in actions]#✅
            
            if state.current_phase in state.PHASES:
                winner = santorini.rules.winner(state)
                if winner is not None:
                    renderer.ui_state.update_affichage = False
                    #print(f"Le joueur {winner} a gagné !")
                    state.current_phase = "FIN"
                    state.winner = winner
                    state.cumsum_plateau =0
                    state.current_player = None
                    
                    if tournoi_generatif:   
                        tournoi.enregistrer_match(ia_1, ia_2, winner == ia_1.id_player) 
                        ia_1.temps_par_tour = []
                        ia_2.temps_par_tour = []
                        ia_1.noeuds_par_tour = []
                        ia_2.noeuds_par_tour = []
                        if tournoi.cpt_matchs !=0 or tournoi.cpt_matchs ==0:
                            ia_1,ia_2 = tournoi.matchmaking()
                            renderer.ui_state.match_infos = f"[{tournoi.cpt_matchs}eme] {ia_1.id_database} D{ia_1.profondeur} (B) elo : {ia_1.elo} vs {ia_2.id_database} D{ia_2.profondeur} (R) elo : {ia_2.elo}"

                            santorini.init_players([ia_1, ia_2])
                            
                            ordre_tour = list(range(len(santorini.players)))
                            np.random.shuffle(ordre_tour)
                            state = santorini.rules.initial_state(ordre_tour)
                            state.current_phase = "PLACEMENT"
                    break
        
        if renderer.ui_state.update_affichage:          
            renderer.ui_state.selected_worker = selected_worker#✅
            renderer.ui_state.allowed_cells = allowed_cells #✅
            renderer.update_pion_buttons(state)#✅
            renderer.update_active_case_buttons(allowed_cells, state)#✅  
            renderer.ui_state.update_affichage = False
               
        # 3) REDESSIN FINAL
        screen.fill(renderer.ui_state.SABLE)
        renderer.render(state)
        
        # 4) FIN DE PARTIE

        pygame.display.flip()
        clock.tick(60)
    
    connection.close()

    pygame.quit() 
    sys.exit()

if __name__ == "__main__":
    main()
    
