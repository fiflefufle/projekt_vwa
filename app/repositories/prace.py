from app.models.db import open_conn

def list_praci() -> list[dict]:
    with open_conn() as c:
        rows = c.execute("SELECT * FROM Prace ORDER BY nazev_prace").fetchall()
    return [dict(r) for r in rows]