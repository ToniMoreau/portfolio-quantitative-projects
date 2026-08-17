from dataclasses import dataclass
from typing import ClassVar
from datetime import date
from utils.date import *
from domain.enums import DependentType
# dans une banque il y a des profils bancaire, dans un profil bancaire il y a des crédits et des comptes, dans les comptes il y a des comptes bancaires

@dataclass
class Banque:
    id: int
    nom: str
    liste_id_profil_bancaire = list[int]
    taux_credit_pct : float = 0

    def __str__(self):
        return f"Banque {self.nom} (ID = {self.id})"
    
@dataclass
class Profil_bancaire: #contient des compte bancaires de la banque pour cet id_utilisateur
    id:int
    id_utilisateur: int
    id_banque: int
    liste_id_comptes: list[int]
    liste_id_crédits: list[int]

    def __str__(self):
        return f"id"

@dataclass
class CompteBancaire:
    id: int
    type : str 
    id_banque: int | None
    id_scenario : int | None
    id_utilisateur: int | None = None
    solde_initial: float = 0.
    taux_annuel : float | None = None
    

@dataclass
class CompteCourant(CompteBancaire):
    decouvert_autorisé : ClassVar[bool] = False

    montant_minimum : float | None = 10
    virement_interne : bool = True
    virement_externe : bool = True

    def décrire(self):
        super().décrire()
    
@dataclass
class CompteEpargne(CompteBancaire):
    taux_remun : ClassVar[float] = 0.0
    decouvert_autorisé : ClassVar[bool] = False
    virement_interne : ClassVar[bool] = True
    virement_externe : ClassVar[bool] = False

    montant_minimum : float | None = 10

    def décrire(self):
        super().décrire()


@dataclass
class ProduitsDérivés:
    nom: str
@dataclass
class Crédit:
    id: int
    id_banque: int
    id_utilisateur : int
    id_compte : int
    id_source : int | None= None
    debut : date = None
    fin : date = None
    montant : float = 0
    duree_diff_mois : int | None = None
    durée_crédit_mois : int | None = None
    mensualite_constante : float | None = None
    taux_crédit_pct : float = 0.
    type : str = "" #"Mensualité Constante" ou "DUREE (MOIS)"


    def __str__(self):
        return f"Crédit d'un montant de {self.montant} €, échéance de {self.mensualite_constante} €. Remboursement pendant {self.durée_crédit_mois} mois"

    def credit_restant_from_date(self, date : date):
        total_remboursement = self.mensualite_constante * self.durée_crédit_mois
        if date < self.debut:
            return total_remboursement
        return max(total_remboursement - self.mensualite_constante * month_count(self.debut, date),0)
    
    def duree_restante_from_date(self, date :date):
        
        return max(month_count(self.debut, self.fin) - month_count(self.debut, date),0)
    

    def prix_credit(self):
        return self.mensualite_constante * self.durée_crédit_mois

    def present_value(self):
        monthly_inflation =  (1+0.015)**(1/12) - 1
        print(self.mensualite_constante)
        print(self.mensualite_constante*(1-(1+monthly_inflation)**(-self.durée_crédit_mois))/monthly_inflation)
        return self.mensualite_constante*(1-(1+monthly_inflation)**(-self.durée_crédit_mois))/monthly_inflation
    
    def get_dependent_type(self):
        return DependentType.CREDIT
