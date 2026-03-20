from dataclasses import dataclass
from typing import ClassVar



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

    id_utilisateur: int | None = None
    montant: float = 0. 
    

    def décrire(self):
        return f"{self.intitule_compte} chez {self.id_banque}, avec un solde de {self.montant}"
    

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
    debut : int = 0
    montant : float = 0
    duree_diff_mois : int | None = None
    durée_crédit_mois : int | None = None
    mensualite_constante : float | None = None
    taux_crédit_pct : float = 0.
    type : str = "" #"Mensualité Constante" ou "DUREE (MOIS)"

    def __str__(self):
        return f"Crédit d'un montant de {self.montant} €, échéance de {self.échéance} €. Remboursement pendant {self.durée_crédit_année} mois"





