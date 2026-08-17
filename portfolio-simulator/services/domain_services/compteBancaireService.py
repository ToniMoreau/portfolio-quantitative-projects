from repositories import CompteBancaireRepository
from domain.entities import Banque, CompteBancaire
from domain.errors import (
    CompteBancaireNotFoundError,
    IntegrityError,
    MissingColumnError,
)
from .recetteService import RecetteService
from .depenseService import DepenseService
from datetime import date
from utils.date import *
from typing import NamedTuple

class ResultatSolde(NamedTuple):
    solde: float
    interets_totaux: float
    interets_dernier_mois: float
    solde_hors_interets: float  # ← Nouveau

class CompteBancaireService:
    def __init__(self, cb_repo: CompteBancaireRepository, recette_service : RecetteService, depense_service : DepenseService):
        self.cb_repo = cb_repo
        self.depense_service = depense_service
        self.recette_service = recette_service
        self.cb_actif_id = None
    
    def update_cb(self, cb_id, data):
        try:
            cb = self.cb_repo.get_by_ID(cb_id)
            if cb is None:
                cb = self.cb_repo.create(data)
            else:
                self.cb_repo.update(cb.id, data)
            fresh_cb = self.cb_repo.get_by_ID(cb.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="CompteBancaire") from e

        if fresh_cb is None:
            raise IntegrityError("CompteBancaire introuvable après update")
        return fresh_cb
    
    def set_cb_actif(self, new_actif_id : int | None = None):
        self.cb_actif_id = new_actif_id
        
    def get_all_cb_from_user(self, user_id) -> list[CompteBancaire]:
        try:
            liste = self.cb_repo.get_by_userID(user_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="CompteBancaire") from e

        if liste is None:
            return []
        return liste
    
    def get_cb_by_id(self, cb_id):
        try:
            return self.cb_repo.get_by_ID(cb_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="CompteBancaire") from e
    
    def delete_cb(self, cb_id):
        cb = self.cb_repo.get_by_ID(cb_id)
        if cb is None:
            raise CompteBancaireNotFoundError(cb_id)
        try:
            depenses_liees = self.depense_service.get_by_criterias({"ID COMPTE": cb_id})
            recettes_liees = self.recette_service.get_by_criterias({"ID COMPTE": cb_id})

            for depense in depenses_liees:
                self.depense_service.delete_depense(depense.id)
            for recette in recettes_liees:
                self.recette_service.delete_recette(recette.id)

            self.cb_repo.delete(cb.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Comptes Bancaires") from e   
             
    def all_userCB_from_banque(self, user_id, banque_id):
        cb_user = self.get_all_cb_from_user(user_id)
        from_this_banque = []
        for cb in cb_user:
            if cb.id_banque == banque_id:
                from_this_banque.append(cb)
                
        return from_this_banque
    
    def all_userCB_from_(self, dict_str_id : dict[str,int]):
        try:
            return self.cb_repo.get_by_(dict_str_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="CompteBancaire") from e
        
    def all_userCB_from_scenario(self, scenario_id):
        try:
            cbs = self.cb_repo.get_by_({"ID SCENARIO": scenario_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="CompteBancaire") from e
        return cbs

    def montant_total_cb_from_scenario(self, scenario, date_valide : date):
        cbs = self.all_userCB_from_scenario(scenario.id)
        somme = 0
        for cb in cbs:
            somme += self.solde_from_cb(scenario.date_in, cb.id, date_valide).solde
        return somme
    

    def solde_from_cb(self, date_in_scenario: date, cbs_id: int | list[int], date_valide: date,
                    excluded_ids: set = None) -> ResultatSolde:
        excluded_ids = excluded_ids or set()
        print('inner excl id', excluded_ids)
        if isinstance(cbs_id, int):
            cbs_id = [cbs_id]
        
        solde_total = 0.0
        solde_hors_interets_total = 0.0
        interets_totaux = 0.0
        interets_dernier_mois = 0.0
        
        mois_debut = date_in_scenario.year * 12 + date_in_scenario.month
        mois_fin = date_valide.year * 12 + date_valide.month
        
        for cb_id in cbs_id:
            cb = self.get_cb_by_id(cb_id)
            if cb is None:
                raise CompteBancaireNotFoundError(cb_id)

            solde_cb = 0.
            solde_cb_hors_interets = 0.  # ← Suit les flux sans intérêts
            taux_mensuel = (1 + cb.taux_annuel) ** (1/12) - 1
            
            try:
                depenses = self.depense_service.get_by_criterias({"ID COMPTE": cb_id}) or []
                recettes = self.recette_service.get_by_criterias({"ID COMPTE": cb_id}) or []
            except KeyError as e:
                raise MissingColumnError(str(e), feuille="Recette/Depense") from e
            
            depenses = [d for d in depenses 
                        if d.id not in excluded_ids and d.id_source not in excluded_ids]
            recettes = [r for r in recettes 
                        if r.id not in excluded_ids and r.id_source not in excluded_ids]
            
            for mois in range(mois_debut, mois_fin + 1):
                flux_mois = self._calculer_flux_mois(mois, recettes, depenses)
                
                solde_cb += flux_mois
                solde_cb_hors_interets += flux_mois  # ← Même flux, pas d'intérêts
                
                if solde_cb > 0:
                    interets_mois = solde_cb * taux_mensuel
                    interets_totaux += interets_mois
                    
                    if mois == mois_fin:
                        interets_dernier_mois += interets_mois
                    
                    solde_cb += interets_mois
            
            solde_total += solde_cb
            solde_hors_interets_total += solde_cb_hors_interets
        
        return ResultatSolde(
            solde=round(solde_total, 2),
            solde_hors_interets=round(solde_hors_interets_total, 2),
            interets_totaux=round(interets_totaux, 2),
            interets_dernier_mois=round(interets_dernier_mois, 2)
        )          
    def _calculer_flux_mois(self, mois: int, recettes: list, depenses: list) -> float:
        """Calcule le flux net (recettes - dépenses) pour un mois donné."""
        flux = 0.0
        
        for recette in recettes:
            if self._est_actif_ce_mois(recette, mois):
                flux += recette.montant
        
        for depense in depenses:
            if self._est_actif_ce_mois(depense, mois):
                flux -= depense.montant
        
        return flux

    def _est_actif_ce_mois(self, flux, mois: int) -> bool:
        """Vérifie si une recette/dépense est active pour un mois donné."""
        year, month = get_date_tuple_from_month(mois)
        year_in,month_in = (flux.date_in.year, flux.date_in.month)
        year_out, month_out = (flux.date_out.year, flux.date_out.month)
        
        if flux.frequence == "Annuel":            
            return month_in == month and year_in < year <= year_out
        else:
            mois_debut = year_in * 12 + month_in
            mois_fin = year_out * 12 + month_out
            
            return mois_debut <= mois <= mois_fin