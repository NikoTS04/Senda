from pydantic import BaseModel, Field, ConfigDict

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class DeveloperLoginRequest(BaseModel):
    email: str
    role: str = Field("lector", pattern="^(admin|lector)$")
