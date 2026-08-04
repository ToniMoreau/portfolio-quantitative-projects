


from dataclasses import dataclass
from typing import ClassVar
from datetime import date
from utils.date import month_count

@dataclass
class Investissement:
    nature: ClassVar[str] = "investissement"    
    id : int
    id_scenario : int
    
    id_user : int
    id_compte : int
    id_achat : int | None
    id_vente : int | None

    titre : str #infos minimale sur le projet
    etat : str # "à créditer/à conclure/actif/vendu"

    prix_achat : float
    
    date_in : date
    date_out : date | None
    
    valorisation_annuelle_pct : float #% d'augmentation annuel de la valeur
    

    def prix_vente(self, date_vente : date, sold_prior : bool = True):
        """
        sold_prior = True :
        Donne le prix de vente a la date_vente souhaitée sauf si le bien est déja vendu, auquel cas le prix affiché sera celui de la vente. 
        sold_prior = False:
        Donne le prix du bien à la date_vente souhaitée, peu importe s'il a déjà été vendu avant, ou après.

        Args:
            date_vente (date): _description_
            sold_prior (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        valo_mensuelle = (1 + self.valorisation_annuelle_pct)**(1/12)-1
        if sold_prior:
            if self.date_out is not None:
                return self.prix_achat*(1+valo_mensuelle)**(month_count(self.date_in, self.date_out))
            else:
                return self.prix_achat*(1+valo_mensuelle)**(month_count(self.date_in, date_vente))
        else:
            return self.prix_achat*(1+valo_mensuelle)**(month_count(self.date_in, date_vente))
        
    def present_value(self, date_vente : date, sold_prior :bool = True):
        """
        sold_prior = True :
        Donne la valeur actuelle (inflation corrigée) a la date souhaitée sauf si le bien est déja vendu, 
        auquel cas la valeur affiché sera celle de la vente. 
        sold_prior = False:
        Donne la valeur actuelle (inflation corrigée) à la date souhaitée, peu importe s'il a déjà été vendu à une autre date
        Args:
            date_vente (date): _description_
            sold_prior (_type_): _description_

        Returns:
            _type_: _description_
        """
        monthly_inflation = (1 + 0.015)**(1/12)-1
        if sold_prior:
            if self.date_out is not None:
                return self.prix_vente(date_vente)/(1+monthly_inflation)**(month_count(self.date_in, self.date_out))
            else:
                return self.prix_vente(date_vente)/(1+monthly_inflation)**(month_count(self.date_in, date_vente))
        else:
            return self.prix_vente(date_vente)/(1+monthly_inflation)**(month_count(self.date_in, date_vente))

@dataclass
class Immobilier(Investissement):
    nature: ClassVar[str] = "Immobilier"
    localisation: str
    surface: int
    type: str
    comptant_pct: float
    id_credit: int | None = None    
    
    @property
    def credit_pct(self):
        return 100 - self.comptant_pct
    def est_actif(self):
        return self.etat == "actif" or self.etat == "vendu"
    def paiement_comptant(self):
        return self.prix_achat * self.comptant_pct
@dataclass
class StockOption(Investissement):
    nature: ClassVar[str] = "Stock"    
    id_dividendes : int
    dividendes_pct : float

    def dividendes_montant(self):
        return self.prix_achat * self.dividendes_pct
