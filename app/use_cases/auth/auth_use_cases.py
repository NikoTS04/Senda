from datetime import datetime
from app.domain.models import Usuario
from app.domain.repositories import IUsuarioRepository
from app.infrastructure.config import settings
from app.infrastructure.security.jwt_service import create_access_token

class AuthenticateGoogleUserUseCase:
    def __init__(self, user_repo: IUsuarioRepository):
        self.user_repo = user_repo

    def execute(self, email: str, name: str, google_id: str) -> dict:
        # Check by google_id
        usuario = self.user_repo.get_by_google_id(google_id)
        
        # If not found, check by email
        if not usuario:
            usuario = self.user_repo.get_by_email(email)
            if usuario:
                # Link google_id
                usuario.google_id = google_id
                usuario = self.user_repo.update(usuario)
            else:
                # Determine role
                role = "admin" if email == settings.ADMIN_EMAIL else "lector"
                usuario = Usuario(
                    email=email,
                    name=name,
                    role=role,
                    google_id=google_id
                )
                usuario = self.user_repo.create(usuario)
        else:
            # Update name if changed
            if usuario.name != name:
                usuario.name = name
                usuario = self.user_repo.update(usuario)

        # Generate JWT
        token_data = {
            "sub": str(usuario.id),
            "email": usuario.email,
            "role": usuario.role,
            "name": usuario.name
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": usuario.id,
                "email": usuario.email,
                "name": usuario.name,
                "role": usuario.role
            }
        }

class DeveloperLoginUseCase:
    def __init__(self, user_repo: IUsuarioRepository):
        self.user_repo = user_repo

    def execute(self, email: str, role: str) -> dict:
        usuario = self.user_repo.get_by_email(email)
        if not usuario:
            usuario = Usuario(
                email=email,
                name=f"Dev User {role.capitalize()}",
                role=role,
                google_id=f"dev-oauth-{email}"
            )
            usuario = self.user_repo.create(usuario)
        elif usuario.role != role:
            # Update role if developer requested a different role for testing
            usuario.role = role
            usuario = self.user_repo.update(usuario)
            
        token_data = {
            "sub": str(usuario.id),
            "email": usuario.email,
            "role": usuario.role,
            "name": usuario.name
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": usuario.id,
                "email": usuario.email,
                "name": usuario.name,
                "role": usuario.role
            }
        }
