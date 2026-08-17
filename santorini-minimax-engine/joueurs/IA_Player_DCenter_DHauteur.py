from joueurs.player import Player
from joueurs.ia_player import IAPlayer
from core import GameState, SantoriniRules
from math import inf,sqrt
from time import sleep, perf_counter
from core import MoveAction, BuildAction
import random

count_ok = False
class IAPlayerDCenterDHauteur(IAPlayer):
    def __init__(self, nom, prenom, dict_coefs_eval : dict[str, float], dict_coefs_tri: dict[str, float], database_tuple):
        super().__init__(nom, prenom, database_tuple)
        self.id_player = None
        self.rules : SantoriniRules = None
        
        self.dict_coefs_eval = dict_coefs_eval
        self.dict_eval_function = {("Mobilite_Verticale_Montee","Mobilite_Verticale_Descente") : (self.evaluate_mobilite_verticale, self.evaluate_mobilité_montee, self.evaluate_mobilite_descente), 
                           "Controle_Hauteur_3" : self.evaluate_controle_hauteur3, 
                           "Difference_Hauteur" : self.evaluate_diff_hauteur, 
                           "Distance_Centre" : self.evaluate_distance_centre}
        self.dict_coefs_tri = dict_coefs_tri
        
        self.historique_tri= [] #liste avec un tuple (dict_poids_normalisés, ratio élagage) par match
        self.temps_par_tour = []
        self.temps_moyen_parties = []
        self.noeuds_par_tour = []
        self.noeuds_moyen_parties = []
        self.matchs = []
        
        self.SEUIL_GHOSTING= 0.75
    @property
    def id_database(self):
        return self.database_tuple[0]
    @property
    def generation(self):
        return self.database_tuple[1]
    @property
    def profondeur(self):
        return self.database_tuple[2]
    @property
    def beam_N(self):
        return self.database_tuple[3]
    @property
    def temps_moyen_dernier_match(self):
        return self.database_tuple[4]
    @property
    def nb_victoire(self):
        return self.database_tuple[5]
    @property
    def nb_match(self):
        return self.database_tuple[6]
    @property
    def ratio_elagage(self):
        return self.database_tuple[7]
    @property
    def elo(self):
        return self.database_tuple[8]
    
    def utility(self, state : GameState):
        winner = self.rules.winner(state)
        if winner is not None: #y'a un gagnant
            if winner == self.id_player:
                return 10000
            return -10000     
        
    def evaluate_controle_hauteur3(self, state: GameState):
        workers_max = state.workers_by_player[self.id_player]
        worker_pos = state.worker_pos_by_worker
        hauteurs_3 = state.cases_hauteurs_3
        cpt_max = 0
        cpt_min = 0      
        for l_case, c_case in hauteurs_3:
            dist_min_max = min(
                max(abs(worker_pos[wkr][0] - l_case), abs(worker_pos[wkr][1] - c_case))
                for wkr in workers_max
            )
            dist_min_min = min(
                max(abs(worker_pos[wkr][0] - l_case), abs(worker_pos[wkr][1] - c_case))
                for wkr in state.workers_by_player[1 - self.id_player]
            )
            if dist_min_max < dist_min_min:
                cpt_max += 1
            elif dist_min_min < dist_min_max:
                cpt_min += 1
        return cpt_max - cpt_min 
                       
    def evaluate_mobilite_verticale(self, state : GameState):
        hauteur = state.hauteur_plateau
        wkr_by_ply = state.workers_by_player
        voisins_valides= self.rules.voisins_valides
        wkr_coord_by_wkr = state.worker_pos_by_worker
        hauteur_max = self.rules.taille_plateau[2]
        
        bon_voisin_max = 0
        minime_descente_max = -hauteur_max
        for wkr in wkr_by_ply[self.id_player]: #wkr du max
            l_wkr, c_wkr = wkr_coord_by_wkr[wkr]
            wkr_hauteur = hauteur[l_wkr][c_wkr]
            for l_vois, c_vois in voisins_valides[(l_wkr, c_wkr)]:                
                hauteur_voisin = hauteur[l_vois][c_vois]
                diff_hauteur = hauteur_voisin - wkr_hauteur
                if diff_hauteur ==1:
                    bon_voisin_max +=hauteur_voisin
                elif diff_hauteur < 1 and minime_descente_max != 0:
                    minime_descente_max = max(minime_descente_max, diff_hauteur)      
                                  
        bon_voisin_min =0
        minime_descente_min = -hauteur_max
        for wkr in wkr_by_ply[1-self.id_player]: #wkr du max
            l_wkr, c_wkr = wkr_coord_by_wkr[wkr]
            wkr_hauteur = hauteur[l_wkr][c_wkr]
            for l_vois, c_vois in voisins_valides[(l_wkr, c_wkr)]:                
                hauteur_voisin = hauteur[l_vois][c_vois]
                diff_hauteur = hauteur_voisin - wkr_hauteur
                if diff_hauteur ==1:
                    bon_voisin_min +=hauteur_voisin
                elif diff_hauteur < 1 and minime_descente_min != 0:
                    minime_descente_min = max(minime_descente_min, diff_hauteur)     
                       
        score_descente = minime_descente_max - minime_descente_min
        score_montee = bon_voisin_max - bon_voisin_min
        return (score_montee, score_descente)
    
    def evaluate_mobilite_descente(self, state : GameState):
        hauteur = state.hauteur_plateau
        wkr_by_ply = state.workers_by_player
        voisins_valides= self.rules.voisins_valides
        wkr_coord_by_wkr = state.worker_pos_by_worker
        hauteur_max = self.rules.taille_plateau[2]
        
        found_zero = False
        minime_descente_max = -hauteur_max
        for wkr in wkr_by_ply[self.id_player]: #wkr du max
            if found_zero:
                break
            l_wkr, c_wkr = wkr_coord_by_wkr[wkr]
            wkr_hauteur = hauteur[l_wkr][c_wkr]
            if wkr_hauteur == 0:
                minime_descente_max = 0
                found_zero = True
                break
            else:
                for l_vois, c_vois in voisins_valides[(l_wkr, c_wkr)]:                
                    hauteur_voisin = hauteur[l_vois][c_vois]
                    diff_hauteur = hauteur_voisin - wkr_hauteur
                    if diff_hauteur ==0:
                        minime_descente_max = 0
                        found_zero = True
                        break
                    elif diff_hauteur <0:
                        minime_descente_max = max(minime_descente_max, diff_hauteur)      
        
        found_zero = False                
        minime_descente_min = -hauteur_max
        for wkr in wkr_by_ply[1-self.id_player]: #wkr du max
            if found_zero:
                break
            l_wkr, c_wkr = wkr_coord_by_wkr[wkr]
            wkr_hauteur = hauteur[l_wkr][c_wkr]
            if wkr_hauteur ==0:
                minime_descente_min =0
                found_zero = True
                break
            else:
                for l_vois, c_vois in voisins_valides[(l_wkr, c_wkr)]:                
                    hauteur_voisin = hauteur[l_vois][c_vois]
                    diff_hauteur = hauteur_voisin - wkr_hauteur
                    if diff_hauteur ==0:
                        minime_descente_min =0
                        found_zero = True
                        break
                    elif diff_hauteur < 0:
                        minime_descente_min = max(minime_descente_min, diff_hauteur)     
                       
        score_descente = minime_descente_max - minime_descente_min
        return score_descente
    
    def evaluate_mobilité_montee(self, state : GameState):
        hauteur = state.hauteur_plateau
        wkr_by_ply = state.workers_by_player
        voisins_valides= self.rules.voisins_valides
        wkr_coord_by_wkr = state.worker_pos_by_worker
        
        bon_voisin_max = 0
        for wkr in wkr_by_ply[self.id_player]: #wkr du max
            l_wkr, c_wkr = wkr_coord_by_wkr[wkr]
            wkr_hauteur = hauteur[l_wkr][c_wkr]
            for l_vois, c_vois in voisins_valides[(l_wkr, c_wkr)]:                
                hauteur_voisin = hauteur[l_vois][c_vois]
                diff_hauteur = hauteur_voisin - wkr_hauteur
                if diff_hauteur ==1:
                    bon_voisin_max +=hauteur_voisin
                                  
        bon_voisin_min =0
        for wkr in wkr_by_ply[1-self.id_player]: #wkr du max
            l_wkr, c_wkr = wkr_coord_by_wkr[wkr]
            wkr_hauteur = hauteur[l_wkr][c_wkr]
            for l_vois, c_vois in voisins_valides[(l_wkr, c_wkr)]:                
                hauteur_voisin = hauteur[l_vois][c_vois]
                diff_hauteur = hauteur_voisin - wkr_hauteur
                if diff_hauteur ==1:
                    bon_voisin_min +=hauteur_voisin
                       
        score_montee = bon_voisin_max - bon_voisin_min
        return score_montee

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
    
    def evaluate(self, state : GameState):
        if state.current_phase =="PLACEMENT":
            return random.randint(1,100)
        else:
            score = 0
            coefs = self.dict_coefs_eval
            for nom, function in self.dict_eval_function.items():
                if isinstance(nom,tuple):
                    coef_1, coef_2 = coefs[nom[0]], coefs[nom[1]]
                    if coef_1 <= self.SEUIL_GHOSTING and coef_2 <= self.SEUIL_GHOSTING:
                        continue
                    elif coef_1 <= self.SEUIL_GHOSTING:
                        result_1 = 0
                        result_2 = function[2](state)
                        score += (result_1 * coef_1) + (result_2 * coef_2)
                        continue
                    elif coef_2 <= self.SEUIL_GHOSTING:
                        result_1 = function[1](state)
                        result_2 = 0
                        score += (result_1 * coef_1) + (result_2 * coef_2)
                        continue
                    else:
                        result_1, result_2 = function[0](state)
                        score += (result_1 * coef_1) + (result_2 * coef_2)
                        continue
                else:
                    if coefs[nom] <= self.SEUIL_GHOSTING:
                        continue
                    else:
                        result = function(state)
                        score += (result* coefs[nom])
            return score
    
    def tri_move(self, state : GameState, action):
        laction, caction = action.move_to_pos
        hauteurs = state.hauteur_plateau
        hauteur = hauteurs[laction][caction]
        #OPTIMISATION : GHOSTING SOUS SEUIL (ECONOMIE CALCUL) + COEFFICIENTS APPRIS PAR L'IA (EFFICACITE)
        if self.dict_coefs_eval["Distance_Centre"] <= self.SEUIL_GHOSTING:
            ##GHOSTING DISTANCE CENTRE
            score_distance = 0
        else:
            distance = self.rules.distance_du_centre[laction][caction]
            score_distance = (self.rules.centre[0] - distance) * self.dict_coefs_tri["Distance_Centre"]
            
        if state.current_phase == "PLACEMENT":
            #ECONOMIE PHASE PLACEMENT
            return score_distance
        else:
            #PHASE MOVE/BUILD
            #SCORING CH3 
            score_CH3 = 0
            if self.dict_coefs_eval["Controle_Hauteur_3"] <= self.SEUIL_GHOSTING:
                ##GHOSTING CONTROLE HAUTEUR 3
                pass
            else:
                if state.cases_hauteurs_3:
                    score_CH3 = -min([max(abs(l_case_3 - laction), abs(c_case_3 -caction)) for l_case_3, c_case_3 in state.cases_hauteurs_3]) *self.dict_coefs_tri["Controle_Hauteur_3"]
        
            #SCORING DIFF HAUTEUR 
            if self.dict_coefs_eval["Difference_Hauteur"] <= self.SEUIL_GHOSTING:
                ##GHOSTING Difference_Hauteur
                score_hauteur = 0
            else:
                score_hauteur = hauteur*self.dict_coefs_tri["Difference_Hauteur"]
                
            #SCORING MV MONTEE 
            score_MV = 0
            if (self.dict_coefs_eval["Mobilite_Verticale_Montee"] <= self.SEUIL_GHOSTING)  and (self.dict_coefs_eval["Mobilite_Verticale_Descente"] <= self.SEUIL_GHOSTING):
                ##GHOSTING Mobilite_Verticale_Montee
                pass
            else:
                for lv, cv in self.rules.voisins_valides[(laction,caction)]:
                    if (hauteurs[lv][cv] - hauteur) == 1:
                        score_MV = hauteurs[lv][cv] * self.dict_coefs_tri["Mobilite_Verticale_Montee"]
                        break
                else:
                    score_MV = -3 * self.dict_coefs_tri["Mobilite_Verticale_Descente"]
            
            #SCORISATION : NEGATIF SI TRI MIN, POSITIF SI TRI MAX     
            wkr_from_ia = action.worker_id in state.workers_by_player[self.id_player]
            score = score_CH3 + score_hauteur + score_MV + score_distance
            score = score  * (wkr_from_ia) - score * (1 - wkr_from_ia)
            return score

    ## doit se baser sur les éléments du evaluate
    ##distance du centre
    ##difference hauteur
    ##mobilité verticale montée/descente
    ##controle hauteur 3
    
    #est ce que ce build me permet de monter au prochain tour? Mobilité verticale Montée
    #est ce que ce build favorise le nombre de hauteur 3 pour moi/ et pas pour mon adversaire?
    #est ce que ce build est un dome favorable (bloquant) ? 
    def tri_build_trop_complexe(self, state : GameState, action : BuildAction):
        coef_MVM = 0 if (self.dict_coefs_eval["Mobilite_Verticale_Montee"] <= self.SEUIL_GHOSTING or self.dict_coefs_tri["Mobilite_Verticale_Montee"] <= self.SEUIL_GHOSTING) else self.dict_coefs_tri["Mobilite_Verticale_Montee"]
        coef_CH3 = 0 if (self.dict_coefs_eval["Controle_Hauteur_3"] <= self.SEUIL_GHOSTING or self.dict_coefs_tri["Controle_Hauteur_3"] <= self.SEUIL_GHOSTING) else self.dict_coefs_tri["Controle_Hauteur_3"]
        coef_desc = 0 if (self.dict_coefs_eval["Mobilite_Verticale_Descente"] <= self.SEUIL_GHOSTING or self.dict_coefs_tri["Mobilite_Verticale_Descente"] <= self.SEUIL_GHOSTING) else self.dict_coefs_tri["Mobilite_Verticale_Descente"]
        
        if coef_MVM == 0 and coef_CH3 == 0 and coef_desc == 0:
            return 0
        
        l_action, c_action = action.build_to_pos
        hauteur_build = state.hauteur_plateau[l_action][c_action]
        
        score_adv = 0
        for wkr in state.workers_by_player[1 - state.current_player]:
            wkr_pos = state.worker_pos_by_worker[wkr]
            if wkr_pos in self.rules.voisins_valides[action.build_to_pos]:
                i, j = wkr_pos
                adv_hauteur = state.hauteur_plateau[i][j]
                diff_advBuild = hauteur_build - adv_hauteur
                if diff_advBuild == 1:
                    score_adv += hauteur_build * (coef_MVM + (hauteur_build == 3) * coef_CH3)
                elif diff_advBuild == 2:
                    score_adv -= hauteur_build * (coef_MVM + (hauteur_build == 4) * coef_CH3)
        
        l_wkr, c_wkr = state.worker_pos_by_worker[action.worker_id]
        hauteur_wkr = state.hauteur_plateau[l_wkr][c_wkr]
        
        score_joueur = 0
        diff = hauteur_build - hauteur_wkr
        if hauteur_build < 4:
            if diff > 0:
                score_joueur = (3 - diff) * hauteur_build * (coef_MVM + (hauteur_build == 3) * coef_CH3) / 3
            elif diff == 0:
                score_joueur = hauteur_build * coef_desc
            else:
                score_joueur = -coef_desc
        else:
            if diff == 2:
                score_joueur = -coef_CH3 - coef_MVM
        
        score_MVM = -score_adv + score_joueur
        wkr_from_ia = action.worker_id in state.workers_by_player[self.id_player]
        score_MVM = score_MVM * (wkr_from_ia) - score_MVM * (1 - wkr_from_ia)
        return score_MVM                       
    
    def tri_build_claude(self, state: GameState, action: BuildAction):
        l_action, c_action = action.build_to_pos
        hauteur_build = state.hauteur_plateau[l_action][c_action]
        l_wkr, c_wkr = state.worker_pos_by_worker[action.worker_id]
        hauteur_wkr = state.hauteur_plateau[l_wkr][c_wkr]
        diff = hauteur_build - hauteur_wkr

        # SCORE DE BASE : hauteur construite × accessibilité
        if hauteur_build == 3:
            score = 30  # case hauteur 3 très précieuse
        elif diff == 1:
            score = hauteur_build * 10  # montée possible au prochain tour
        elif diff == 0:
            score = hauteur_build * 5   # latéral utile
        elif hauteur_build == 4:
            score = 15  # dôme — bloque une case
        else:
            score = -5  # build peu utile

        # BONUS : si worker adverse adjacent peut monter sur ce build
        for wkr in state.workers_by_player[1 - state.current_player]:
            pos = state.worker_pos_by_worker[wkr]
            if pos in self.rules.voisins_valides[action.build_to_pos]:
                adv_h = state.hauteur_plateau[pos[0]][pos[1]]
                if hauteur_build - adv_h == 1:
                    score -= 20  # on facilite la montée adverse
                if hauteur_build == 3 and hauteur_build - adv_h == 1:
                    score -= 50  # catastrophique : adversaire peut gagner

        wkr_from_ia = action.worker_id in state.workers_by_player[self.id_player]
        score = score * (wkr_from_ia) - score * (1 - wkr_from_ia)
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
                score = -15
        wkr_from_ia = action.worker_id in state.workers_by_player[self.id_player]
        score = score  * (wkr_from_ia) - score * (1 - wkr_from_ia)
        return score
                
    def alpha_beta(self, state: GameState):
        start_time = perf_counter()
        best_score = -float('inf')
        best_action = None
        depth_choix = self.profondeur if state.current_phase != "PLACEMENT" else 3
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
        actions1 = actions1[:self.beam_N]
        if not actions1:
            return -10000, total_noeuds
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
                actions2 = actions2[:int(self.beam_N*0.67)]

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
                        beta=beta_root,
                        start_time=start_time
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
                    hauteur_apres_undo = state.hauteur_plateau[row_build][col_build]
                    if hauteur_apres_undo == 2:
                        state.cases_hauteurs_3.remove((row_build, col_build))
                    elif hauteur_apres_undo == 3:
                        state.cases_hauteurs_3.append((row_build, col_build))                    
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
                    start_time=start_time
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
        if start_time is not None and perf_counter() - start_time > 12:
            return self.evaluate(state), nb_fils_reel
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
            actions1 = actions1[:self.beam_N]

            if not actions1:
                return -10000, nb_fils_reel
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
                    actions2 = actions2[:int(self.beam_N*0.67)]
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
                        hauteur_apres_undo = state.hauteur_plateau[row_build][col_build]
                        if hauteur_apres_undo == 2:
                            state.cases_hauteurs_3.remove((row_build, col_build))
                        elif hauteur_apres_undo == 3:
                            state.cases_hauteurs_3.append((row_build, col_build))                    

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
            actions1 = actions1[:self.beam_N]
            if not actions1:
                return 10000, nb_fils_reel
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
                    actions2 = actions2[:int(self.beam_N*0.67)]
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
                        hauteur_apres_undo = state.hauteur_plateau[row_build][col_build]
                        if hauteur_apres_undo == 2:
                            state.cases_hauteurs_3.remove((row_build, col_build))
                        elif hauteur_apres_undo == 3:
                            state.cases_hauteurs_3.append((row_build, col_build))                    

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
    def tri_move_old(self, state : GameState, action):
        laction, caction = action.move_to_pos
        distance = self.rules.distance_du_centre[laction][caction]
        score_distance = self.rules.centre[0] - distance
        if state.current_phase == "PLACEMENT":
            return score_distance
        else:
            hauteurs = state.hauteur_plateau
            score_hauteur = hauteurs[laction][caction]
            #------
            for lv, cv in self.rules.voisins_valides[(laction,caction)]:
                if (hauteurs[lv][cv] - score_hauteur) == 1:
                    score_hauteur *= 2
                    break
            #------            
            wkr_from_ia = action.worker_id in state.workers_by_player[self.id_player]
            score = score_hauteur * 10 + score_distance * 4
            
            score = score  * (wkr_from_ia) - score * (1 - wkr_from_ia)
            
            return score

    def evaluate_obsolete(self, state : GameState):
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
            return score_diff_hauteur * self.dict_coefs["Différence Hauteur"] + score_distance_centre * self.dict_coefs["Distance Centre"]

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

