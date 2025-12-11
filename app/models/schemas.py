from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --------------------------
# UŽIVATEL
# --------------------------
class UzivatelPublic(BaseModel):
    id: int
    login: str
    jmeno: str
    prijmeni: str
    role: str

class UzivatelCreate(BaseModel):
    login: str
    heslo: str
    jmeno: str
    prijmeni: str

class UzivatelUpdatePassword(BaseModel):
    heslo: str

class UzivatelUpdateName(BaseModel):
    jmeno: str
    prijmeni: str


# --------------------------
# ROLE
# --------------------------
class Role(BaseModel):
    id: int
    nazev_role: str


# --------------------------
# PRACE
# --------------------------
class Prace(BaseModel):
    id: int
    nazev_prace: str


# --------------------------
# STAV OBJEDNAVKY
# --------------------------
class StavObjednavky(BaseModel):
    id: int
    nazev_stavu: str


# --------------------------
# SERVIS
# --------------------------
class ServisPublic(BaseModel):
    id: int
    id_objednavky: int
    id_mechanik: Optional[int] = None
    id_prace: int
    cas: Optional[float] = None
    cena: Optional[float] = None
    prace_nazev: Optional[str] = None


# --------------------------
# OBJEDNAVKA
# --------------------------
class ObjednavkaPublic(BaseModel):
    id_objednavky: int
    id_uzivatele: int
    datum: datetime
    znacka: str
    poznamka: Optional[str] = None
    id_stavu: int
    stav: str
    servisy: list[ServisPublic] = []
    total_cena: float = 0.0
    total_cas: float = 0.0


class ObjednavkaCreate(BaseModel):
    datum: datetime
    znacka: str
    poznamka: Optional[str] = None