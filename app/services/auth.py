from app.core.security import verify_password, create_access_token, hash_password
from app.repositories.uzivatel import (
    get_by_login,
    get_by_id,
    create_user,
    set_new_password
)
from app.repositories.role import get_role_by_id


class AuthService:

    def login(self, login: str, password: str) -> str:
        """Ověří uživatele podle loginu a hesla (case-insensitive)."""
        login = login.lower()  # převede vstup na malá písmena
        u = get_by_login(login)
        if not u or not verify_password(password, u["heslo"]):
            raise ValueError("Neplatné přihlášení")

        role = get_role_by_id(u["ID_role"])   # jedna role podle DB struktury

        token = create_access_token(
            sub=str(u["ID_uzivatele"]),
            roles=[role["nazev_role"].lower()] if role else []
        )

        return token


    def user_data(self, user_id: int) -> dict:
        """Vrátí data přihlášeného uživatele."""
        return get_by_id(user_id)


    def pridej_uzivatele(self, login: str, jmeno: str, prijmeni: str,
                        password: str, id_role: int):
        """Vytvoří nového uživatele (login je case-insensitive)."""
        login = login.lower()  # uložíme vždy malé písmeno
        if get_by_login(login):
            return {"chyba": "Login již existuje"}

        hashed = hash_password(password)

        return create_user(
            login=login,
            hashed_password=hashed,
            id_role=id_role,
            jmeno=jmeno,
            prijmeni=prijmeni
        )


    def set_new_password(self, user_id: int, password: str):
        """Nastaví nové heslo uživateli."""
        hashed = hash_password(password)
        return set_new_password(user_id, hashed)
