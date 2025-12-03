from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.api.dependencies import get_current_user, require_user, require_mechanik, require_admin
from app.services.objednavka import ObjednavkaService
from app.services.stavobjednavky import StavObjednavkyService
from app.services.uzivatel import UzivatelService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
obj_service = ObjednavkaService()
stav_service = StavObjednavkyService()
uzivatel_service = UzivatelService()

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
    objednavky = obj_service.list_all()
    stavy = stav_service.list_all()  # všechny možné stavy
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
    mechanici = uzivatel_service.list_mechanics()  # id_role=2
    stavy = stav_service.list_all()
    return templates.TemplateResponse(
        "dashboard_admin.html",
        {"request": request, "objednavky": objednavky, "mechanici": mechanici, "stavy": stavy}
    )


@router.post("/dashboard/admin/pridel_mechanik")
def pridel_mechanik(
    id_servisu: int = Form(...),
    id_mechanik: str = Form("")
):
    if id_mechanik == "":
        raise HTTPException(400, "Musíte vybrat mechanika.")

    try:
        id_mechanik = int(id_mechanik)
    except ValueError:
        raise HTTPException(400, "Neplatná hodnota mechanika.")

    # provést přiřazení do DB
    repo_servis.update_mechanik(id_servisu, id_mechanik)

    return RedirectResponse("/dashboard/admin", status_code=303)