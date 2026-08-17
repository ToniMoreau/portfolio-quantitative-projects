from joueurs import IAPlayer, IAPlayerDCenterDHauteur
from data.database import *
import numpy as np
import random as rd

class GestionTournoi:
    def __init__(self, connection : sqlite3.Connection, rules):
        self.pool = []
        self.TAILLE_POOL = 30
        self.NB_MATCHS_MANCHE = 500
        self.cpt_matchs = get_tournoi_cpt(connection, self.NB_MATCHS_MANCHE)
        self.NB_SURVIVANTS = 10
        self.generation =  get_generation_actuelle(connection) or 0
        self.connection = connection
        self.ELO_INITIAL = 1000
        self.rules = rules
        self.DEPTH_MAX = 6
        self.BEAM_MAX =16
        self.SEUIL_NB_MATCH_AJUSTEMENT_TRI = 5
        self.TAUX_APPRENTISSAGE_TRI = 0.5
        
    def ajuster_coefs_tri(self, ia : IAPlayerDCenterDHauteur):
        import math
        seuil = math.sqrt(70**ia.profondeur) * 3
        ratio = np.median(ia.historique_tri) / seuil if seuil > 0 else 0
        print(f"ia : {ia.id_database} depth {ia.profondeur} ","ratio : ", ratio," seuil : ", seuil, "meidane : ", np.median(ia.historique_tri))
        
        if ratio > 1:
            sigma = min(2.0, (ratio - 1) * self.TAUX_APPRENTISSAGE_TRI)
            for nom in ia.dict_coefs_tri:
                bruit = rd.gauss(0, sigma)
                ia.dict_coefs_tri[nom] = max(0, ia.dict_coefs_tri[nom] + bruit)
            mettre_a_jour_coefs_tri(self.connection, ia.id_database, ia.dict_coefs_tri)
        
        ia.historique_tri = []        
    def enregistrer_match(self, ia_1 : IAPlayerDCenterDHauteur, ia_2 : IAPlayerDCenterDHauteur, gagant_1 : bool):
        ia_1_elo, ia_2_elo = self.calculer_elo(ia_1, ia_2, gagant_1)
        ia_1_median_time_dernier_match = round(np.median(ia_1.temps_par_tour),2)
        ia_2_median_time_dernier_match = round(np.median(ia_2.temps_par_tour),2)
        ia_1_median_noeuds_dernier_match = int(np.median(ia_1.noeuds_par_tour))
        ia_2_median_noeuds_dernier_match = int(np.median(ia_2.noeuds_par_tour))
        ia_1_ratio_elagage = round(ia_1_median_noeuds_dernier_match / (70**ia_1.profondeur), 5)
        ia_2_ratio_elagage = round(ia_2_median_noeuds_dernier_match / (70**ia_2.profondeur),5)
        ia_1.historique_tri.append(ia_1_median_noeuds_dernier_match)
        ia_2.historique_tri.append(ia_2_median_noeuds_dernier_match)
        
        db_ia_1 = mettre_a_jour_ia(self.connection, ia_1.id_database, ia_1_median_time_dernier_match, ia_1.nb_victoire + 1*(gagant_1),ia_1.nb_match+1,ia_1_ratio_elagage, ia_1_elo, self.calculer_score(ia_1_elo,ia_1_median_time_dernier_match))
        db_ia_2 = mettre_a_jour_ia(self.connection, ia_2.id_database, ia_2_median_time_dernier_match, ia_2.nb_victoire + 1*(1-gagant_1),ia_2.nb_match+1,ia_2_ratio_elagage, ia_2_elo, self.calculer_score(ia_2_elo,ia_2_median_time_dernier_match)) 
        ia_1.database_tuple = db_ia_1
        ia_2.database_tuple = db_ia_2
        session = inserer_session(self.connection, ia_1.id_database, ia_2.id_database, ia_1_median_noeuds_dernier_match, ia_2_median_noeuds_dernier_match, ia_1.id_database * (gagant_1) + ia_2.id_database*(1-gagant_1))
        self.cpt_matchs +=1
        
        if len(ia_1.historique_tri) >= self.SEUIL_NB_MATCH_AJUSTEMENT_TRI:
            self.ajuster_coefs_tri(ia_1)
        if len(ia_2.historique_tri) >= self.SEUIL_NB_MATCH_AJUSTEMENT_TRI:
            self.ajuster_coefs_tri(ia_2)
            
        if self.cpt_matchs >=500:
            self.selectionner_survivants()
            self.générer_nouvelle_génération()
            self.cpt_matchs =0
    
    def db_to_ia(self, tuple, dict_coefs_eval = None, dict_coefs_tri = None):
        if dict_coefs_eval is None:
            dict_coefs_eval = get_coefs_eval_from_id(self.connection, tuple[0])
        if dict_coefs_tri is None:
            dict_coefs_tri = get_coefs_tri_from_id(self.connection, tuple[0])
            
        ia = IAPlayerDCenterDHauteur(str(tuple[0]), str(tuple[1]), dict_coefs_eval, dict_coefs_tri, tuple)
        ia.rules = self.rules
        return ia    
    
    def random_coefs(self):
        dict_coefs = {"Difference_Hauteur" : round(np.random.uniform(0,10),2), 
            "Distance_Centre" : round(np.random.uniform(0,10),2), 
            "Controle_Hauteur_3" :round(np.random.uniform(0,10),2), 
            "Mobilite_Verticale_Montee" : round(np.random.uniform(0,10),2),
            "Mobilite_Verticale_Descente": round(np.random.uniform(0,10),2)}
        return dict_coefs

    def initialiser_pool(self):
        ias = get_all_ias(self.connection)
        
        self.pool = [self.db_to_ia(ia) for ia in ias]
        if len(self.pool) > self.TAILLE_POOL:
            self.pool = sorted(self.pool, key = lambda ia: self.calculer_score(ia.elo, ia.temps_moyen_dernier_match), reverse=True)[:self.TAILLE_POOL]
        while len(self.pool)< self.TAILLE_POOL:
            dict_coefs_eval = self.random_coefs()
            dict_coefs_tri  = self.random_coefs()
            database_tuple = inserer_ia(self.connection,self.generation,np.random.randint(1,4),np.random.randint(4,self.BEAM_MAX+1),self.ELO_INITIAL)
            ia = self.db_to_ia(database_tuple, dict_coefs_eval, dict_coefs_tri)
            inserer_coefs_eval(self.connection, ia.id_database,dict_coefs_eval)
            inserer_coefs_tri(self.connection, ia.id_database, dict_coefs_tri)
            self.pool.append(ia)
        
    def calculer_elo(self, ia_1 : IAPlayerDCenterDHauteur, ia_2 : IAPlayerDCenterDHauteur, gagnant_1 : bool):
        ancien_elo_1 = ia_1.elo
        ancien_elo_2 = ia_2.elo
        nb_matchs_ia_1 = ia_1.nb_match
        nb_matchs_ia_2 = ia_2.nb_match
        
        k1=32 if nb_matchs_ia_1 < 30 else 16
        k2= 32 if nb_matchs_ia_2 <30 else 16
        E_1 = 1 / (1 + 10**((ancien_elo_2-ancien_elo_1)/400))
        E_2 =  1 / (1 + 10**((ancien_elo_1-ancien_elo_2)/400))
        
        nouvel_elo_1 = ancien_elo_1 + k1*(gagnant_1 - E_1)
        nouvel_elo_2 = ancien_elo_2 + k2*((1-gagnant_1) - E_2)
        
        return round(nouvel_elo_1,2), round(nouvel_elo_2,2)
        
    def calculer_score(self, elo:float, temps_moyen_tour : float):
        K= np.exp(-(temps_moyen_tour/30)**2)
        return max(1, round(elo * K, 2))
    
    def matchmaking(self):
        np.random.shuffle(self.pool)
        return self.pool[0], self.pool[1]
    def selectionner_survivants(self):
        self.pool= sorted(self.pool, key= lambda ia: self.calculer_score(ia.elo, ia.temps_moyen_dernier_match), reverse=True)
        self.eliminés = self.pool.copy()[self.NB_SURVIVANTS:]
        for eliminé in self.eliminés:
            mettre_a_jour_active(self.connection, id_ia=eliminé.id_database, active=0)
        self.pool = self.pool[:self.NB_SURVIVANTS]
    
    def coefs_mutant(self, parent1 : IAPlayerDCenterDHauteur, parent2: IAPlayerDCenterDHauteur):
        dict_coefs_eval = {}
        dict_coefs_tri = {}
        for nom, _ in parent1.dict_coefs_eval.items():
            choix_parent = rd.choice([parent1, parent2])
            coef_eval_parent = choix_parent.dict_coefs_eval[nom]
            coef_eval_enfant = coef_eval_parent + rd.gauss(0, 0.5)
            coef_tri_enfant = choix_parent.dict_coefs_tri[nom]
            if rd.random() < 0.1:
                coef_eval_enfant = rd.uniform(0,20)
                coef_tri_enfant = rd.uniform(0,20)
                
            dict_coefs_eval[nom] = round(max(0,coef_eval_enfant),2)
            dict_coefs_tri[nom] =  round(max(0,coef_tri_enfant),2)
        return dict_coefs_eval, dict_coefs_tri
            
    def générer_nouvelle_génération(self):
        self.generation +=1
        taille_actuelle_pool = len(self.pool)
        for place in range(taille_actuelle_pool,self.TAILLE_POOL):
            parent1 : IAPlayerDCenterDHauteur = rd.choices(self.pool, [self.calculer_score(ia.elo, ia.temps_moyen_dernier_match) for ia in self.pool])[0]
            parent2  : IAPlayerDCenterDHauteur= rd.choices(self.pool, [self.calculer_score(ia.elo, ia.temps_moyen_dernier_match) for ia in self.pool])[0]
            
            profondeur_parent = rd.choice([parent1.profondeur, parent2.profondeur])
            beam_N_parent = rd.choice([parent1.beam_N,parent2.beam_N])
            delta_prof = rd.choices([-1, 0, 1], weights=[0.1, 0.8, 0.1])[0]
            delta_beam =  rd.choices([-1, 0, 1], weights=[0.1, 0.8, 0.1])[0]
            profondeur_enfant = max(1, min(self.DEPTH_MAX, profondeur_parent + delta_prof))
            beam_enfant = max(4, min(self.BEAM_MAX,beam_N_parent+delta_beam))
            dict_coefs_eval_enfant, dict_coefs_tri_enfant = self.coefs_mutant(parent1, parent2)
            
            db_tuple_enfant = inserer_ia(self.connection, self.generation, profondeur_enfant,beam_enfant, self.ELO_INITIAL)
            enfant = self.db_to_ia(db_tuple_enfant, dict_coefs_eval_enfant, dict_coefs_tri_enfant)
            inserer_coefs_eval(self.connection, enfant.id_database, dict_coefs_eval_enfant)
            inserer_coefs_tri(self.connection, enfant.id_database, dict_coefs_tri_enfant)
            
            self.pool.append(enfant)
            
            
            
            
            
    
    
        
    

    