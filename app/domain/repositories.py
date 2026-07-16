from abc import ABC, abstractmethod
from app.domain.models import Escrito

class IEscritoRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Escrito | None:
        pass

    @abstractmethod
    def list_all(self, limit: int = 10, offset: int = 0, status: str | None = None) -> list[Escrito]:
        pass

    @abstractmethod
    def create(self, escrito: Escrito) -> Escrito:
        pass

    @abstractmethod
    def update(self, escrito: Escrito) -> Escrito:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10, offset: int = 0) -> list[Escrito]:
        pass
