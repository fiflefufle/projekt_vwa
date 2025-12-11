from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.auth import AuthService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
auth_service = AuthService()

ACCESS_COOKIE = "access_token"

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_user(request: Request, response: Response,
               login: str = Form(...),
               password: str = Form(...)):
    try:
        token = auth_service.login(login=login, password=password)
        resp = RedirectResponse(url="/dashboard", status_code=303)
        resp.set_cookie(
            key=ACCESS_COOKIE,
            value=token,
            httponly=True,
            samesite="lax"
        )
        return resp
    except ValueError:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "chyba": "Neplatné přihlášení"}
        )

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(ACCESS_COOKIE)
    return response

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_submit(
    request: Request,
    login: str = Form(...),
    jmeno: str = Form(...),
    prijmeni: str = Form(...),
    password: str = Form(...),
    password_check: str = Form(...)
):
    if password != password_check:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "chyba": "Hesla se neshodují.",
                "login": login,
                "jmeno": jmeno,
                "prijmeni": prijmeni
            }
        )

    # ID_role = 1 (Zákazník, dle konvence)
    result = auth_service.pridej_uzivatele(
        login=login,
        jmeno=jmeno,
        prijmeni=prijmeni,
        password=password,
        id_role=1 
    )

    if "chyba" in result:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "chyba": result["chyba"],
                "login": login,
                "jmeno": jmeno,
                "prijmeni": prijmeni
            }
        )
    
    return RedirectResponse("/login?registered=1", status_code=303)