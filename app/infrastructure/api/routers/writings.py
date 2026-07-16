from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from app.domain.exceptions import EscritoNoEncontradoException
from app.infrastructure.api.schemas.writings import WritingCreate, WritingUpdate, WritingResponse
from app.infrastructure.api.dependencies import (
    get_create_writing_use_case,
    get_update_writing_use_case,
    get_delete_writing_use_case,
    get_get_writing_use_case,
    get_list_writings_use_case,
    get_search_writings_use_case,
    get_current_admin,
    get_current_user_optional
)
from app.use_cases.content.writings_use_cases import (
    CreateWritingUseCase,
    UpdateWritingUseCase,
    DeleteWritingUseCase,
    GetWritingUseCase,
    ListWritingsUseCase,
    SearchWritingsUseCase
)

router = APIRouter(prefix="/writings", tags=["writings"])

@router.post("/", response_model=WritingResponse, status_code=http_status.HTTP_201_CREATED)
def create_writing(
    payload: WritingCreate,
    admin_user: dict = Depends(get_current_admin),
    use_case: CreateWritingUseCase = Depends(get_create_writing_use_case)
):
    try:
        escrito = use_case.execute(
            title=payload.title,
            content=payload.content,
            status=payload.status
        )
        return escrito
    except Exception as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=list[WritingResponse])
def list_writings(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str | None = Query(None, pattern="^(borrador|publicado)$"),
    current_user: dict | None = Depends(get_current_user_optional),
    use_case: ListWritingsUseCase = Depends(get_list_writings_use_case)
):
    is_admin = current_user and current_user.get("role") == "admin"
    if status == "borrador" and not is_admin:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para ver borradores."
        )
    
    if not status and not is_admin:
        status = "publicado"
        
    return use_case.execute(limit=limit, offset=offset, status=status)

@router.get("/search", response_model=list[WritingResponse])
def search_writings(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case: SearchWritingsUseCase = Depends(get_search_writings_use_case)
):
    return use_case.execute(query=q, limit=limit, offset=offset)

@router.get("/{writing_id}", response_model=WritingResponse)
def get_writing(
    writing_id: int,
    current_user: dict | None = Depends(get_current_user_optional),
    use_case: GetWritingUseCase = Depends(get_get_writing_use_case)
):
    try:
        escrito = use_case.execute(id=writing_id)
        if escrito.status == "borrador":
            is_admin = current_user and current_user.get("role") == "admin"
            if not is_admin:
                raise HTTPException(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    detail="Permisos insuficientes para ver este borrador."
                )
        return escrito
    except EscritoNoEncontradoException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/{writing_id}", response_model=WritingResponse)
def update_writing(
    writing_id: int,
    payload: WritingUpdate,
    admin_user: dict = Depends(get_current_admin),
    use_case: UpdateWritingUseCase = Depends(get_update_writing_use_case)
):
    try:
        return use_case.execute(
            id=writing_id,
            title=payload.title,
            content=payload.content,
            status=payload.status
        )
    except EscritoNoEncontradoException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{writing_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_writing(
    writing_id: int,
    admin_user: dict = Depends(get_current_admin),
    use_case: DeleteWritingUseCase = Depends(get_delete_writing_use_case)
):
    try:
        use_case.execute(id=writing_id)
    except EscritoNoEncontradoException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))
