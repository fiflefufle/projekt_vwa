from app.repositories import uzivatel as repo
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
        rows = repo.list_users()
        return [UzivatelPublic(**r) for r in rows]

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