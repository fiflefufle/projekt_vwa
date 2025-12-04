from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime



#
#
#   !!!ASI BY BYLO DOBRÝ UDĚLAT NĚCO JAK MÁ TURČÍNEK OHLEDNĚ MIN LENGTH AŤ NEJSOU PRÁZDNÝ ŘETĚZCE!!!
#
#


# --------------------------
# UŽIVATEL
# --------------------------
class UzivatelPublic(BaseModel):
    """To, co API vrací o uživateli"""
    id: int
    login: str
    jmeno: str
    prijmeni: str
    role: str  # pro jednodušší projekt jen 1 role, nebo list[str] pro víc rolí

class UzivatelCreate(BaseModel):
    """Co API přijímá při registraci nového uživatele"""
    login: str
    heslo: str
    jmeno: str
    prijmeni: str

class UzivatelUpdatePassword(BaseModel):
    """Payload pro změnu hesla"""
    heslo: str

class UzivatelUpdateName(BaseModel):
    """Payload pro změnu jména"""
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
    servisy: list[ServisPublic] = []  # default prázdný seznam


class ObjednavkaCreate(BaseModel):
    datum: datetime
    znacka: str
    poznamka: Optional[str] = None


# --------------------------
# SERVIS
# --------------------------
class ServisPublic(BaseModel):
    id: int
    id_objednavky: int
    id_mechanik: Optional[int] = None  # mechanik – bude mapováno z DB sloupce ID_uzivatele
    id_prace: int
    cas: Optional[float] = None
    cena: Optional[float] = None
    prace_nazev: Optional[str] = None

