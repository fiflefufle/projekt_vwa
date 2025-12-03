# app/services/prace.py
from app.repositories import prace as repo

class PraceService:
    """Service vrstva pro práce"""
    
    def list_all(self) -> list[dict]:
        """Vrátí všechny práce"""
        return repo.list_praci()
