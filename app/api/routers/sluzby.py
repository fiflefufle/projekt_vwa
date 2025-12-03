# app/api/routers/sluzby.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.models.db import open_conn

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/sluzby", response_class=HTMLResponse)
def zobraz_sluzby(request: Request):
    """
    Zobrazí všechny služby (práce), které autoservis nabízí
    """
    with open_conn() as conn:
        rows = conn.execute("SELECT nazev_prace FROM Prace ORDER BY nazev_prace").fetchall()
        prace = [r["nazev_prace"] for r in rows]

    return templates.TemplateResponse("sluzby.html", {"request": request, "prace": prace})
