from repositories import CreditRepository
from domain.entities import Crédit
from domain.errors import (
    CreditNotFoundError,
    IntegrityError,
    MissingColumnError,
    BusinessRuleError,
)
from numpy import log
from .depenseService import DepenseService
from .recetteService import RecetteService
from datetime import date
from utils.date import *

class CreditService:
    def __init__(self, credit_repo: CreditRepository, recette_service : RecetteService, depense_service :DepenseService ):
        self.credit_repo = credit_repo        
        self.depense_service = depense_service
        self.recette_service = recette_service
        self.credit_actif_id = None
    
    def update_credit(self, credit_id, data):
        try:
            credit = self.credit_repo.get_by_ID(credit_id)
            if credit is None:
                credit = self.credit_repo.create(data)
            else:
                self.credit_repo.update(credit.id, data)
            fresh_credit = self.credit_repo.get_by_ID(credit.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Credit") from e

        if fresh_credit is None:
            raise IntegrityError("Credit introuvable après update")
        return fresh_credit
    
    def set_credit_actif(self, new_actif_id : int | None = None):
        self.credit_actif_id = new_actif_id

    def get_by_criterias(self, dict_bys):
        try:
            return self.credit_repo.get_by_(dict_bys)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Credit") from e
    
    def get_all_credit_from_user(self, user_id) -> list[Crédit]:
        try:
            liste = self.credit_repo.get_by_userID(user_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Credit") from e

        if liste is None:
            return []
        return liste
    
    def get_credit_by_id(self, credit_id):
        try:
            return self.credit_repo.get_by_ID(credit_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Credit") from e

    def delete_credit(self, credit_id):
        credit = self.credit_repo.get_by_ID(credit_id)
        if credit is None:
            raise CreditNotFoundError(credit_id)
        try:
            depenses_liees = self.depense_service.get_by_criterias({"ID SOURCE": credit_id}) or []
            recettes_liees = self.recette_service.get_by_criterias({"ID SOURCE": credit_id}) or []

            for depense in depenses_liees:
                self.depense_service.delete_depense(depense.id)
            for recette in recettes_liees:
                self.recette_service.delete_recette(recette.id)

            self.credit_repo.delete(credit.id)

        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Credit") from e    
    
    def get_all_credits_from_scenario(self, scenario_id):
        try:
            credits = self.credit_repo.get_by_({"ID SCENARIO": scenario_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Credit") from e
        return credits
    
    def montant_total_credits_from_scenario(self, scenario_id):
        credits = self.get_all_credits_from_scenario(scenario_id)
        somme = 0
        for credit in credits:
            somme += credit.montant
        return somme
    
    def capacite_emprunt(self, id_scenario, date_credit: date, excluded_ids: set = None):
        excluded_ids = excluded_ids or set()
        # revenus (salaires, locatifs *70%)
        #crédits en cours
        #35% d'endettement
        ENDETTEMENT_TAUX = 0.35
        
        try:
            revenu_mensuels = self.recette_service.get_by_criterias({"ID SCENARIO": id_scenario, "NATURE": "Revenus", "FREQUENCE": "Mensuel"}) or []
            revenus_locatifs = self.recette_service.get_by_criterias({"ID SCENARIO": id_scenario, "NATURE": "Locataires", "FREQUENCE": "Mensuel"}) or []
            salaires = self.recette_service.get_by_criterias({"ID SCENARIO": id_scenario, "NATURE": "Salaires", "FREQUENCE": "Mensuel"}) or []
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Recette/") from e
        
        revenus_admissibles = []
        revenus_admissibles.extend(revenus_locatifs)
        revenus_admissibles.extend(revenu_mensuels)
        revenus_admissibles.extend(salaires)

        revenus_admissibles = [r for r in revenus_admissibles
                            if r.id not in excluded_ids and r.id_source not in excluded_ids]
        
        date_out = date_credit.month + date_credit.year * 12
        date_in = date_out - 5
        
        capa_emprunt = 0
        for recette in revenus_admissibles:
            recette_out = recette.date_out.month + recette.date_out.year * 12 
            recette_in = recette.date_in.month + recette.date_in.year * 12
            coef = 1
            if recette.nature.lower() == "revenus locatifs":
                coef = 0.7
                
            date = date_out
            while date >= date_in:
                if recette_in <= date <= recette_out:
                    capa_emprunt += recette.montant * coef
                date -= 1

        capa_emprunt *= ENDETTEMENT_TAUX
        
        credits = self.depense_service.get_by_criterias({"ID SCENARIO": id_scenario, "NATURE": "Crédit", "FREQUENCE": "Mensuel"}) or []
        loyers = self.depense_service.get_by_criterias({"ID SCENARIO": id_scenario, "NATURE": "Loyers", "FREQUENCE": "Mensuel"}) or []
        
        depenses_admissibles = []
        depenses_admissibles.extend(credits)
        depenses_admissibles.extend(loyers)

        depenses_admissibles = [d for d in depenses_admissibles
                                if d.id_source not in excluded_ids and d.id not in excluded_ids]

        for depense in depenses_admissibles:
            depense_out = depense.date_out.month + depense.date_out.year * 12 
            depense_in = depense.date_in.month + depense.date_in.year * 12
            
            date = date_out
            while date >= date_in:
                if depense_in <= date <= depense_out:   
                    capa_emprunt -= depense.montant
                date -= 1
        capa_emprunt /= (date_out - date_in + 1)
        
        return max(0, capa_emprunt)
    
    def tableau_amortissement(self, id_credit):
        credit = self.get_credit_by_id(id_credit)
        if credit is None:
            raise CreditNotFoundError(id_credit)

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
            duree_annee = duree_mois//12 + 1
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
            empruntable = mensualite * duree_mois
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
            raise BusinessRuleError("Mensualité trop faible pour couvrir les intérêts")        
        a_amortir = montant *(1+taux_mensuel)**duree_differe_mois
        
        duree_mois = - (log(1 - (a_amortir * taux_mensuel)/mensu)/log(1+taux_mensuel))
        return duree_mois