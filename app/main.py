from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from app.api.routers.home import router as home_router
from app.api.routers.sluzby import router as sluzby_router
from app.api.routers.login import router as login_router
from app.api.routers.dashboard import router as dashboard_router
from app.api.routers.objednavka import router as objednavka_router

def create_app() -> FastAPI:
    app = FastAPI(title="Autoservis")

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    app.state.templates = Jinja2Templates(directory="app/templates")

    app.include_router(home_router, prefix="", tags=["Home"])
    app.include_router(sluzby_router, prefix="", tags=["Služby"])
    app.include_router(login_router, prefix="", tags=["Login"])
    app.include_router(dashboard_router, prefix="", tags=["Dashboard"])
    app.include_router(objednavka_router, prefix="", tags=["Objednávka"])

    return app

app = create_app()