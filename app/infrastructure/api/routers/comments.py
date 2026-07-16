from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.exceptions import (
    EscritoNoEncontradoException,
    ComentarioNoEncontradoException,
    AccesoDenegadoException
)
from app.infrastructure.api.schemas.comments import CommentCreate, CommentResponse
from app.infrastructure.api.dependencies import (
    get_create_comment_use_case,
    get_list_comments_use_case,
    get_delete_comment_use_case,
    get_current_user
)
from app.use_cases.feedback.comments_use_cases import (
    CreateCommentUseCase,
    ListCommentsUseCase,
    DeleteCommentUseCase
)

router = APIRouter(tags=["comments"])

@router.post("/writings/{writing_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    writing_id: int,
    payload: CommentCreate,
    current_user: dict = Depends(get_current_user),
    use_case: CreateCommentUseCase = Depends(get_create_comment_use_case)
):
    try:
        usuario_id = int(current_user.get("sub"))
        comentario = use_case.execute(
            content=payload.content,
            escrito_id=writing_id,
            usuario_id=usuario_id,
            rating=payload.rating
        )
        return comentario
    except EscritoNoEncontradoException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/writings/{writing_id}/comments", response_model=list[CommentResponse])
def list_comments(
    writing_id: int,
    use_case: ListCommentsUseCase = Depends(get_list_comments_use_case)
):
    try:
        return use_case.execute(escrito_id=writing_id)
    except EscritoNoEncontradoException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: DeleteCommentUseCase = Depends(get_delete_comment_use_case)
):
    try:
        usuario_id = int(current_user.get("sub"))
        role = current_user.get("role")
        use_case.execute(
            comment_id=comment_id,
            current_user_id=usuario_id,
            current_user_role=role
        )
    except ComentarioNoEncontradoException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccesoDenegadoException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
