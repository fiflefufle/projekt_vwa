# app/repositories/role.py
from app.models.db import open_conn

def list_roles() -> list[dict]:
    with open_conn() as c:
        rows = c.execute("SELECT * FROM Role ORDER BY nazev_role").fetchall()
    return [dict(r) for r in rows]

def get_role_by_id(id_role: int):
    with open_conn() as c:
        r = c.execute(
            "SELECT * FROM Role WHERE ID_role = ?",
            (id_role,)
        ).fetchone()
    return dict(r) if r else None