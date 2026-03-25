from dataclasses import dataclass
from typing import ClassVar

@dataclass
class catégorie_immo:
    nb_chambre : int
    nb_pièce : int
    nom: str

@dataclass
class nature_immmo:
    nature : str
    
@dataclass
class Immobilier:
    id : int
    nom: str

    date_construction : str
    valeur: float
    nature : nature_immmo
    catégorie: catégorie_immo
    surface: float 

    id_propriétaire : int | None = None
    id_locataire : int | None = None

@dataclass
class Projet_immo:
    id : int

    id_immo: int
    id_crédit: int

    balance: int
    etat: str # projet, actif, ancien

Maison = nature_immmo("Maison")
Appartement = nature_immmo("Appartement")
Immeuble = nature_immmo("Immeuble")
Parking = nature_immmo("Parking")
Local_commercial = nature_immmo("Local Commercial")
Terrain = nature_immmo("Terrain")

Studio = catégorie_immo("Studio", 1,0)
T1 = catégorie_immo("T1",2,0)
T1bis = catégorie_immo("T1bis", 1,1)
T2 = catégorie_immo("T2", 2,1)
T3 = catégorie_immo("T3", 3,1)

@dataclass
class VenteImmo:
    id_acquereur: int
    id_vendeur: int

    montant_vente: float