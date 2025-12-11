from app.models.db import open_conn as get_conn

def get_by_login(login: str):
    with get_conn() as c:
        r = c.execute(
            "SELECT * FROM Uzivatel WHERE login=?", 
            (login,)
        ).fetchone()
    return dict(r) if r else None

def get_by_id(id_uzivatele: int):
    with get_conn() as c:
        r = c.execute(
            "SELECT * FROM Uzivatel WHERE ID_uzivatele=?", 
            (id_uzivatele,)
        ).fetchone()
    return dict(r) if r else None

def create_user(login: str, hashed_password: str, id_role: int, jmeno: str, prijmeni: str):
    with get_conn() as c:
        cur = c.execute(
            """
            INSERT INTO Uzivatel(login, heslo, ID_role, jmeno, prijmeni)
            VALUES (?, ?, ?, ?, ?)
            """,
            (login, hashed_password, id_role, jmeno, prijmeni)
        )
        c.commit()

    return {
        "ID_uzivatele": cur.lastrowid,
        "login": login,
        "jmeno": jmeno,
        "prijmeni": prijmeni,
        "ID_role": id_role
    }

def set_new_password(id_uzivatele: int, hashed: str) -> int:
    with get_conn() as c:
        cur = c.execute(
            "UPDATE Uzivatel SET heslo=? WHERE ID_uzivatele=?",
            (hashed, id_uzivatele)
        )
        c.commit()
    return 1 if cur.rowcount > 0 else 0

def get_user_list():
    with get_conn() as c:
        r = c.execute(
            "SELECT ID_uzivatele, login, jmeno, prijmeni, ID_role FROM Uzivatel ORDER BY login"
        ).fetchall()
    return [dict(row) for row in r]

def list_mechanics():
    with get_conn() as c:
        r = c.execute(
            "SELECT ID_uzivatele, login, jmeno, prijmeni FROM Uzivatel WHERE ID_role = 2"
        ).fetchall()
    return [dict(row) for row in r]

def delete_user(id_uzivatele: int) -> bool:
    with get_conn() as c:
        cur = c.execute("DELETE FROM Uzivatel WHERE ID_uzivatele = ?", (id_uzivatele,))
        c.commit()
    return cur.rowcount > 0

def update_user_data(id_uzivatele: int, login: str, jmeno: str, prijmeni: str, id_role: int):
    with get_conn() as c:
        c.execute("""
            UPDATE Uzivatel 
            SET login = ?, jmeno = ?, prijmeni = ?, ID_role = ?
            WHERE ID_uzivatele = ?
        """, (login, jmeno, prijmeni, id_role, id_uzivatele))
        c.commit()