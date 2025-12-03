from app.repositories import stavobjednavky as repo

class StavObjednavkyService:
    """Service vrstva pro stavy objednávek"""

    def list_all(self):
        """Vrátí seznam všech stavů objednávek"""
        return repo.list_stavy()

    def get_by_id(self, id_stavu: int):
        """Vrátí konkrétní stav podle ID"""
        return repo.get_stav_by_id(id_stavu)
