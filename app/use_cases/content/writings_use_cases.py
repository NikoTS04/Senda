from datetime import datetime
from app.domain.models import Escrito
from app.domain.repositories import IEscritoRepository
from app.domain.exceptions import EscritoNoEncontradoException

class CreateWritingUseCase:
    def __init__(self, repo: IEscritoRepository):
        self.repo = repo

    def execute(self, title: str, content: str, status: str) -> Escrito:
        escrito = Escrito(title=title, content=content, status=status)
        return self.repo.create(escrito)

class UpdateWritingUseCase:
    def __init__(self, repo: IEscritoRepository):
        self.repo = repo

    def execute(self, id: int, title: str, content: str, status: str) -> Escrito:
        escrito = self.repo.get_by_id(id)
        if not escrito:
            raise EscritoNoEncontradoException(id)
        
        escrito.title = title
        escrito.content = content
        escrito.status = status
        escrito.updated_at = datetime.now()
        return self.repo.update(escrito)

class DeleteWritingUseCase:
    def __init__(self, repo: IEscritoRepository):
        self.repo = repo

    def execute(self, id: int) -> None:
        escrito = self.repo.get_by_id(id)
        if not escrito:
            raise EscritoNoEncontradoException(id)
        self.repo.delete(id)

class GetWritingUseCase:
    def __init__(self, repo: IEscritoRepository):
        self.repo = repo

    def execute(self, id: int) -> Escrito:
        escrito = self.repo.get_by_id(id)
        if not escrito:
            raise EscritoNoEncontradoException(id)
        return escrito

class ListWritingsUseCase:
    def __init__(self, repo: IEscritoRepository):
        self.repo = repo

    def execute(self, limit: int = 10, offset: int = 0, status: str | None = None) -> list[Escrito]:
        return self.repo.list_all(limit=limit, offset=offset, status=status)

class SearchWritingsUseCase:
    def __init__(self, repo: IEscritoRepository):
        self.repo = repo

    def execute(self, query: str, limit: int = 10, offset: int = 0) -> list[Escrito]:
        return self.repo.search(query=query, limit=limit, offset=offset)
