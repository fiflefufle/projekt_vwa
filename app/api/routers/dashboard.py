from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.api.dependencies import get_current_user, require_user, require_mechanik, require_admin
from app.services.objednavka import ObjednavkaService
from app.services.stavobjednavky import StavObjednavkyService
from app.services.uzivatel import UzivatelService
from app.services.prace import PraceService
from app.models.schemas import UzivatelCreate

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

# ---------------------------------
# SPRÁVA UŽIVATELŮ (ADMIN)
# ---------------------------------

@router.get("/dashboard/admin/users", response_class=HTMLResponse)
def admin_users_list(request: Request, user: dict = Depends(require_admin)):
    """Zobrazí seznam uživatelů a formulář pro přidání"""
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
    """Zpracuje přidání nového uživatele"""
    # Vytvoříme objekt schématu (heslo se zahashuje uvnitř service.create_user)
    new_user_data = UzivatelCreate(
        login=login,
        heslo=password,
        jmeno=jmeno,
        prijmeni=prijmeni
    )
    
    # Pozor: metoda create_user v service očekává "data" typu UzivatelCreate 
    # a my musíme ještě nějak předat ID role, které ve schématu UzivatelCreate chybí?
    # Rychlá oprava: AuthService.pridej_uzivatele to umí přímo. 
    # Ale abychom drželi pořádek, použijeme AuthService nebo upravíme UzivatelService.
    # PRO JEDNODUCHOST použijeme přímo auth_service, který už máš importovaný v login.py? 
    # Ne, tady v dashboard.py nemáme AuthService.
    
    # Tákže: Nejčistší je zavolat repo přímo přes service wrapper, 
    # ale musíme si poradit s tím hashováním.
    # Service.create_user bere UzivatelCreate, ale tam není ID_role.
    # UPRAVÍME RYCHLE VOLÁNÍ, abychom využili existující repo.create_user:
    
    from app.core.security import hash_password
    hashed = hash_password(password)
    
    # Voláme přímo repo (nebo si na to udělej metodu v service, pokud chceš být purista)
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
    # Ochrana: Admin by neměl smazat sám sebe
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
        # Pokud by se admin pokusil smazat něco jiného (např. přes hacknutí formuláře)
        raise HTTPException(400, "Tuto objednávku nelze smazat (není hotová ani stornovaná).")
        
    return RedirectResponse("/dashboard/admin", status_code=303)

@router.post("/dashboard/admin/pridat_praci")
def pridat_praci_admin(
    id_obj: int = Form(...),
    id_prace: int = Form(...),
    user: dict = Depends(require_admin)
):
    """
    Umožní adminovi přidat další práci k existující objednávce.
    """
    # Použijeme existující service metodu
    obj_service.add_prace(id_obj=id_obj, id_prace=id_prace)
    
    return RedirectResponse("/dashboard/admin", status_code=303)