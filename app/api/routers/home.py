from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/")
def home(request: Request):
    return request.app.state.templates.TemplateResponse(
        "mainpage.html", {"request": request}
    )
