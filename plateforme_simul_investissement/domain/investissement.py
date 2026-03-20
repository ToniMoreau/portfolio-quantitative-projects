


from dataclasses import dataclass

@dataclass
class Investissement:
    investissement_ID : int
    user_ID : int
    
    nom : str
    
    valeur : int
    augmentation_annuelle : int
    date_achat : str
    date_vente : str