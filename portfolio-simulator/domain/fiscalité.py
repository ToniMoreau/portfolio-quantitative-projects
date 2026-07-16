from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Fiscalité:
    annee: int = 2025
@dataclass
class Fiscalité_salaires(Fiscalité):
    pass
