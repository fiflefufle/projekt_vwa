from app.repositories import objednavka as repo
from app.repositories import servis as repo_servis
from app.repositories import stavobjednavky as repo_stav
from app.models.schemas import ObjednavkaPublic, ObjednavkaCreate
from app.models.schemas import ServisPublic
from typing import List

class ObjednavkaService:
    """Service vrstva pro objednávky"""

    def create(self, id_uzivatele: int, data: ObjednavkaCreate) -> ObjednavkaPublic:
        """Vytvoří novou objednávku pro zákazníka"""
        db_obj = repo.create_objednavka(
            id_uzivatele=id_uzivatele,
            datum=data.datum,
            znacka=data.znacka,
            poznamka=data.poznamka
        )
        stav_nazev = repo_stav.get_stav_by_id(db_obj["ID_stavu"])
        return ObjednavkaPublic(
            id_objednavky=db_obj["ID_objednavky"],
            id_uzivatele=db_obj["ID_uzivatele"],
            datum=db_obj["datum"],
            znacka=db_obj["znacka"],
            poznamka=db_obj.get("poznamka"),
            stav=stav_nazev
        )

    def list_all(self) -> list[ObjednavkaPublic]:
        """Seznam všech objednávek pro admina/technika"""
        rows = repo.list_objednavek()  # načtení objednávek
        result = []
        for r in rows:
            # získáme název stavu podle ID
            stav_nazev = repo_stav.get_stav_by_id(r["ID_stavu"]) or "Neznámý stav"

            # načtení všech servisních položek pro objednávku
            servisy_db = repo_servis.list_servisy_for_objednavka(r["ID_objednavky"])

            # mapování servisních položek na Pydantic model ServisPublic
            servisy = [
                ServisPublic(
                    id=s["ID_servisu"],
                    id_objednavky=s["ID_objednavky"],
                    id_mechanik=s.get("ID_uzivatele"),
                    id_prace=s["ID_prace"],
                    cas=s.get("cas"),
                    cena=s.get("cena"),
                    prace_nazev=s.get("prace_nazev")
                )
                for s in servisy_db
            ]

            result.append(
                ObjednavkaPublic(
                    id_objednavky=r["ID_objednavky"],
                    id_uzivatele=r["ID_uzivatele"],
                    datum=r["datum"],
                    znacka=r["znacka"],
                    poznamka=r.get("poznamka"),
                    stav=stav_nazev,
                    servisy=servisy  # seznam servisních položek
                )
            )
        return result

    def list_for_user(self, id_uzivatele: int) -> List[ObjednavkaPublic]:
        """Seznam objednávek pouze pro konkrétního uživatele"""
        rows = repo.list_objednavky_for_user(id_uzivatele)
        result = []
        for r in rows:
            # získáme název stavu podle ID
            stav_nazev = repo_stav.get_stav_by_id(r["ID_stavu"])
            servisy_raw = repo_servis.list_servisy_for_objednavka(r["ID_objednavky"])
            servisy = [
                ServisPublic(
                    id=s["ID_servisu"],
                    id_objednavky=s["ID_objednavky"],
                    id_uzivatele=s.get("ID_uzivatele"),
                    id_prace=s["ID_prace"],
                    cas=s.get("cas"),
                    cena=s.get("cena"),
                    prace_nazev=s.get("prace_nazev")
                )
                for s in servisy_raw
            ]

            result.append(
                ObjednavkaPublic(
                    id_objednavky=r["ID_objednavky"],
                    id_uzivatele=r["ID_uzivatele"],
                    datum=r["datum"],
                    znacka=r["znacka"],
                    poznamka=r.get("poznamka"),
                    stav=stav_nazev if stav_nazev else "Neznámý stav",
                    servisy=servisy
                )
            )
        return result


    def get(self, id_obj: int) -> ObjednavkaPublic | None:
        """Detail objednávky podle ID"""
        r = repo.get_objednavka_by_id(id_obj)
        return ObjednavkaPublic(**r) if r else None

    def update_stav(self, id_obj: int, id_stavu: int) -> bool:
        """Změní stav objednávky (mechanik/admin)"""
        return repo.update_stav(id_obj, id_stavu)

    def add_prace(self, id_obj: int, id_prace: int, id_mechanik: int | None = None,
                  cas: float | None = None, cena: float | None = None):
        """
        Přiřadí práci k objednávce pomocí repo/servis.
        """
        return repo_servis.add_prace_to_objednavka(
            id_obj=id_obj,
            id_prace=id_prace,
            id_mechanik=id_mechanik,
            cas=cas,
            cena=cena
        )
        
    def assign_mechanik(self, id_servisu: int, id_mechanik: int) -> bool:
        """Přiřadí mechanika k servisní práci"""
        return repo_servis.assign_mechanik(id_servisu, id_mechanik)