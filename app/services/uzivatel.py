from app.repositories import uzivatel as repo
from app.repositories import role as repo_role
from app.models.schemas import UzivatelPublic, UzivatelCreate
from app.core.security import hash_password
from typing import List

class UzivatelService:
    """Service vrstva pro uživatele"""

    def create_user(self, data: UzivatelCreate) -> UzivatelPublic:
        """Vytvoří nového uživatele s hashovaným heslem"""
        hashed = hash_password(data.heslo)
        db_obj = repo.create_user(
            login=data.login,
            jmeno=data.jmeno,
            prijmeni=data.prijmeni,
            password_hash=hashed
        )
        return UzivatelPublic(**db_obj)

    def get_user(self, id_uzivatele: int) -> UzivatelPublic | None:
        """Detail uživatele"""
        r = repo.get_user_by_id(id_uzivatele)
        return UzivatelPublic(**r) if r else None

    def list_users(self) -> List[UzivatelPublic]:
        """Seznam všech uživatelů (pro admina)"""
        rows = repo.get_user_list()
        result = []
        for r in rows:
            # Musíme získat název role podle ID_role
            role_info = repo_role.get_role_by_id(r["ID_role"])
            role_nazev = role_info["nazev_role"] if role_info else "Neznámá"
            
            # Vytvoříme slovník pro Pydantic model
            # Mapujeme ID_uzivatele -> id
            user_dict = {
                "id": r["ID_uzivatele"],
                "login": r["login"],
                "jmeno": r["jmeno"],
                "prijmeni": r["prijmeni"],
                "role": role_nazev  # Zde dosadíme string
            }
            result.append(UzivatelPublic(**user_dict))
            
        return result

    def update_password(self, id_uzivatele: int, heslo: str) -> bool:
        """Změní heslo uživatele"""
        hashed = hash_password(heslo)
        return repo.set_new_password(hashed, id_uzivatele)

    def update_name(self, id_uzivatele: int, jmeno: str, prijmeni: str) -> bool:
        """Změní jméno a příjmení uživatele"""
        return repo.set_new_user_full_name(jmeno, prijmeni, id_uzivatele)

    def list_mechanics(self):
        """Vrátí seznam všech mechaniků"""
        return repo.list_mechanics()

    def delete_user(self, id_uzivatele: int) -> bool:
        """Smaže uživatele podle ID"""
        return repo.delete_user(id_uzivatele)

    def list_roles(self) -> list[dict]:
        """Vrátí seznam všech rolí (pro formulář na přidání uživatele)"""
        return repo_role.list_roles()