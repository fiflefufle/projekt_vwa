from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.models.db import open_conn

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/sluzby", response_class=HTMLResponse)
def zobraz_sluzby(request: Request):
    with open_conn() as conn:
        rows = conn.execute("SELECT * FROM Prace ORDER BY nazev_prace").fetchall()
        prace = [dict(r) for r in rows]

    return templates.TemplateResponse("sluzby.html", {"request": request, "prace": prace})