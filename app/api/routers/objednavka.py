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

# ---------------------------------
# Formulář na vytvoření objednávky (GET)
# ---------------------------------
@router.get("/objednavka/nova", response_class=HTMLResponse)
def nova_objednavka_form(request: Request, user: dict = Depends(require_user)):
    prace = prace_service.list_all()  # načte všechny práce
    return templates.TemplateResponse(
        "objednavka_nova.html",
        {
            "request": request,
            "prace": prace
        }
    )

# ---------------------------------
# POST: vytvoření objednávky
# ---------------------------------
@router.post("/objednavka/nova")
def nova_objednavka_submit(
    request: Request,
    user: dict = Depends(require_user),
    datum: str = Form(...),
    znacka: str = Form(...),
    poznamka: str = Form(""),
    # ZMĚNA ZDE: Přijímáme seznam integerů (List[int])
    id_prace: List[int] = Form(...) 
):
    # převede string z datetime-local na datetime objekt
    datum_obj = datetime.fromisoformat(datum)

    # 1. Vytvoření samotné objednávky (hlavička)
    # Poznámka: Z data pro vytvoření objednávky jsme vyhodili id_prace, 
    # protože to už není jedno číslo, ale řešíme to smyčkou níže.
    data = ObjednavkaCreate(
        datum=datum_obj,
        znacka=znacka,
        poznamka=poznamka
    )

    # Uložíme objednávku do DB a získáme její nové ID
    objednavka = obj_service.create(id_uzivatele=user["id"], data=data)
    
    # 2. Cyklus pro uložení všech vybraných prací
    for jedno_id_prace in id_prace:
        obj_service.add_prace(
            id_obj=objednavka.id_objednavky, 
            id_prace=jedno_id_prace
        )

    return RedirectResponse("/dashboard/zakaznik", status_code=303)