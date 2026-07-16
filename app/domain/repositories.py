from abc import ABC, abstractmethod
from app.domain.models import Escrito, Usuario, Comentario

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


class IUsuarioRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Usuario | None:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Usuario | None:
        pass

    @abstractmethod
    def get_by_google_id(self, google_id: str) -> Usuario | None:
        pass

    @abstractmethod
    def create(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def update(self, usuario: Usuario) -> Usuario:
        pass


class IComentarioRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Comentario | None:
        pass

    @abstractmethod
    def list_by_escrito(self, escrito_id: int) -> list[Comentario]:
        pass

    @abstractmethod
    def create(self, comentario: Comentario) -> Comentario:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass
