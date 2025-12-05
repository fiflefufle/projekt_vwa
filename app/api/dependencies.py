from typing import Iterator
from fastapi import Depends, Cookie, HTTPException, status
from fastapi.responses import RedirectResponse
from app.models.db import open_conn
from app.core.security import decode_access_token
from app.repositories import uzivatel as repo_uzivatel
from app.repositories import role as repo_role

ACCESS_COOKIE = "access_token"

# ---------------------------------
# DB connection
# ---------------------------------
def get_conn() -> Iterator:
    with open_conn() as conn:
        yield conn


# ---------------------------------
# Aktuální uživatel podle JWT
# ---------------------------------
def get_current_user(token: str | None = Cookie(default=None, alias=ACCESS_COOKIE)):
    # 1. Pokud token chybí -> Login
    if not token:
        return RedirectResponse(url="/login", status_code=303)

    try:
        payload = decode_access_token(token)
    except ValueError:
        # 2. Pokud je token neplatný/expirovaný -> Login
        return RedirectResponse(url="/login", status_code=303)

    user_id = int(payload["sub"])
    user = repo_uzivatel.get_by_id(user_id)
    
    if not user:
        # 3. Uživatel smazán z DB, ale má token -> Login
        return RedirectResponse(url="/login", status_code=303)

    role_data = repo_role.get_role_by_id(user["ID_role"])
    if not role_data:
        raise HTTPException(status_code=500, detail="Role nenalezena")

    role_name = role_data["nazev_role"].lower()

    return {
        "id": user_id,
        "login": user["login"],
        "role": role_name
    }



# ---------------------------------
# Role-based ochrana
# ---------------------------------
async def require_admin(user = Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    if user["role"] != "admin":
        raise HTTPException(403, "Pouze pro adminy")
    return user


async def require_mechanik(user = Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    if user["role"] != "mechanik":
        raise HTTPException(403, "Pouze pro mechaniky")
    return user


async def require_user(user = Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    if user["role"] != "zákazník":
        raise HTTPException(403, "Pouze pro zákazníky")
    return user
