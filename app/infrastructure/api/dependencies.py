from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories import SqliteEscritoRepository, SqliteUsuarioRepository
from app.domain.repositories import IEscritoRepository, IUsuarioRepository
from app.use_cases.content.writings_use_cases import (
    CreateWritingUseCase,
    UpdateWritingUseCase,
    DeleteWritingUseCase,
    GetWritingUseCase,
    ListWritingsUseCase,
    SearchWritingsUseCase
)
from app.use_cases.auth.auth_use_cases import (
    AuthenticateGoogleUserUseCase,
    DeveloperLoginUseCase
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

def get_usuario_repository(db: Session = Depends(get_db)) -> IUsuarioRepository:
    return SqliteUsuarioRepository(db)

def get_authenticate_google_user_use_case(
    repo: IUsuarioRepository = Depends(get_usuario_repository)
) -> AuthenticateGoogleUserUseCase:
    return AuthenticateGoogleUserUseCase(repo)

def get_developer_login_use_case(
    repo: IUsuarioRepository = Depends(get_usuario_repository)
) -> DeveloperLoginUseCase:
    return DeveloperLoginUseCase(repo)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status
from app.infrastructure.security.jwt_service import decode_access_token

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security_optional)
) -> dict | None:
    if not credentials:
        return None
    return decode_access_token(credentials.credentials)

def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes. Requiere rol de Administrador."
        )
    return current_user
