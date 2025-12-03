from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.auth import AuthService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
auth_service = AuthService()

ACCESS_COOKIE = "access_token"


# ---------------------------------
# GET /login
# ---------------------------------
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ---------------------------------
# POST /login
# ---------------------------------
@router.post("/login")
def login_user(request: Request, response: Response,
               login: str = Form(...),
               password: str = Form(...)):
    """
    Přihlášení pomocí login + heslo
    """
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
