from app.domain.models import Comentario
from app.domain.repositories import IComentarioRepository, IEscritoRepository
from app.domain.exceptions import (
    ComentarioNoEncontradoException,
    EscritoNoEncontradoException,
    AccesoDenegadoException
)

class CreateCommentUseCase:
    def __init__(self, comment_repo: IComentarioRepository, escrito_repo: IEscritoRepository):
        self.comment_repo = comment_repo
        self.escrito_repo = escrito_repo

    def execute(self, content: str, escrito_id: int, usuario_id: int, rating: int | None = None) -> Comentario:
        # Verify writing exists
        escrito = self.escrito_repo.get_by_id(escrito_id)
        if not escrito:
            raise EscritoNoEncontradoException(escrito_id)
            
        comentario = Comentario(
            content=content,
            escrito_id=escrito_id,
            usuario_id=usuario_id,
            rating=rating
        )
        return self.comment_repo.create(comentario)

class ListCommentsUseCase:
    def __init__(self, comment_repo: IComentarioRepository, escrito_repo: IEscritoRepository):
        self.comment_repo = comment_repo
        self.escrito_repo = escrito_repo

    def execute(self, escrito_id: int) -> list[Comentario]:
        # Verify writing exists
        escrito = self.escrito_repo.get_by_id(escrito_id)
        if not escrito:
            raise EscritoNoEncontradoException(escrito_id)
            
        return self.comment_repo.list_by_escrito(escrito_id)

class DeleteCommentUseCase:
    def __init__(self, comment_repo: IComentarioRepository):
        self.comment_repo = comment_repo

    def execute(self, comment_id: int, current_user_id: int, current_user_role: str) -> None:
        comentario = self.comment_repo.get_by_id(comment_id)
        if not comentario:
            raise ComentarioNoEncontradoException(comment_id)
            
        # User must be comment author or admin
        is_author = comentario.usuario_id == current_user_id
        is_admin = current_user_role == "admin"
        
        if not is_author and not is_admin:
            raise AccesoDenegadoException("No tiene permisos para eliminar este comentario.")
            
        self.comment_repo.delete(comment_id)
