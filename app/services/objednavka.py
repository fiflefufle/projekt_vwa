from app.repositories import objednavka as repo
from app.repositories import servis as repo_servis
from app.repositories import stavobjednavky as repo_stav
from app.repositories import prace as repo_prace
from app.models.schemas import ObjednavkaPublic, ObjednavkaCreate
from app.models.schemas import ServisPublic
from typing import List

HOURLY_RATE = 800.0

class ObjednavkaService:

    def _map_servisy(self, servisy_db: list[dict]) -> list[ServisPublic]:
        mapped = []
        for s in servisy_db:
            cas = s.get("cas")
            cena = s.get("cena")
            if cas is None:
                prace_info = repo_prace.get_by_id(s["ID_prace"])
                if prace_info and prace_info.get("odhad_hodin"):
                    cas = float(prace_info["odhad_hodin"])
            
            if cena is None and cas is not None:
                try:
                    cena = float(cas) * HOURLY_RATE
                except ValueError:
                    pass

            mapped.append(ServisPublic(
                id=s["ID_servisu"],
                id_objednavky=s["ID_objednavky"],
                id_mechanik=s.get("ID_uzivatele"),
                id_prace=s["ID_prace"],
                cas=cas,
                cena=cena,
                prace_nazev=s.get("prace_nazev")
            ))
        return mapped

    def create(self, id_uzivatele: int, data: ObjednavkaCreate) -> ObjednavkaPublic:
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
            id_stavu=db_obj["ID_stavu"],
            servisy=[]
        )

    def list_all(self) -> list[ObjednavkaPublic]:
        rows = repo.list_objednavek()
        result = []
        for r in rows:
            stav_nazev = repo_stav.get_stav_by_id(r["ID_stavu"]) or "Neznámý stav"
            servisy_db = repo_servis.list_servisy_for_objednavka(r["ID_objednavky"])
            servisy = self._map_servisy(servisy_db)
            sum_cena = sum((s.cena or 0) for s in servisy)
            sum_cas = sum((s.cas or 0) for s in servisy)

            result.append(
                ObjednavkaPublic(
                    id_objednavky=r["ID_objednavky"],
                    id_uzivatele=r["ID_uzivatele"],
                    datum=r["datum"],
                    znacka=r["znacka"],
                    poznamka=r.get("poznamka"),
                    stav=stav_nazev,
                    id_stavu=r["ID_stavu"],
                    servisy=servisy,
                    total_cena=sum_cena,
                    total_cas=sum_cas
                )
            )
        return result

    def list_for_user(self, id_uzivatele: int) -> List[ObjednavkaPublic]:
        rows = repo.list_objednavky_for_user(id_uzivatele)
        result = []
        for r in rows:
            stav_nazev = repo_stav.get_stav_by_id(r["ID_stavu"])
            servisy_raw = repo_servis.list_servisy_for_objednavka(r["ID_objednavky"])
            servisy = self._map_servisy(servisy_raw)
            sum_cena = sum((s.cena or 0) for s in servisy)
            sum_cas = sum((s.cas or 0) for s in servisy)

            result.append(
                ObjednavkaPublic(
                    id_objednavky=r["ID_objednavky"],
                    id_uzivatele=r["ID_uzivatele"],
                    datum=r["datum"],
                    znacka=r["znacka"],
                    poznamka=r.get("poznamka"),
                    stav=stav_nazev if stav_nazev else "Neznámý stav",
                    id_stavu=r["ID_stavu"],
                    servisy=servisy,
                    total_cena=sum_cena,
                    total_cas=sum_cas
                )
            )
        return result

    def get(self, id_obj: int) -> ObjednavkaPublic | None:
        r = repo.get_objednavka_by_id(id_obj)
        return ObjednavkaPublic(**r) if r else None

    def update_stav(self, id_obj: int, id_stavu: int) -> bool:
        return repo.update_stav(id_obj, id_stavu)

    def add_prace(self, id_obj: int, id_prace: int, id_mechanik: int | None = None,
                  cas: float | None = None, cena: float | None = None):
        if cas is None:
            prace_info = repo_prace.get_by_id(id_prace)
            if prace_info and prace_info.get("odhad_hodin"):
                cas = float(prace_info["odhad_hodin"])
                if cena is None:
                    cena = cas * HOURLY_RATE

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
        rows = repo.list_objednavky_for_mechanic(id_mechanik)
        result = []
        for r in rows:
            stav_nazev = repo_stav.get_stav_by_id(r["ID_stavu"]) or "Neznámý stav"
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
                    servisy=servisy,
                )
            )
        return result

    def delete(self, id_obj: int):
        obj = repo.get_objednavka_by_id(id_obj)
        if not obj:
            return
        current_status = obj["ID_stavu"]
        
        if current_status in [1, 3, 4]:
            repo.delete_objednavka(id_obj)
        else:
            raise ValueError("Lze smazat pouze objednávky ve stavu Hotovo nebo Stornováno.")

    def nacenit_praci(self, id_servisu: int, cas: float, cena: float = None):
        if cena is None or cena == 0:
            cena = cas * HOURLY_RATE
        repo_servis.update_servis_price_time(id_servisu, cas, cena)

    def assign_mechanik_to_order(self, id_obj: int, id_mechanik: int):
        repo_servis.assign_mechanik_to_whole_order(id_obj, id_mechanik)