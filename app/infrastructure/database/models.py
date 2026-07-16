from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.infrastructure.database.session import Base
from app.domain.models import Escrito, Usuario, Comentario

class EscritoDB(Base):
    __tablename__ = "escritos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="borrador")
    tags = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_domain(self) -> Escrito:
        tag_list = [t.strip() for t in self.tags.split(",") if t.strip()] if self.tags else []
        return Escrito(
            id=self.id,
            title=self.title,
            content=self.content,
            status=self.status,
            tags=tag_list,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_domain(cls, escrito: Escrito) -> "EscritoDB":
        tag_str = ",".join(escrito.tags) if escrito.tags else None
        return cls(
            id=escrito.id,
            title=escrito.title,
            content=escrito.content,
            status=escrito.status,
            tags=tag_str,
            created_at=escrito.created_at,
            updated_at=escrito.updated_at
        )


class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="lector")
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_domain(self) -> Usuario:
        return Usuario(
            id=self.id,
            email=self.email,
            name=self.name,
            role=self.role,
            google_id=self.google_id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_domain(cls, usuario: Usuario) -> "UsuarioDB":
        return cls(
            id=usuario.id,
            email=usuario.email,
            name=usuario.name,
            role=usuario.role,
            google_id=usuario.google_id,
            created_at=usuario.created_at,
            updated_at=usuario.updated_at
        )


class ComentarioDB(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)
    escrito_id = Column(Integer, ForeignKey("escritos.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("UsuarioDB")

    def to_domain(self) -> Comentario:
        return Comentario(
            id=self.id,
            content=self.content,
            rating=self.rating,
            escrito_id=self.escrito_id,
            usuario_id=self.usuario_id,
            usuario_name=self.usuario.name if self.usuario else None,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_domain(cls, comentario: Comentario) -> "ComentarioDB":
        return cls(
            id=comentario.id,
            content=comentario.content,
            rating=comentario.rating,
            escrito_id=comentario.escrito_id,
            usuario_id=comentario.usuario_id,
            created_at=comentario.created_at,
            updated_at=comentario.updated_at
        )
