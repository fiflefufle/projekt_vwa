from app.repositories import uzivatel as repo
from app.repositories import role as repo_role
from app.models.schemas import UzivatelPublic, UzivatelCreate
from app.core.security import hash_password
from typing import List

class UzivatelService:

    def create_user(self, data: UzivatelCreate) -> UzivatelPublic:
        hashed = hash_password(data.heslo)
        db_obj = repo.create_user(
            login=data.login,
            jmeno=data.jmeno,
            prijmeni=data.prijmeni,
            password_hash=hashed
        )
        return UzivatelPublic(**db_obj)

    def get_user(self, id_uzivatele: int) -> UzivatelPublic | None:
        r = repo.get_by_id(id_uzivatele)
        
        if not r:
            return None
        role_info = repo_role.get_role_by_id(r["ID_role"])
        role_nazev = role_info["nazev_role"] if role_info else "Neznámá"

        user_dict = {
            "id": r["ID_uzivatele"],
            "login": r["login"],
            "jmeno": r["jmeno"],
            "prijmeni": r["prijmeni"],
            "role": role_nazev
        }

        return UzivatelPublic(**user_dict)

    def list_users(self) -> List[UzivatelPublic]:
        rows = repo.get_user_list()
        result = []
        for r in rows:
            role_info = repo_role.get_role_by_id(r["ID_role"])
            role_nazev = role_info["nazev_role"] if role_info else "Neznámá"
            
            user_dict = {
                "id": r["ID_uzivatele"],
                "login": r["login"],
                "jmeno": r["jmeno"],
                "prijmeni": r["prijmeni"],
                "role": role_nazev
            }
            result.append(UzivatelPublic(**user_dict))
            
        return result

    def update_password(self, id_uzivatele: int, heslo: str) -> bool:
        hashed = hash_password(heslo)
        return repo.set_new_password(hashed, id_uzivatele)

    def update_name(self, id_uzivatele: int, jmeno: str, prijmeni: str) -> bool:
        return repo.set_new_user_full_name(jmeno, prijmeni, id_uzivatele)

    def list_mechanics(self):
        return repo.list_mechanics()

    def delete_user(self, id_uzivatele: int) -> bool:
        return repo.delete_user(id_uzivatele)

    def list_roles(self) -> list[dict]:
        return repo_role.list_roles()

    def update_user_complete(self, id_uzivatele: int, data: UzivatelCreate, new_role_id: int):
        repo.update_user_data(
            id_uzivatele=id_uzivatele,
            login=data.login,
            jmeno=data.jmeno,
            prijmeni=data.prijmeni,
            id_role=new_role_id
        )
        if data.heslo and len(data.heslo.strip()) > 0:
            hashed = hash_password(data.heslo)
            repo.set_new_password(id_uzivatele, hashed)