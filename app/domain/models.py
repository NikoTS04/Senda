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
