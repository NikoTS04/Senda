from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from app.infrastructure.api.schemas.auth import TokenResponse, DeveloperLoginRequest
from app.infrastructure.api.dependencies import (
    get_authenticate_google_user_use_case,
    get_developer_login_use_case
)
from app.use_cases.auth.auth_use_cases import (
    AuthenticateGoogleUserUseCase,
    DeveloperLoginUseCase
)
from app.infrastructure.auth_provider.google_client import GoogleOAuthClient

router = APIRouter(prefix="/auth", tags=["auth"])
google_client = GoogleOAuthClient()

@router.get("/login")
def google_login():
    auth_url = google_client.get_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def google_callback(
    code: str,
    use_case: AuthenticateGoogleUserUseCase = Depends(get_authenticate_google_user_use_case)
):
    try:
        user_info = await google_client.get_user_info_from_code(code)
        email = user_info.get("email")
        name = user_info.get("name", email.split("@")[0] if email else "Google User")
        google_id = user_info.get("sub")
        
        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google OAuth did not return sufficient user information."
            )
            
        result = use_case.execute(email=email, name=name, google_id=google_id)
        token = result["access_token"]
        # Redirect to frontend with the token
        return RedirectResponse(url=f"/?token={token}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de autenticacion Google: {str(e)}"
        )

@router.post("/developer-login", response_model=TokenResponse)
def developer_login(
    payload: DeveloperLoginRequest,
    use_case: DeveloperLoginUseCase = Depends(get_developer_login_use_case)
):
    try:
        return use_case.execute(email=payload.email, role=payload.role)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en login de desarrollador: {str(e)}"
        )
