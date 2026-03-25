from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Identité:
    nom: str
    prénom: str
    age: int

    def __str__(self):
        return f"{self.prénom} {self.nom}, {self.age} an{"s" if self.age >1 else ""}"