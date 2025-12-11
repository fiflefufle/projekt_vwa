from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.api.dependencies import get_current_user, require_user, require_mechanik, require_admin
from app.services.objednavka import ObjednavkaService
from app.services.stavobjednavky import StavObjednavkyService
from app.services.uzivatel import UzivatelService
from app.services.prace import PraceService
from app.models.schemas import UzivatelCreate
from app.core.security import hash_password

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
    vsechny_prace = prace_service.list_all()

    return templates.TemplateResponse(
        "dashboard_admin.html",
        {
            "request": request, 
            "objednavky": objednavky, 
            "mechanici": mechanici, 
            "stavy": stavy,
            "prace": vsechny_prace
        }
    )


@router.post("/dashboard/admin/pridel_mechanik_objednavka")
def pridel_mechanik_objednavka(
    id_obj: int = Form(...),
    id_mechanik: str = Form(""),
    user: dict = Depends(require_admin)
):
    if id_mechanik == "":
        return RedirectResponse("/dashboard/admin", status_code=303)

    try:
        id_mechanik_int = int(id_mechanik)
    except ValueError:
        raise HTTPException(400, "Neplatná hodnota mechanika.")

    obj_service.assign_mechanik_to_order(id_obj, id_mechanik_int)
    return RedirectResponse("/dashboard/admin", status_code=303)


# ---------------------------------
# SPRÁVA UŽIVATELŮ (ADMIN)
# ---------------------------------
@router.get("/dashboard/admin/users", response_class=HTMLResponse)
def admin_users_list(request: Request, user: dict = Depends(require_admin)):
    users = uzivatel_service.list_users()
    roles = uzivatel_service.list_roles()
    return templates.TemplateResponse(
        "manage_users.html", 
        {"request": request, "users": users, "roles": roles}
    )

@router.post("/dashboard/admin/users/add")
def admin_user_add(
    login: str = Form(...),
    password: str = Form(...),
    jmeno: str = Form(...),
    prijmeni: str = Form(...),
    id_role: int = Form(...),
    user: dict = Depends(require_admin)
):
    hashed = hash_password(password)
    from app.repositories import uzivatel as repo_uzivatel
    repo_uzivatel.create_user(
        login=login,
        hashed_password=hashed,
        id_role=id_role,
        jmeno=jmeno,
        prijmeni=prijmeni
    )
    return RedirectResponse("/dashboard/admin/users", status_code=303)

@router.post("/dashboard/admin/users/delete")
def admin_user_delete(
    id_uzivatele: int = Form(...),
    user: dict = Depends(require_admin)
):
    if id_uzivatele == user["id"]:
        raise HTTPException(400, "Nemůžete smazat sami sebe.")
    uzivatel_service.delete_user(id_uzivatele)
    return RedirectResponse("/dashboard/admin/users", status_code=303)

@router.post("/dashboard/admin/delete_objednavka")
def delete_objednavka_admin(
    id_obj: int = Form(...),
    user: dict = Depends(require_admin)
):
    try:
        obj_service.delete(id_obj)
    except ValueError:
        raise HTTPException(400, "Tuto objednávku nelze smazat (není hotová ani stornovaná).")
    return RedirectResponse("/dashboard/admin", status_code=303)

@router.post("/dashboard/admin/pridat_praci")
def pridat_praci_admin(
    id_obj: int = Form(...),
    id_prace: int = Form(...),
    user: dict = Depends(require_admin)
):
    obj_service.add_prace(id_obj=id_obj, id_prace=id_prace)
    return RedirectResponse("/dashboard/admin", status_code=303)

@router.get("/dashboard/admin/users/edit/{user_id}", response_class=HTMLResponse)
def admin_user_edit_form(user_id: int, request: Request, user: dict = Depends(require_admin)):
    user_to_edit = uzivatel_service.get_user(user_id)
    if not user_to_edit:
        return RedirectResponse("/dashboard/admin/users", status_code=303)
    roles = uzivatel_service.list_roles()
    return templates.TemplateResponse(
        "admin_user_edit.html", 
        {"request": request, "u": user_to_edit, "roles": roles}
    )

@router.post("/dashboard/admin/users/edit/{user_id}")
def admin_user_edit_submit(
    user_id: int,
    login: str = Form(...),
    jmeno: str = Form(...),
    prijmeni: str = Form(...),
    id_role: int = Form(...),
    password: str = Form(""),
    user: dict = Depends(require_admin)
):
    data = UzivatelCreate(
        login=login,
        jmeno=jmeno,
        prijmeni=prijmeni,
        heslo=password 
    )
    uzivatel_service.update_user_complete(user_id, data, id_role)
    return RedirectResponse("/dashboard/admin/users", status_code=303)

@router.post("/dashboard/admin/nacenit_praci")
def admin_nacenit_praci(
    id_servisu: int = Form(...),
    cas: float = Form(...),
    cena: str = Form(None), 
    user: dict = Depends(require_admin)
):
    cena_float = None
    if cena and cena.strip() != "":
        try:
            cena_float = float(cena)
        except ValueError:
            raise HTTPException(status_code=400, detail="Cena musí být číslo.")

    obj_service.nacenit_praci(id_servisu, cas, cena_float)
    return RedirectResponse("/dashboard/admin", status_code=303)