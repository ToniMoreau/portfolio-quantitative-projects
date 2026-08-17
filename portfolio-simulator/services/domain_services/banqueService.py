from repositories import BanqueRepository
from domain.entities import Banque
from domain.errors import (
    ValidationError,
    BanqueNotFoundError,
    IntegrityError,
    MissingColumnError,
)


class BanqueService:
    def __init__(self, banque_repo: BanqueRepository):
        self.banque_repo = banque_repo
        self.banque_active_id: int | None = None

    def update_banque(self, banque_id, data):
        try:
            if banque_id is None:
                banque = self.banque_repo.create(data)
            else:
                banque = self.banque_repo.get_by_ID(banque_id)

            if banque is None:
                banque = self.banque_repo.create(data)
            else:
                self.banque_repo.update(banque.id, data)

            fresh_banque = self.banque_repo.get_by_ID(banque.id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Banque") from e

        if fresh_banque is None:
            raise IntegrityError("Banque introuvable après update")
        return fresh_banque

    def get_all_banques(self):
        try:
            return self.banque_repo.get_all_banques()
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Banque") from e

    def get_banque_by_name(self, banque_name):
        try:
            return self.banque_repo.get_by_name(banque_name)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Banque") from e

    def get_banque_by_id(self, banque_id):
        try:
            return self.banque_repo.get_by_ID(banque_id)
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Banque") from e

    def get_all_banque_names(self):
        try:
            return self.banque_repo.get_all_names().to_list()
        except KeyError as e:
            raise MissingColumnError(str(e), feuille="Banque") from e

    def set_banque_active(self, banque_id: int | None = None):
        self.banque_active_id = banque_id

    def delete_banque(self, banque_id: str):
        banque = self.get_banque_by_id(banque_id)
        if banque is None:
            raise BanqueNotFoundError(banque_id)
        self.banque_repo.delete(banque.id)