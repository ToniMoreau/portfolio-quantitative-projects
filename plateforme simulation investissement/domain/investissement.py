


from dataclasses import dataclass
from datetime import date
@dataclass
class Investissement:
    id : int
    id_user : int
    id_compte : int
    id_scenario : int
    id_achat : int | None
    id_vente : int | None
    id_credit : int | None

    nature : str #Immobilier ou Boursier
    etat : str # TRUE / FALSE

    prix_achat : int
    comptant_pct : int #pourcentage de l'achant fait en comptant
    
    date_in : date
    date_out : date | None
    
    valorisation_annuelle_pct : int #% d'augmentation annuel de la valeur
    @property
    def credit_pct(self):
        return 100 - self.comptant_pct

    def est_actif(self):
        return self.etat
    def est_immo(self):
        return self.nature == "Immobilier"
    def est_boursier(self):
        return self.nature == "Boursier"

    def est_projet_immo(self):
        return not(self.est_actif()) and self.est_immo()
    def est_actif_immo(self):
        return self.est_actif() and self.est_immo()
    
