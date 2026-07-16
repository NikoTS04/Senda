import httpx
from app.infrastructure.config import settings

class GoogleOAuthClient:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    def get_auth_url(self) -> str:
        return (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=openid%20email%20profile"
            f"&access_type=offline"
            f"&prompt=consent"
        )

    async def get_user_info_from_code(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            if token_res.status_code != 200:
                raise Exception("Failed to exchange code for token: " + token_res.text)
            
            tokens = token_res.json()
            access_token = tokens.get("access_token")
            
            user_info_res = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if user_info_res.status_code != 200:
                raise Exception("Failed to get user info: " + user_info_res.text)
                
            return user_info_res.json()
