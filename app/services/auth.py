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
        login = login.lower() 
        u = get_by_login(login)
        if not u or not verify_password(password, u["heslo"]):
            raise ValueError("Neplatné přihlášení")

        role = get_role_by_id(u["ID_role"])

        token = create_access_token(
            sub=str(u["ID_uzivatele"]),
            roles=[role["nazev_role"].lower()] if role else []
        )

        return token


    def user_data(self, user_id: int) -> dict:
        return get_by_id(user_id)


    def pridej_uzivatele(self, login: str, jmeno: str, prijmeni: str,
                        password: str, id_role: int):
        login = login.lower() 
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
        hashed = hash_password(password)
        return set_new_password(user_id, hashed)
