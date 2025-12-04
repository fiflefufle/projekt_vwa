from app.repositories import objednavka as repo
from app.repositories import servis as repo_servis
from app.repositories import stavobjednavky as repo_stav
from app.models.schemas import ObjednavkaPublic, ObjednavkaCreate
from app.models.schemas import ServisPublic
from typing import List

class ObjednavkaService:
    """Service vrstva pro objednávky"""

    # --- POMOCNÁ METODA PRO MAPOVÁNÍ (NOVÉ) ---
    def _map_servisy(self, servisy_db: list[dict]) -> list[ServisPublic]:
        return [
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

    def create(self, id_uzivatele: int, data: ObjednavkaCreate) -> ObjednavkaPublic:
        # ... (zůstává stejné) ...
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
            stav=stav_nazev,
            id_stavu=db_obj["ID_stavu"],  # <--- NOVÉ: doplňujeme ID
            servisy=[]
        )

    def list_all(self) -> list[ObjednavkaPublic]:
        rows = repo.list_objednavek()
        result = []
        for r in rows:
            stav_nazev = repo_stav.get_stav_by_id(r["ID_stavu"]) or "Neznámý stav"
            
            # ZDE POUŽIJEME NOVOU METODU
            servisy_db = repo_servis.list_servisy_for_objednavka(r["ID_objednavky"])
            servisy = self._map_servisy(servisy_db)

            result.append(
                ObjednavkaPublic(
                    id_objednavky=r["ID_objednavky"],
                    id_uzivatele=r["ID_uzivatele"],
                    datum=r["datum"],
                    znacka=r["znacka"],
                    poznamka=r.get("poznamka"),
                    stav=stav_nazev,
                    id_stavu=r["ID_stavu"],
                    servisy=servisy
                )
            )
        return result

    def list_for_user(self, id_uzivatele: int) -> List[ObjednavkaPublic]:
        rows = repo.list_objednavky_for_user(id_uzivatele)
        result = []
        for r in rows:
            stav_nazev = repo_stav.get_stav_by_id(r["ID_stavu"])
            
            # ZDE POUŽIJEME NOVOU METODU
            servisy_raw = repo_servis.list_servisy_for_objednavka(r["ID_objednavky"])
            servisy = self._map_servisy(servisy_raw)

            result.append(
                ObjednavkaPublic(
                    id_objednavky=r["ID_objednavky"],
                    id_uzivatele=r["ID_uzivatele"],
                    datum=r["datum"],
                    znacka=r["znacka"],
                    poznamka=r.get("poznamka"),
                    stav=stav_nazev if stav_nazev else "Neznámý stav",
                    id_stavu=r["ID_stavu"],
                    servisy=servisy
                )
            )
        return result

    def get(self, id_obj: int) -> ObjednavkaPublic | None:
        """Detail objednávky podle ID"""
        r = repo.get_objednavka_by_id(id_obj)
        return ObjednavkaPublic(**r) if r else None

    # ... (zbytek metod create, get, update_stav... zůstává stejný)
    
    # METODY PRO MECHANIKA A PRÁCI (Wrappery)
    # Tady je vidět, že vlastně jen přeposíláš volání do repo_servis.
    # To je v pořádku, ale pokud bys chtěl být důsledný, mohl bys používat ServisService.
    # Pro teď je ale lepší nechat to takhle, aby se nerozbilo volání v routeru.
    def update_stav(self, id_obj: int, id_stavu: int) -> bool:
        return repo.update_stav(id_obj, id_stavu)

    def add_prace(self, id_obj: int, id_prace: int, id_mechanik: int | None = None,
                  cas: float | None = None, cena: float | None = None):
        return repo_servis.add_prace_to_objednavka(
            id_obj=id_obj,
            id_prace=id_prace,
            id_mechanik=id_mechanik,
            cas=cas,
            cena=cena
        )
        
    def assign_mechanik(self, id_servisu: int, id_mechanik: int) -> bool:
        return repo_servis.assign_mechanik(id_servisu, id_mechanik)



    def list_for_mechanik(self, id_mechanik: int) -> list[ObjednavkaPublic]:
        """Seznam objednávek pouze pro konkrétního mechanika"""
        # Zde voláme novou funkci z repozitáře
        rows = repo.list_objednavky_for_mechanic(id_mechanik)
        
        result = []
        for r in rows:
            # Zbytek logiky je stejný jako v list_all - načteme stav a servisní položky
            stav_nazev = repo_stav.get_stav_by_id(r["ID_stavu"]) or "Neznámý stav"
            servisy_db = repo_servis.list_servisy_for_objednavka(r["ID_objednavky"])

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
                    id_stavu=r["ID_stavu"],
                    servisy=servisy
                )
            )
        return result


    def delete(self, id_obj: int):
        """Smaže objednávku, ale pouze pokud je Hotová (3) nebo Stornovaná (4)"""
        # Nejdřív načteme aktuální stav z DB
        obj = repo.get_objednavka_by_id(id_obj)
        if not obj:
            return # Objednávka neexistuje
            
        current_status = obj["ID_stavu"]
        
        # Kontrola stavu
        if current_status in [3, 4]:
            repo.delete_objednavka(id_obj)
        else:
            raise ValueError("Lze smazat pouze objednávky ve stavu Hotovo nebo Stornováno.")