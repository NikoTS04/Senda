from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Escrito:
    title: str
    content: str
    status: str  # "borrador" | "publicado"
    id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Usuario:
    email: str
    name: str
    role: str  # "admin" | "lector"
    google_id: str | None = None
    id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Comentario:
    content: str
    escrito_id: int
    usuario_id: int
    rating: int | None = None
    id: int | None = None
    usuario_name: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
