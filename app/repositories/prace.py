from app.models.db import open_conn

def list_praci() -> list[dict]:
    with open_conn() as c:
        rows = c.execute("SELECT * FROM Prace ORDER BY nazev_prace").fetchall()
    return [dict(r) for r in rows]

def get_by_id(id_prace: int) -> dict | None:
    with open_conn() as c:
        r = c.execute("SELECT * FROM Prace WHERE ID_prace = ?", (id_prace,)).fetchone()
    return dict(r) if r else None