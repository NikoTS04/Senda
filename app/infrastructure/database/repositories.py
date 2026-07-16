from sqlalchemy.orm import Session
from app.domain.models import Escrito, Usuario, Comentario
from app.domain.repositories import IEscritoRepository, IUsuarioRepository, IComentarioRepository
from app.infrastructure.database.models import EscritoDB, UsuarioDB, ComentarioDB

class SqliteEscritoRepository(IEscritoRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Escrito | None:
        db_escrito = self.db.query(EscritoDB).filter(EscritoDB.id == id).first()
        return db_escrito.to_domain() if db_escrito else None

    def list_all(self, limit: int = 10, offset: int = 0, status: str | None = None) -> list[Escrito]:
        query = self.db.query(EscritoDB)
        if status:
            query = query.filter(EscritoDB.status == status)
        
        # Order chronologically descending
        db_escritos = query.order_by(EscritoDB.created_at.desc()).offset(offset).limit(limit).all()
        return [e.to_domain() for e in db_escritos]

    def create(self, escrito: Escrito) -> Escrito:
        db_escrito = EscritoDB.from_domain(escrito)
        self.db.add(db_escrito)
        self.db.commit()
        self.db.refresh(db_escrito)
        return db_escrito.to_domain()

    def update(self, escrito: Escrito) -> Escrito:
        db_escrito = self.db.query(EscritoDB).filter(EscritoDB.id == escrito.id).first()
        if not db_escrito:
            db_escrito = EscritoDB.from_domain(escrito)
            self.db.add(db_escrito)
        else:
            db_escrito.title = escrito.title
            db_escrito.content = escrito.content
            db_escrito.status = escrito.status
            db_escrito.tags = ",".join(escrito.tags) if escrito.tags else None
            db_escrito.updated_at = escrito.updated_at
        
        self.db.commit()
        self.db.refresh(db_escrito)
        return db_escrito.to_domain()

    def delete(self, id: int) -> None:
        db_escrito = self.db.query(EscritoDB).filter(EscritoDB.id == id).first()
        if db_escrito:
            self.db.delete(db_escrito)
            self.db.commit()

    def search(self, query: str, limit: int = 10, offset: int = 0) -> list[Escrito]:
        search_query = f"%{query}%"
        db_escritos = (
            self.db.query(EscritoDB)
            .filter(
                (EscritoDB.status == "publicado") &
                (
                    (EscritoDB.title.like(search_query)) |
                    (EscritoDB.content.like(search_query)) |
                    (EscritoDB.tags.like(search_query))
                )
            )
            .order_by(EscritoDB.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [e.to_domain() for e in db_escritos]


class SqliteUsuarioRepository(IUsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Usuario | None:
        db_user = self.db.query(UsuarioDB).filter(UsuarioDB.id == id).first()
        return db_user.to_domain() if db_user else None

    def get_by_email(self, email: str) -> Usuario | None:
        db_user = self.db.query(UsuarioDB).filter(UsuarioDB.email == email).first()
        return db_user.to_domain() if db_user else None

    def get_by_google_id(self, google_id: str) -> Usuario | None:
        db_user = self.db.query(UsuarioDB).filter(UsuarioDB.google_id == google_id).first()
        return db_user.to_domain() if db_user else None

    def create(self, usuario: Usuario) -> Usuario:
        db_user = UsuarioDB.from_domain(usuario)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user.to_domain()

    def update(self, usuario: Usuario) -> Usuario:
        db_user = self.db.query(UsuarioDB).filter(UsuarioDB.id == usuario.id).first()
        if not db_user:
            db_user = UsuarioDB.from_domain(usuario)
            self.db.add(db_user)
        else:
            db_user.email = usuario.email
            db_user.name = usuario.name
            db_user.role = usuario.role
            db_user.google_id = usuario.google_id
            db_user.updated_at = usuario.updated_at
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user.to_domain()


class SqliteComentarioRepository(IComentarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Comentario | None:
        db_comment = self.db.query(ComentarioDB).filter(ComentarioDB.id == id).first()
        return db_comment.to_domain() if db_comment else None

    def list_by_escrito(self, escrito_id: int) -> list[Comentario]:
        db_comments = (
            self.db.query(ComentarioDB)
            .filter(ComentarioDB.escrito_id == escrito_id)
            .order_by(ComentarioDB.created_at.asc())
            .all()
        )
        return [c.to_domain() for c in db_comments]

    def create(self, comentario: Comentario) -> Comentario:
        db_comment = ComentarioDB.from_domain(comentario)
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment.to_domain()

    def delete(self, id: int) -> None:
        db_comment = self.db.query(ComentarioDB).filter(ComentarioDB.id == id).first()
        if db_comment:
            self.db.delete(db_comment)
            self.db.commit()
