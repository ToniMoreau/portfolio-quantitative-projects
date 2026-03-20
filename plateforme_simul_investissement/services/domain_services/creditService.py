from repositories.repositories import CreditcRepository, RecetteRepository
from domain import Crédit
from numpy import log
class CreditService:
    def __init__(self, credit_repo: CreditcRepository, recette_repo : RecetteRepository):
        self.credit_repo = credit_repo
        self.recette_repo = recette_repo
        self.credit_actif = None
    
    def update_credit(self, credit_id, data):
        credit = self.credit_repo.get_by_ID(credit_id)
        if credit is None:
            credit = self.credit_repo.create(data)
        else: self.credit_repo.update(credit.id, data)
        
        fresh_credit = self.credit_repo.get_by_ID(credit.id)
        if fresh_credit is None:
            raise ValueError("Metier introuvable après update")
        return fresh_credit
    
    def set_credit_actif(self, new_actif : Crédit | None = None):
        self.credit_actif = new_actif
        
    def get_all_credit_from_user(self, user_id) -> list[Crédit]:
        liste = self.credit_repo.get_by_userID(user_id)
        if liste is None:
            return []
        return liste
    
    def get_credit_by_id(self, credit_id):
        return self.credit_repo.get_by_ID(credit_id)
    def delete_credit(self, credit : Crédit):
        self.credit_repo.delete(credit.id)
    
    def get_all_credits_from_scenario(self, scenario_id):
        credits = self.credit_repo.get_by_({"ID SCENARIO": scenario_id})
        return credits
    
    def montant_total_cb_from_scenario(self, scenario_id):
        credits = self.get_all_credits_from_scenario(scenario_id)
        somme = 0
        for credit in credits:
            somme += credit.montant
        return somme
    
    def capacite_emprunt(self, id_scenario):
        # revenus (salaires, locatifs - 70%)
        #crédits en cours
        #35% d'endettement
        ENDETTEMENT_TAUX = 0.35
        
        revenu_mensuels = self.recette_repo.get_by_({"ID SCENARIO" : id_scenario, "NATURE" : "Revenus", "FREQUENCE" : "Mensuel"})
        print("REVENUS : ", revenu_mensuels)
        revenus_locatifs = self.recette_repo.get_by_({"ID SCENARIO" : id_scenario, "NATURE" : "Revenus locatifs", "FREQUENCE" : "Mensuel"})     
        print("REVENUS LOC : ", revenus_locatifs)
        capa_emprunt = 0
        for revenu in revenu_mensuels:
            capa_emprunt += revenu.montant
        for locatif in revenus_locatifs:
            capa_emprunt += locatif.montant * 0.7
            
        capa_emprunt*=ENDETTEMENT_TAUX
        
        credits = self.get_all_credits_from_scenario(id_scenario)
        
        for credit in credits:
            amortissement = self.tableau_amortissement(credit.id)
            moyenne_mensu = sum(amortissement["MENSUALITE TOTALE (€)"])/len(amortissement["MENSUALITE TOTALE (€)"])
            capa_emprunt -= moyenne_mensu
        
        return max(0, capa_emprunt)
    
    def tableau_amortissement(self, id_credit):
        credit = self.get_credit_by_id(id_credit)
        amortissement = {"ANNEE" : [], 
                    "A REMBOURSER (€)" : [], 
                    "TAUX INTERET (PCT)" : [], 
                    "INTERETS (ANNUEL)" : [], "INTERETS (MENSUEL)" : [], 
                    "REMBOURSEMENT (ANNUEL)" : [], "REMBOURSEMENT (MENSUEL)" : [], 
                    "MENSUALITE TOTALE (€)" : []}

        a_rembourser = credit.montant
        taux_interet_pct = credit.taux_crédit_pct
        
        #Traitement de la partie différée
        interet_diff_annuel = a_rembourser * taux_interet_pct/100
        interet_diff_mensuel = interet_diff_annuel/12
        
        annee = 0
        for diff in range(credit.duree_diff_mois // 12):
            annee = diff
            amortissement["ANNEE"].append(annee)
            amortissement["A REMBOURSER (€)"].append(round(a_rembourser,2))
            amortissement["TAUX INTERET (PCT)"].append(taux_interet_pct)
            amortissement["INTERETS (ANNUEL)"].append(round(interet_diff_annuel,2))
            amortissement["INTERETS (MENSUEL)"].append(round(interet_diff_mensuel,2))
            amortissement["REMBOURSEMENT (MENSUEL)"].append(0)
            amortissement["REMBOURSEMENT (ANNUEL)"].append(0)
            amortissement["MENSUALITE TOTALE (€)"].append(0)

        #Traitement de la partie amortissement
        if credit.type == "Mensualité Constante":
            annuite = credit.mensualite_constante * 12
            annee +=1
            while a_rembourser > 0:
                
                amortissement["ANNEE"].append(annee)
                amortissement["A REMBOURSER (€)"].append(round(a_rembourser,2))
                amortissement["TAUX INTERET (PCT)"].append(taux_interet_pct)
                
                interet_annuel = a_rembourser * taux_interet_pct/100
                part_rbsmt_annuel = min(annuite - interet_annuel, a_rembourser)

                interet_mensuel = interet_annuel/12
                part_rbsmt_mensuel = part_rbsmt_annuel/12
                
                amortissement["INTERETS (ANNUEL)"].append(round(interet_annuel,2))
                amortissement["INTERETS (MENSUEL)"].append(round(interet_mensuel,2))
                amortissement["REMBOURSEMENT (MENSUEL)"].append(round(part_rbsmt_mensuel,2))
                amortissement["REMBOURSEMENT (ANNUEL)"].append(round(part_rbsmt_annuel,2))
                amortissement["MENSUALITE TOTALE (€)"].append(round(part_rbsmt_mensuel + interet_mensuel,2))
                
                a_rembourser -= part_rbsmt_annuel
                annee +=1
            return amortissement
        elif credit.type == "DUREE (MOIS)":
            duree_mois = credit.durée_crédit_mois
            print(duree_mois)
            duree_annee = duree_mois//12 + 1
            print(duree_annee)
            part_rbsmt_annuel = a_rembourser / duree_annee
            annee = 0
            while annee != duree_annee:
                amortissement["ANNEE"].append(annee)
                amortissement["A REMBOURSER (€)"].append(round(a_rembourser,2))
                amortissement["TAUX INTERET (PCT)"].append(taux_interet_pct)
                
                interet_annuel = a_rembourser * taux_interet_pct/100
                part_rbsmt_annuel = min(part_rbsmt_annuel, a_rembourser)
                part_rbsmt_mensuel = part_rbsmt_annuel/12
                interet_mensuel = interet_annuel/12

                amortissement["INTERETS (ANNUEL)"].append(round(interet_annuel,2))
                amortissement["INTERETS (MENSUEL)"].append(round(interet_mensuel,2))
                amortissement["REMBOURSEMENT (MENSUEL)"].append(round(part_rbsmt_mensuel,2))
                amortissement["REMBOURSEMENT (ANNUEL)"].append(round(part_rbsmt_annuel,2))
                amortissement["MENSUALITE TOTALE (€)"].append(round(part_rbsmt_mensuel + interet_mensuel,2))
                
                a_rembourser -=part_rbsmt_annuel
                annee +=1
            return amortissement
                
    def montant_from_mensu_duree(self, duree_mois : int, mensualite : float, taux_annuel_pct : float, duree_differe_mois : int = 0):
        taux_mensuel_pct = taux_annuel_pct/12
        taux_mensuel = taux_mensuel_pct/100
        
        if taux_annuel_pct == 0:
            empruntable == mensualite * duree_mois
        else:
            empruntable = mensualite * (1 - (1+taux_mensuel)**(-duree_mois))/(taux_mensuel * (1+taux_mensuel)**duree_differe_mois)
        return empruntable
     
    def mensu_from_montant_duree(self, montant : float, duree_mois : int, taux_annuel_pct : float, duree_differe_mois : int):
        taux_mensuel = taux_annuel_pct/(100*12)
        
        if taux_annuel_pct ==0:
            return montant/duree_mois
        mensu_constante = montant * (1+taux_mensuel)**(duree_differe_mois) * (taux_mensuel/(1-(1+taux_mensuel)**(-duree_mois)))
        return mensu_constante
    
    def duree_from_montant_mensu(self, montant, mensu, taux_annuel_pct, duree_differe_mois : int):
        taux_mensuel = taux_annuel_pct/(100*12)
        if taux_mensuel == 0:
            return montant / mensu  
        if mensu <= montant * taux_mensuel:
            raise ValueError("Mensualité trop faible pour couvrir les intérêts")        
        a_amortir = montant *(1+taux_mensuel)**duree_differe_mois
        
        duree_mois = - (log(1 - (a_amortir * taux_mensuel)/mensu)/log(1+taux_mensuel))
        return duree_mois
                        
            
            
            