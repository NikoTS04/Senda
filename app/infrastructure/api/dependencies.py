from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories import SqliteEscritoRepository
from app.domain.repositories import IEscritoRepository
from app.use_cases.content.writings_use_cases import (
    CreateWritingUseCase,
    UpdateWritingUseCase,
    DeleteWritingUseCase,
    GetWritingUseCase,
    ListWritingsUseCase,
    SearchWritingsUseCase
)

def get_escrito_repository(db: Session = Depends(get_db)) -> IEscritoRepository:
    return SqliteEscritoRepository(db)

def get_create_writing_use_case(
    repo: IEscritoRepository = Depends(get_escrito_repository)
) -> CreateWritingUseCase:
    return CreateWritingUseCase(repo)

def get_update_writing_use_case(
    repo: IEscritoRepository = Depends(get_escrito_repository)
) -> UpdateWritingUseCase:
    return UpdateWritingUseCase(repo)

def get_delete_writing_use_case(
    repo: IEscritoRepository = Depends(get_escrito_repository)
) -> DeleteWritingUseCase:
    return DeleteWritingUseCase(repo)

def get_get_writing_use_case(
    repo: IEscritoRepository = Depends(get_escrito_repository)
) -> GetWritingUseCase:
    return GetWritingUseCase(repo)

def get_list_writings_use_case(
    repo: IEscritoRepository = Depends(get_escrito_repository)
) -> ListWritingsUseCase:
    return ListWritingsUseCase(repo)

def get_search_writings_use_case(
    repo: IEscritoRepository = Depends(get_escrito_repository)
) -> SearchWritingsUseCase:
    return SearchWritingsUseCase(repo)
