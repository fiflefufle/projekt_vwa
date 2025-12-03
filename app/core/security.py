import time
import bcrypt
import jwt
from app.core.config import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_access_token(sub: str, roles: list[str]) -> str:
    """
    Vytvoří JWT token (řetězec), který obsahuje ID uživatele (sub) a role.
    """
    exp = int(time.time()) + 60 * settings.access_token_expire_minutes
    payload = {"sub": sub, "roles": roles, "exp": exp}
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token  # → řetězec

def decode_access_token(token: str) -> dict:
    """
    Ověří a dekóduje JWT token. Vyhodí výjimku při expiraci nebo neplatném tokenu.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expiroval")
    except jwt.InvalidTokenError:
        raise ValueError("Neplatný token")
