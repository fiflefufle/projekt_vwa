from app.repositories import servis as repo
from app.models.schemas import ServisPublic
from typing import List, Optional

class ServisService:
    """Service vrstva pro servisní práce"""

    def add_prace(
        self,
        id_objednavky: int,
        id_prace: int,
        id_mechanik: Optional[int] = None,
        cas: Optional[float] = None,
        cena: Optional[float] = None
    ) -> ServisPublic | None:
        """Přidá jednu práci k objednávce"""
        db_obj = repo.add_prace_to_objednavka(
            id_obj=id_objednavky,
            id_prace=id_prace,
            id_mechanik=id_mechanik,
            cas=cas,
            cena=cena
        )
        return ServisPublic(**db_obj) if db_obj else None

    def assign_mechanik(self, id_servisu: int, id_mechanik: int) -> bool:
        """Přiřadí mechanika k servisní práci (admin)"""
        return repo.assign_mechanik(id_servisu, id_mechanik)

    def list_for_objednavka(self, id_objednavky: int) -> List[ServisPublic]:
        """Vrátí všechny servisní úkony u objednávky"""
        rows = repo.get_servis_for_objednavka(id_objednavky)
        return [ServisPublic(**r) for r in rows]

    def remove_prace(self, id_servisu: int) -> bool:
        """Odstraní jednu servisní položku"""
        return repo.remove_prace(id_servisu)
