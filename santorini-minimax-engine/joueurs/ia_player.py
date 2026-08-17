from joueurs.player import Player
from core import GameState, SantoriniRules
from math import inf,sqrt
from time import sleep, perf_counter
from core import MoveAction, BuildAction
import random

count_ok = False
class IAPlayer(Player):
    def __init__(self, nom, prenom, database_tuple):
        super().__init__(nom, prenom)
        self.id_player = None
        self.rules : SantoriniRules = None
        self.eval_function = None
        #self.depth =depth
        
        self.temps_par_tour = []
        self.temps_moyen_parties = []
        self.noeuds_par_tour = []
        self.noeuds_moyen_parties = []
        self.matchs = []
        self.database_tuple = database_tuple

    def utility(self, state : GameState):
        winner = self.rules.winner(state)
        if winner is not None: #y'a un gagnant
            if winner == self.id_player:
                return 10000
            return -10000     
        
    def evaluate_diff_hauteur(self, state : GameState):
        score_diff_hauteur = 0
        for wkr in state.workers_by_player[self.id_player]:
            l_wkr, c_wkr = state.worker_pos_by_worker[wkr]
            hauteur_wkr = state.hauteur_plateau[l_wkr][c_wkr]
            score_diff_hauteur += hauteur_wkr #gestion du score_diff_hauteur

        for wkr in state.workers_by_player[1 - self.id_player]:
            l_wkr, c_wkr = state.worker_pos_by_worker[wkr]
            hauteur_adv = state.hauteur_plateau[l_wkr][c_wkr]
            score_diff_hauteur -= state.hauteur_plateau[l_wkr][c_wkr]

        return score_diff_hauteur

    def evaluate_montabilité(self, state : GameState):
        score_montée = 0
        voisinage = self.rules.voisinage
        hauteurs_plateau = state.hauteur_plateau
        hauteur_plateau = self.rules.taille_plateau[2]
        workers_by_player = state.workers_by_player
        worker_pos_by_worker = state.worker_pos_by_worker
        
        for wkr in workers_by_player[self.id_player]:
            l_wkr, c_wkr = worker_pos_by_worker[wkr]
            hauteur_wkr = hauteur_plateau[l_wkr][c_wkr]
            score_wkr =0
            has_good_voisin = False #voisin ou on peut monter
            minime_descente = -hauteur_plateau
            minime_montée = hauteur_plateau
            for dl,dc in voisinage:
                lm, cm = (l_wkr + dl, c_wkr+dc)
                if not (0 <= lm < 5 and 0 <= cm < 5):
                    continue

                hauteur_voisine = hauteurs_plateau[lm][cm]
                diff_voisine = hauteur_wkr - hauteur_voisine
                minime_montée = min(minime_montée, diff_voisine)
                if diff_voisine ==1:
                    has_good_voisin = True
                    score_wkr += hauteur_wkr * 5
                    break
                elif diff_voisine <=0:               
                    minime_descente = max(diff_voisine, minime_descente)
            
            if not has_good_voisin:
                score_wkr += minime_descente * 5
            if minime_montée >1:
                score_wkr -= 1000
            
            score_montée += score_wkr
            
        for wkr in workers_by_player[1 - self.id_player]:
            l_wkr, c_wkr = worker_pos_by_worker[wkr]
            hauteur_adv = hauteurs_plateau[l_wkr][c_wkr]
            score_wadv =0
            has_good_voisin = False #voisin ou on peut monter
            minime_descente = -hauteur_plateau
            minime_montée = hauteur_plateau
            for dl,dc in voisinage:
                lm, cm = (l_wkr + dl, c_wkr+dc)
                if not (0 <= lm < 5 and 0 <= cm < 5):
                    continue

                hauteur_voisine = hauteurs_plateau[lm][cm]
                diff_voisine = hauteur_adv - hauteur_voisine
                minime_montée = min(minime_montée, diff_voisine)
                if diff_voisine ==1:
                    has_good_voisin = True
                    score_wadv -= hauteur_adv * 5
                    break
                elif diff_voisine <=0:               
                    minime_descente = -max(diff_voisine, minime_descente)
            
            if not has_good_voisin:
                score_wadv += minime_descente * 15
            if minime_montée >1:
                score_wadv += 1000
            
            score_montée += score_wadv

        return score_montée

    def evaluate_distance_centre(self, state: GameState):
        score_distance =0
        nb_wkr =0
        for wkr in state.workers_by_player[self.id_player]:
            wkr_pos = state.worker_pos_by_worker[wkr]
            if wkr_pos is not None:
                l_wkr, c_wkr = wkr_pos
                distance = self.rules.distance_du_centre[l_wkr][c_wkr]
                score_distance -=  distance
        for wkr in state.workers_by_player[1 - self.id_player]:
            wkr_pos = state.worker_pos_by_worker[wkr]
            if wkr_pos is not None:
                l_wkr, c_wkr = wkr_pos
                distance = self.rules.distance_du_centre[l_wkr][c_wkr]
                score_distance += distance
        return score_distance/(state.nb_joueurs)
    
    def evaluate_1(self, state : GameState):
        if state.current_phase == "PLACEMENT":
            score_distance_centre = random.randint(1,100) #self.evaluate_distance_centre(state)
            return score_distance_centre
            """elif state.cumsum_plateau < 4:
            score_distance_centre = self.evaluate_distance_centre(state)
            score_diff_hauteur = self.evaluate_diff_hauteur(state)
            return score_distance_centre * 4 + score_diff_hauteur*2"""
        else:
            score_diff_hauteur = self.evaluate_diff_hauteur(state)
            score_distance_centre = self.evaluate_distance_centre(state)
            return score_diff_hauteur * 5 + score_distance_centre * 3
        
    def evaluate_2(self, state : GameState):
        if state.current_phase == "PLACEMENT":
            score_distance_centre = random.randint(1,100)            
            return score_distance_centre
            """elif state.cumsum_plateau < 4:
            score_distance_centre = self.evaluate_distance_centre(state)
            score_diff_hauteur = self.evaluate_diff_hauteur(state)
            return score_distance_centre * 4 + score_diff_hauteur*2"""
        else:
            score_montabilite = self.evaluate_montabilité(state)
            score_diff_hauteur = self.evaluate_diff_hauteur(state)
            score_distance_centre = self.evaluate_distance_centre(state)
            return score_diff_hauteur * 5 + score_distance_centre * 3 + score_montabilite * 5

    def tri_move(self, state : GameState, action):
        laction, caction = action.move_to_pos
        if state.current_phase == "PLACEMENT":
            distance = self.rules.distance_du_centre[laction][caction]
            score_distance = self.rules.centre[0] - distance
            return score_distance
        else:
            hauteurs = state.hauteur_plateau
            score_hauteur = hauteurs[laction][caction]
            #------
            for ld,cd in self.rules.voisinage:
                lv = laction + ld
                cv = caction + cd
                if 0 <= lv < len(state.hauteur_plateau) and 0 <= cv < len(state.hauteur_plateau):
                    if (hauteurs[lv][cv] - score_hauteur) == 1:
                        score_hauteur *= 2
                        break
            #------
            distance = self.rules.distance_du_centre[laction][caction]
            score_distance = self.rules.centre[0] - distance
            
            wkr_from_ia = action.worker_id in state.workers_by_player[self.id_player]
            score = score_hauteur * 10 + score_distance * 4
            
            score = score  * (wkr_from_ia) - score * (1 - wkr_from_ia)
            
            return score
    
    def tri_build(self, state : GameState, action : BuildAction):
        l_wkr, c_wkr = state.worker_pos_by_worker[action.worker_id]
        hauteur_acteur = state.hauteur_plateau[l_wkr][c_wkr]
        l_action, c_action =action.build_to_pos
        hauteur_action = state.hauteur_plateau[l_action][c_action]
        diff = hauteur_action - hauteur_acteur
        if hauteur_action < 4:
            if diff > 0:
                score =  (3-diff) * 10 * hauteur_action
            elif diff == 0: 
                score =  hauteur_action * 10 * 1.5
            else:
                score =  -10
        else:
            if diff ==2:
                score = -20
            else:
                score -15
        wkr_from_ia = action.worker_id in state.workers_by_player[self.id_player]
        score = score  * (wkr_from_ia) - score * (1 - wkr_from_ia)
        return score
                
    def alpha_beta(self, state: GameState):
        start_time = perf_counter()
        best_score = -float('inf')
        best_action = None
        depth_choix = self.depth if state.current_phase != "PLACEMENT" else 3
        alpha_root = -float('inf')
        beta_root = float('inf')
        k = 0
        total_noeuds = 0

            # Trier action1 par score heuristique décroissant avant la boucle
        actions1 = sorted(
            self.rules.legal_actions(state),
            key=lambda a: self.tri_move(state, a),
            reverse=True
        )
        for action1 in actions1:
            wkr = action1.worker_id
            old_pos = state.worker_pos_by_worker[wkr]
            self.rules.apply_action(state, action1)

            # Cas où il y a une phase BUILD
            if state.current_phase == state.PHASES[0]:
                state.current_phase = state.PHASES[1]
                actions2 = sorted(
                    self.rules.legal_actions(state, wkr = wkr),
                    key=lambda a: self.tri_build(state, a),
                    reverse=True
                )

                for action2 in actions2:
                    k += 1
                    #print(f"On est sur le fils {k} du noeud racine")
                    self.rules.apply_action(state, action2)

                    # Fin du tour → joueur suivant
                    state.current_phase = state.PHASES[0]
                    old_index = state.ordre_passage_index
                    old_player = state.current_player
                    state.current_player = self.rules.next_player(state)

                    score, nb_fils_reel= self.minimax(
                        state,
                        depth=depth_choix-1,
                        alpha=alpha_root,
                        beta=beta_root
                    )
                    total_noeuds += nb_fils_reel
                    if count_ok:
                        print(f"Le fils {k} a généré {nb_fils_reel} fils réels")
                    if score > best_score:
                        best_score = score
                        best_action = (action1, action2)
                    alpha_root = max(alpha_root, best_score)

                    # UNDO action2 (BUILD)
                    row_build, col_build = action2.build_to_pos
                    state.hauteur_plateau[row_build][col_build] -= 1
                    # UNDO next_player
                    state.ordre_passage_index = old_index
                    state.current_player = old_player
                    # UNDO phase
                    state.current_phase = state.PHASES[1]

                state.current_phase = state.PHASES[0]

            else:
                k+=1
                # Fin du tour → joueur suivant
                #Gestion changement de phase/joueur si placement fini :
                all_placed = True
                for worker_id, worker_pos in state.worker_pos_by_worker.items():
                    if worker_pos is None:
                        all_placed = False
                if all_placed:
                    state.current_phase = state.PHASES[0]
                
                old_index = state.ordre_passage_index
                old_player = state.current_player
                state.current_player = self.rules.next_player(state)
                
                # phase placement
                score, nb_fils_reel = self.minimax(
                    state,
                    depth=depth_choix-1,
                    alpha=alpha_root,
                    beta=beta_root,
                )
                if score > best_score:
                    best_score = score
                    best_action = [action1]
                alpha_root = max(alpha_root, best_score)
                total_noeuds += nb_fils_reel
                
                # UNDO next player + phase
                state.current_phase = "PLACEMENT"
                state.ordre_passage_index = old_index
                state.current_player = old_player

            # UNDO action1 (MOVE)
            state.worker_pos_by_worker[wkr] = old_pos
            state.occupants.pop(action1.move_to_pos, None)
            state.occupants[old_pos] = wkr

        #print(f"BEST: {best_action} | SCORE: {best_score}")
        end = perf_counter() - start_time
        if count_ok :
            print(f"Nombre total de noeuds visité : {total_noeuds} ({total_noeuds/k}/fils)")
            print("time taken for action2: {:.4f} seconds".format(end))
        
        return best_action, total_noeuds

    def minimax(self, state: GameState, depth, alpha, beta, start_time=None, nb_fils_reel = 0):
        for joueur_id in state.ordre_passage_joueurs_liste:
            if self.rules.is_winner_by_height(state, joueur_id):
                return self.utility(state), nb_fils_reel
        if depth == 0:
            return self.evaluate(state), nb_fils_reel


        is_maximizing = (state.current_player == self.id_player)
        if is_maximizing:
            max_eval = -float('inf')
            actions1 = sorted(
                self.rules.legal_actions(state),
                key=lambda a: self.tri_move(state, a),
                reverse=is_maximizing
            )
            for action1 in actions1:
                wkr = action1.worker_id
                old_pos = state.worker_pos_by_worker[wkr]
                self.rules.apply_action(state, action1)

                if state.current_phase == state.PHASES[0]:
                    state.current_phase = state.PHASES[1]
                    actions2 = sorted(
                        self.rules.legal_actions(state, wkr=wkr),
                        key=lambda a: self.tri_build(state, a),
                        reverse=is_maximizing
                    )
                    for action2 in actions2:
                        self.rules.apply_action(state, action2)
                        nb_fils_reel+=1

                        state.current_phase = state.PHASES[0]
                        old_index = state.ordre_passage_index
                        old_player = state.current_player
                        state.current_player = self.rules.next_player(state)

                        eval, nb_fils_reel = self.minimax(state, depth - 1, alpha, beta, start_time, nb_fils_reel=nb_fils_reel)
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)

                        # UNDO action2 (BUILD)
                        row_build, col_build = action2.build_to_pos
                        state.hauteur_plateau[row_build][col_build] -= 1
                        # UNDO next_player
                        state.ordre_passage_index = old_index
                        state.current_player = old_player
                        # UNDO phase
                        state.current_phase = state.PHASES[1]

                        if beta <= alpha:
                            state.current_phase = state.PHASES[0]
                            # UNDO action1 (MOVE)
                            state.worker_pos_by_worker[wkr] = old_pos
                            state.occupants.pop(action1.move_to_pos, None)
                            state.occupants[old_pos] = wkr
                            return max_eval, nb_fils_reel  # coupure

                    state.current_phase = state.PHASES[0]

                else:                    
                    nb_fils_reel+=1
                    
                    # Fin du tour → joueur suivant
                    #Gestion changement de phase/joueur si placement fini :
                    all_placed = True
                    for worker_id, worker_pos in state.worker_pos_by_worker.items():
                        if worker_pos is None:
                            all_placed = False
                    if all_placed:
                        state.current_phase = state.PHASES[0]
                    
                    old_index = state.ordre_passage_index
                    old_player = state.current_player
                    state.current_player = self.rules.next_player(state)

                    eval, nb_fils_reel = self.minimax(state, depth - 1, alpha, beta, start_time, nb_fils_reel=nb_fils_reel)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)

                    if beta <= alpha:
                        # UNDO next player + phase
                        state.current_phase = "PLACEMENT"
                        state.ordre_passage_index = old_index
                        state.current_player = old_player
                        # UNDO action1 (MOVE)
                        state.worker_pos_by_worker[wkr] = old_pos
                        state.occupants.pop(action1.move_to_pos, None)
                        state.occupants[old_pos] = wkr
                        return max_eval, nb_fils_reel
                    
                    # UNDO next player + phase
                    state.current_phase = "PLACEMENT"
                    state.ordre_passage_index = old_index
                    state.current_player = old_player

                # UNDO action1 (MOVE)
                state.worker_pos_by_worker[wkr] = old_pos
                state.occupants.pop(action1.move_to_pos, None)
                state.occupants[old_pos] = wkr

            return max_eval, nb_fils_reel

        else:
            min_eval = float('inf')
            actions1 = sorted(
                self.rules.legal_actions(state),
                key=lambda a: self.tri_move(state, a),
                reverse=is_maximizing
            )
            for action1 in actions1:
                wkr = action1.worker_id
                old_pos = state.worker_pos_by_worker[wkr]
                self.rules.apply_action(state, action1)

                if state.current_phase == state.PHASES[0]:
                    state.current_phase = state.PHASES[1]
                    actions2 = sorted(
                        self.rules.legal_actions(state, wkr=wkr),
                        key=lambda a: self.tri_build(state, a),
                        reverse=is_maximizing
                    )
                    for action2 in actions2:
                        self.rules.apply_action(state, action2)
                        nb_fils_reel+=1
                         
                        state.current_phase = state.PHASES[0]
                        old_index = state.ordre_passage_index
                        old_player = state.current_player
                        state.current_player = self.rules.next_player(state)

                        eval, nb_fils_reel= self.minimax(state, depth - 1, alpha, beta, start_time, nb_fils_reel=nb_fils_reel)
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)

                        # UNDO action2 (BUILD)
                        row_build, col_build = action2.build_to_pos
                        state.hauteur_plateau[row_build][col_build] -= 1
                        # UNDO next_player
                        state.ordre_passage_index = old_index
                        state.current_player = old_player
                        # UNDO phase
                        state.current_phase = state.PHASES[1]

                        if beta <= alpha:
                            state.current_phase = state.PHASES[0]
                            
                            # UNDO action1 (MOVE)
                            state.worker_pos_by_worker[wkr] = old_pos
                            state.occupants.pop(action1.move_to_pos, None)
                            state.occupants[old_pos] = wkr
                            return min_eval, nb_fils_reel # coupure

                    state.current_phase = state.PHASES[0]

                else:
                    nb_fils_reel+=1
                    
                    # Fin du tour → joueur suivant
                    #Gestion changement de phase/joueur si placement fini :
                    all_placed = True
                    for worker_id, worker_pos in state.worker_pos_by_worker.items():
                        if worker_pos is None:
                            all_placed = False
                    if all_placed:
                        state.current_phase = state.PHASES[0]
                    
                    old_index = state.ordre_passage_index
                    old_player = state.current_player
                    state.current_player = self.rules.next_player(state)

                    eval, nb_fils_reel= self.minimax(state, depth - 1, alpha, beta, start_time, nb_fils_reel=nb_fils_reel)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)

                    if beta <=alpha:
                        # UNDO next player + phase
                        state.current_phase = "PLACEMENT"
                        state.ordre_passage_index = old_index
                        state.current_player = old_player

                        # UNDO action1 (MOVE)
                        state.worker_pos_by_worker[wkr] = old_pos
                        state.occupants.pop(action1.move_to_pos, None)
                        state.occupants[old_pos] = wkr
                        return min_eval, nb_fils_reel
                    
                    # UNDO next player + phase
                    state.current_phase = "PLACEMENT"
                    state.ordre_passage_index = old_index
                    state.current_player = old_player
                    
                # UNDO action1 (MOVE)
                state.worker_pos_by_worker[wkr] = old_pos
                state.occupants.pop(action1.move_to_pos, None)
                state.occupants[old_pos] = wkr
            
            return min_eval, nb_fils_reel
       
       
    #Corbeille 
    def evaluate_montabilité1(self, state : GameState):
        cpt = 0

        for wkr in state.workers_by_player[self.id_player]:
            l_w, c_w = state.worker_pos_by_worker[wkr]
            hauteur_wkr = state.hauteur_plateau[l_w][c_w]

            taille_plateau = len(state.hauteur_plateau)
            hauteur_plateau = state.hauteur_plateau
            for dl in [-1,1]:
                for dc in [-1, 1]:
                    if dl == 0 and dc == 0:
                        continue
                    nl, nc = l_w + dl, c_w + dc

                    if 0 <= nl < taille_plateau and 0 <= nc <taille_plateau:
                        hauteur_voisine =hauteur_plateau[nl][nc]

                        if hauteur_voisine == hauteur_wkr + 1:
                            cpt += 1

        return cpt            
    def evaluate_obsolete(self, state : GameState):
        if state.current_phase == "PLACEMENT":
            return random.randint(0,100)
        #COEF SELON AVANCEE DU JEU
        else:
            #score_possibilities = self.evaluate_possibility(state)
            score_diff_hauteur = self.evaluate_diff_hauteur(state)
            score_montee = self.evaluate_montabilité(state)
            return score_diff_hauteur * 7+ score_montee*2
    def evaluate_hauteur(self, state: GameState):
        #evaluate notre hauteur et nos possibilité de monter autour de nous

        score_diff_hauteur = 0
        score_montée = 0

        for wkr in state.workers_by_player[self.id_player]:
            l_wkr, c_wkr = state.worker_pos_by_worker[wkr]
            hauteur_wkr = state.hauteur_plateau[l_wkr][c_wkr]
            score_wkr =0
            has_good_voisin = False #voisin ou on peut monter
            minime_descente = -self.rules.taille_plateau[2]
            minime_montée = self.rules.taille_plateau[2]
            for dl,dc in self.rules.voisinage:
                lm, cm = (l_wkr + dl, c_wkr+dc)
                if not (0 <= lm < 5 and 0 <= cm < 5):
                    continue

                hauteur_voisine = state.hauteur_plateau[lm][cm]
                diff_voisine = hauteur_wkr - hauteur_voisine
                minime_montée = min(minime_montée, diff_voisine)
                if diff_voisine ==1:
                    has_good_voisin = True
                    score_wkr += hauteur_wkr * 5
                    break
                elif diff_voisine <=0:               
                    minime_descente = max(diff_voisine, minime_descente)
            
            if not has_good_voisin:
                score_wkr += minime_descente * 5
            if minime_montée >1:
                score_wkr -= 1000
            
            score_montée += score_wkr
            score_diff_hauteur += hauteur_wkr #gestion du score_diff_hauteur

        for wkr in state.workers_by_player[1 - self.id_player]:
            l_wkr, c_wkr = state.worker_pos_by_worker[wkr]
            hauteur_adv = state.hauteur_plateau[l_wkr][c_wkr]
            score_wadv =0
            has_good_voisin = False #voisin ou on peut monter
            minime_descente = -self.rules.taille_plateau[2]
            minime_montée = self.rules.taille_plateau[2]
            for dl,dc in self.rules.voisinage:
                lm, cm = (l_wkr + dl, c_wkr+dc)
                if not (0 <= lm < 5 and 0 <= cm < 5):
                    continue

                hauteur_voisine = state.hauteur_plateau[lm][cm]
                diff_voisine = hauteur_adv - hauteur_voisine
                minime_montée = min(minime_montée, diff_voisine)
                if diff_voisine ==1:
                    has_good_voisin = True
                    score_wadv -= hauteur_adv * 5
                    break
                elif diff_voisine <=0:               
                    minime_descente = -max(diff_voisine, minime_descente)
            
            if not has_good_voisin:
                score_wadv += minime_descente * 15
            if minime_montée >1:
                score_wadv += 1000
            
            score_montée += score_wadv
            score_diff_hauteur -= state.hauteur_plateau[l_wkr][c_wkr]

        return score_diff_hauteur, score_montée
    def tri_move1(self, state : GameState, action): #plus optimal, mais doit l'etre +, si je le laisse tranquille il est censé gagné en 5 coups (renforcer la performance indiv des wkr)
        laction, caction = action.move_to_pos
        score_hauteur = state.hauteur_plateau[laction][caction]

        distance = self.rules.distance_du_centre[laction][caction]
        score_distance = self.rules.centre[0] - distance
        return score_hauteur * 7 + score_distance * 3

