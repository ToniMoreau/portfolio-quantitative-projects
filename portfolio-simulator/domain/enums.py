from enum import Enum



class investType(str, Enum):
    EMPTY = ""
    IMMO = "immobilier"
    STOCK = "stock"


class DependentType(str, Enum):
    INVESTISSEMENT = "INVESTISSEMENT"
    CREDIT = "CREDIT"
    RECETTE = "RECETTE"      # standalone or métier-linked
    DEPENSE = "DEPENSE"      # standalone
    METIER = "METIER"