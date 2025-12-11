from app.repositories import stavobjednavky as repo

class StavObjednavkyService:

    def list_all(self):
        return repo.list_stavy()

    def get_by_id(self, id_stavu: int):
        return repo.get_stav_by_id(id_stavu)
