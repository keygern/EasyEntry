import os
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "test")
_auth_scheme = HTTPBearer()

class TokenData:
    def __init__(self, sub: str):
        self.sub = sub

def verify_supabase_jwt(token: HTTPAuthorizationCredentials = Depends(_auth_scheme)) -> str:
    try:
        payload = jwt.decode(token.credentials, _JWT_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid JWT")
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user id missing")
    return user_id
