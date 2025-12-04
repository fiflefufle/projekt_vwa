from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.api.dependencies import get_current_user, require_user, require_mechanik, require_admin
from app.services.objednavka import ObjednavkaService
from app.services.stavobjednavky import StavObjednavkyService
from app.services.uzivatel import UzivatelService
from app.services.prace import PraceService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
obj_service = ObjednavkaService()
stav_service = StavObjednavkyService()
uzivatel_service = UzivatelService()
prace_service = PraceService()

# ---------------------------------
# /dashboard → přesměrování podle role
# ---------------------------------
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: dict = Depends(get_current_user)):
    """
    Přesměruje uživatele na dashboard podle jeho role.
    """
    role = user.get("role")
    if role == "admin":
        return RedirectResponse(url="/dashboard/admin")
    elif role == "mechanik":
        return RedirectResponse(url="/dashboard/mechanik")
    elif role == "zákazník":
        return RedirectResponse(url="/dashboard/zakaznik")
    else:
        return HTMLResponse("Nepovolený přístup", status_code=403)


# ---------------------------------
# Dashboard pro zákazníky
# ---------------------------------
@router.get("/dashboard/zakaznik", response_class=HTMLResponse)
def dashboard_zakaznik(request: Request, user: dict = Depends(require_user)):
    objednavky = obj_service.list_for_user(user["id"])
    return templates.TemplateResponse(
        "dashboard_zakaznik.html",
        {"request": request, "objednavky": objednavky}
    )


# ---------------------------------
# Dashboard pro mechaniky
# ---------------------------------
@router.get("/dashboard/mechanik", response_class=HTMLResponse)
def dashboard_mechanik(request: Request, user: dict = Depends(require_mechanik)):
    # PŮVODNĚ: objednavky = obj_service.list_all()
    # NOVĚ: Filtrujeme podle ID přihlášeného mechanika (user["id"])
    objednavky = obj_service.list_for_mechanik(user["id"])
    
    stavy = stav_service.list_all()
    return templates.TemplateResponse(
        "dashboard_mechanik.html",
        {"request": request, "objednavky": objednavky, "stavy": stavy}
    )

@router.post("/dashboard/mechanik/zmen_stav")
def zmen_stav_mechanik(
    id_obj: int = Form(...),
    id_stavu: int = Form(...),
    user: dict = Depends(require_mechanik)
):
    obj_service.update_stav(id_obj=id_obj, id_stavu=id_stavu)
    return RedirectResponse("/dashboard/mechanik", status_code=303)

# ---------------------------------
# Dashboard pro adminy
# ---------------------------------
@router.get("/dashboard/admin", response_class=HTMLResponse)
def dashboard_admin(request: Request, user: dict = Depends(require_admin)):
    objednavky = obj_service.list_all()
    mechanici = uzivatel_service.list_mechanics()
    stavy = stav_service.list_all()
    
    # <--- 3. NAČÍST SEZNAM PRACÍ
    vsechny_prace = prace_service.list_all()

    return templates.TemplateResponse(
        "dashboard_admin.html",
        {
            "request": request, 
            "objednavky": objednavky, 
            "mechanici": mechanici, 
            "stavy": stavy,
            "prace": vsechny_prace  # <--- 4. POSLAT DO ŠABLONY (klíč musí být "prace")
        }
    )


@router.post("/dashboard/admin/pridel_mechanik")
def pridel_mechanik(
    id_servisu: int = Form(...),
    id_mechanik: str = Form("")
):
    if id_mechanik == "":
        raise HTTPException(400, "Musíte vybrat mechanika.")

    try:
        id_mechanik_int = int(id_mechanik)
    except ValueError:
        raise HTTPException(400, "Neplatná hodnota mechanika.")

    # OPRAVA: Voláme service vrstvu (obj_service), která už je nahoře inicializovaná.
    # Service vrstva pak správně zavolá repo_servis.assign_mechanik
    obj_service.assign_mechanik(id_servisu, id_mechanik_int)

    return RedirectResponse("/dashboard/admin", status_code=303)