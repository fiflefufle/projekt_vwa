from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.api.dependencies import require_user
from app.services.objednavka import ObjednavkaService
from app.services.prace import PraceService
from app.models.schemas import ObjednavkaCreate
from datetime import datetime
from typing import List

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

obj_service = ObjednavkaService()
prace_service = PraceService()

@router.get("/objednavka/nova", response_class=HTMLResponse)
def nova_objednavka_form(request: Request, user: dict = Depends(require_user)):
    prace = prace_service.list_all()
    return templates.TemplateResponse(
        "objednavka_nova.html",
        {"request": request, "prace": prace}
    )

@router.post("/objednavka/nova")
def nova_objednavka_submit(
    request: Request,
    user: dict = Depends(require_user),
    datum: str = Form(...),
    znacka: str = Form(...),
    poznamka: str = Form(""),
    id_prace: List[int] = Form(...)
):
    try:
        datum_obj = datetime.fromisoformat(datum)
    except ValueError:
        return _vratit_formular_s_chybou(request, user, "Neplatný formát data.", datum, znacka, poznamka)

    if datum_obj < datetime.now():
        return _vratit_formular_s_chybou(request, user, "Nelze objednat termín v minulosti.", datum, znacka, poznamka)

    if datum_obj.weekday() >= 5:
         return _vratit_formular_s_chybou(request, user, "O víkendu máme zavřeno.", datum, znacka, poznamka)
         
    start_hour = 8
    end_hour = 16
    if not (start_hour <= datum_obj.hour < end_hour):
        return _vratit_formular_s_chybou(request, user, f"Máme otevřeno pouze {start_hour}:00 - {end_hour}:00.", datum, znacka, poznamka)

    data = ObjednavkaCreate(
        datum=datum_obj,
        znacka=znacka,
        poznamka=poznamka
    )

    objednavka = obj_service.create(id_uzivatele=user["id"], data=data)
    
    for jedno_id_prace in id_prace:
        obj_service.add_prace(
            id_obj=objednavka.id_objednavky, 
            id_prace=jedno_id_prace
        )

    return RedirectResponse("/dashboard/zakaznik", status_code=303)

def _vratit_formular_s_chybou(request, user, chyba_msg, datum="", znacka="", poznamka=""):
    prace = prace_service.list_all()
    return templates.TemplateResponse(
        "objednavka_nova.html",
        {
            "request": request,
            "prace": prace,
            "chyba": chyba_msg,
            "datum": datum,
            "znacka": znacka,
            "poznamka": poznamka
        }
    )