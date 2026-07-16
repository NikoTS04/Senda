from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.infrastructure.database.session import Base
from app.domain.models import Escrito

class EscritoDB(Base):
    __tablename__ = "escritos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="borrador")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_domain(self) -> Escrito:
        return Escrito(
            id=self.id,
            title=self.title,
            content=self.content,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_domain(cls, escrito: Escrito) -> "EscritoDB":
        return cls(
            id=escrito.id,
            title=escrito.title,
            content=escrito.content,
            status=escrito.status,
            created_at=escrito.created_at,
            updated_at=escrito.updated_at
        )
