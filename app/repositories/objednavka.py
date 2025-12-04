from app.models.db import open_conn


def create_objednavka(id_uzivatele: int, datum: str, znacka: str, poznamka: str = "") -> dict:
    """
    Vytvoří novou objednávku.
    ID_stavu = 1 (výchozí)
    """
    with open_conn() as c:
        cur = c.execute("""
            INSERT INTO Objednavka (ID_uzivatele, datum, znacka, poznamka, ID_stavu)
            VALUES (?, ?, ?, ?, 1)
        """, (id_uzivatele, datum, znacka, poznamka))
        c.commit()

    return {
        "ID_objednavky": cur.lastrowid,
        "ID_uzivatele": id_uzivatele,
        "datum": datum,
        "znacka": znacka,
        "poznamka": poznamka,
        "ID_stavu": 1
    }


def get_objednavka_by_id(id_obj: int) -> dict | None:
    with open_conn() as c:
        r = c.execute("""
            SELECT * FROM Objednavka WHERE ID_objednavky=?
        """, (id_obj,)).fetchone()

    return dict(r) if r else None


def list_objednavek() -> list[dict]:
    with open_conn() as c:
        rows = c.execute("""
            SELECT * FROM Objednavka ORDER BY datum ASC
        """).fetchall()

    return [dict(r) for r in rows]


def update_stav(id_obj: int, id_stavu: int) -> bool:
    with open_conn() as c:
        cur = c.execute("""
            UPDATE Objednavka
            SET ID_stavu = ?
            WHERE ID_objednavky = ?
        """, (id_stavu, id_obj))
        c.commit()

    return cur.rowcount > 0

    
def list_objednavky_for_user(id_uzivatele: int) -> list[dict]:
    """
    Vrátí všechny objednávky, které založil konkrétní uživatel.
    Seřazené podle data sestupně.
    """
    with open_conn() as c:
        rows = c.execute("""
            SELECT * FROM Objednavka
            WHERE ID_uzivatele = ?
            ORDER BY datum ASC
        """, (id_uzivatele,)).fetchall()

    return [dict(r) for r in rows]

def list_objednavky_for_mechanic(id_mechanik: int) -> list[dict]:
    """
    Vrátí objednávky, které mají alespoň jednu servisní položku
    přiřazenou danému mechanikovi.
    """
    with open_conn() as c:
        # DISTINCT je důležitý, aby se objednávka neopakovala, 
        # pokud v ní má mechanik více úkolů.
        rows = c.execute("""
            SELECT DISTINCT o.*
            FROM Objednavka o
            JOIN Servis s ON o.ID_objednavky = s.ID_objednavky
            WHERE s.ID_uzivatele = ?
            ORDER BY o.datum ASC
        """, (id_mechanik,)).fetchall()

    return [dict(r) for r in rows]

def delete_objednavka(id_obj: int):
    """Smaže objednávku a všechny její servisní položky."""
    with open_conn() as c:
        # 1. Nejdřív smažeme vazby v tabulce Servis
        c.execute("DELETE FROM Servis WHERE ID_objednavky = ?", (id_obj,))
        
        # 2. Pak smažeme samotnou objednávku
        c.execute("DELETE FROM Objednavka WHERE ID_objednavky = ?", (id_obj,))
        
        c.commit()