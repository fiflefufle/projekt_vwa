from app.models.db import open_conn

def add_prace_to_objednavka(id_obj: int, id_prace: int, id_mechanik: int | None = None,
                            cas: float | None = None, cena: float | None = None) -> dict | None:
    with open_conn() as c:
        try:
            cur = c.execute("""
                INSERT INTO Servis (ID_objednavky, ID_prace, ID_uzivatele, cas, cena)
                VALUES (?, ?, ?, ?, ?)
            """, (id_obj, id_prace, id_mechanik, cas, cena))
            c.commit()
        except Exception:
            return None

    return {
        "ID_servisu": cur.lastrowid,
        "ID_objednavky": id_obj,
        "ID_prace": id_prace,
        "ID_uzivatele": id_mechanik,
        "cas": cas,
        "cena": cena
    }


def assign_mechanik(id_servisu: int, id_mechanik: int) -> bool:
    with open_conn() as c:
        cur = c.execute("""
            UPDATE Servis
            SET ID_uzivatele = ?
            WHERE ID_servisu = ?
        """, (id_mechanik, id_servisu))
        c.commit()

    return cur.rowcount > 0


def remove_prace(id_servisu: int) -> bool:
    with open_conn() as c:
        cur = c.execute("""
            DELETE FROM Servis WHERE ID_servisu = ?
        """, (id_servisu,))
        c.commit()

    return cur.rowcount > 0

def list_servisy_for_objednavka(id_obj: int) -> list[dict]:
    with open_conn() as c:
        rows = c.execute("""
            SELECT 
                s.ID_servisu,
                s.ID_objednavky,
                s.ID_uzivatele,
                s.ID_prace,
                s.cas,
                s.cena,
                p.nazev_prace AS prace_nazev
            FROM Servis s
            LEFT JOIN Prace p ON s.ID_prace = p.ID_prace
            WHERE s.ID_objednavky = ?
        """, (id_obj,)).fetchall()
    return [dict(r) for r in rows]

def update_servis_price_time(id_servisu: int, cas: float | None, cena: float | None):
    with open_conn() as c:
        c.execute("""
            UPDATE Servis
            SET cas = ?, cena = ?
            WHERE ID_servisu = ?
        """, (cas, cena, id_servisu))
        c.commit()
    
def assign_mechanik_to_whole_order(id_obj: int, id_mechanik: int):
    with open_conn() as c:
        c.execute("""
            UPDATE Servis
            SET ID_uzivatele = ?
            WHERE ID_objednavky = ?
        """, (id_mechanik, id_obj))
        c.commit()