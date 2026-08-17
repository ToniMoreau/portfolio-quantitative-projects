from repositories import MetierRepository
from domain.entities.profil_pro import Salarié
from domain.errors import (
    MetierNotFoundError,
    IntegrityError,
    MissingColumnError,
)
from datetime import date
from utils.date import add_months
import numpy as np

from .depenseService import DepenseService
from .recetteService import RecetteService
class MetierService:
    def __init__(self, recette_service : RecetteService, depense_service : DepenseService, metier_repo: MetierRepository):
        self.metier_repo = metier_repo
        self.metier_actif_id:int | None= None
        self.recette_service = recette_service
        self.depense_service = depense_service
    def update_metier(self, metier_id, data):
        try:
            metier = self.metier_repo.get_by_ID(metier_ID=metier_id)
            if metier is None:
                metier = self.metier_repo.create(data)
            else:
                self.metier_repo.update(metier.id, data)
            fresh_metier = self.metier_repo.get_by_ID(metier.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Metier") from e

        if fresh_metier is None:
            raise IntegrityError("Metier introuvable après update")
        return fresh_metier
    
    def get_by_criterias(self, dict_bys):
        try:
            return self.metier_repo.get_by_(dict_bys)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Metier") from e
    
    def get_metier_by_id(self,metier_id):
        try:
            return self.metier_repo.get_by_ID(metier_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Metier") from e
    
    def get_metier_by_scenario(self, scenario_id):
        try:
            metiers = self.metier_repo.get_by_({"ID SCENARIO": scenario_id})
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Metier") from e

        if metiers is None:
            return []
        return metiers
    
    def revenu_net_mensuel_from_brut_annuel(self,metier_id):
        try:
            metier = self.metier_repo.get_by_ID(metier_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Metier") from e

        if metier is None:
            raise MetierNotFoundError(metier_id)

        if metier.privé.capitalize() == "OUI":
            taux = 0.83
        else :
            taux = 0.77
        net_mensuel = metier.annuel_brut/12 * taux
        return net_mensuel
    
    def set_metier_actif(self, metier_id):
        self.metier_actif_id = metier_id
    
    def get_salaires_nets_from_date(self, scenario_id : int, date_courante : date)-> float:
        salaires_actifs = 0
        for metier in self.get_metier_by_scenario(scenario_id):
            if metier.est_actif(date_courante):
                salaires_actifs += metier.mensuel_net()
        return salaires_actifs
    
    def get_salaires_moyens_x_mois(self, scenario_id : int,nb_mois : int, date_seuil : date) ->float :
        salaires = []
        for i in range(1,nb_mois+1):
            date_test = add_months(date_seuil, -i)
            salaires.append(self.get_salaires_nets_from_date(scenario_id, date_test))
        return float(np.mean(salaires))
             
    def delete(self, metier_id):
        metier = self.metier_repo.get_by_ID(metier_id)
        if metier is None:
            raise MetierNotFoundError(metier_id)
        try:
            depenses_liees = self.depense_service.get_by_criterias({"ID SOURCE": metier_id}) or []
            recettes_liees = self.recette_service.get_by_criterias({"ID SOURCE": metier_id}) or []

            for depense in depenses_liees:
                self.depense_service.delete_depense(depense.id)
            for recette in recettes_liees:
                self.recette_service.delete_recette(recette.id)
                
            self.metier_repo.delete(metier.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Metier") from e