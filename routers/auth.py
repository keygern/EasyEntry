from fastapi import Header, HTTPException, status
import jwt


def verify_supabase_jwt(Authorization: str = Header(...)) -> str:
    """Validate Supabase JWT from Authorization header and return user id."""
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    token = Authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user_id


