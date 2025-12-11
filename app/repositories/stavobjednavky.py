from app.models.db import open_conn

def list_stavy() -> list[dict]:
    with open_conn() as c:
        rows = c.execute("SELECT ID_stavu AS id, nazev_stavu FROM StavObjednavky ORDER BY nazev_stavu").fetchall()
    return [dict(r) for r in rows]

def get_stav_by_id(id_stavu: int) -> str | None:
    with open_conn() as c:
        r = c.execute("SELECT nazev_stavu FROM StavObjednavky WHERE ID_stavu = ?", (id_stavu,)).fetchone()
    return r["nazev_stavu"] if r else None