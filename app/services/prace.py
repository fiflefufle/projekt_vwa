# app/services/prace.py
from app.repositories import prace as repo

class PraceService:
    
    def list_all(self) -> list[dict]:
        return repo.list_praci()
