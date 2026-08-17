from domain.errors import NotFoundError
from .domain_services import DepenseService, RecetteService

class TransactionService:
    """Handles paired dépense/recette flows sharing one id_transaction."""

    def __init__(self, depense_service : DepenseService, recette_service : RecetteService):
        self.depense_service = depense_service
        self.recette_service = recette_service

    def delete(self, id_transaction: int):
        depenses = self.depense_service.get_by_transaction(id_transaction) or self.depense_service.get_depense_by_id(id_transaction) or []
        recettes = self.recette_service.get_by_transaction(id_transaction) or self.recette_service.get_recette_by_id(id_transaction) or []

        if not depenses and not recettes:
            raise NotFoundError(f"No transaction found for id {id_transaction}")

        for dep in depenses:
            self.depense_service.delete_depense(dep.id)
        for rec in recettes:
            self.recette_service.delete_recette(rec.id)