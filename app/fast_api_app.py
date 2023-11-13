from fastapi import FastAPI, APIRouter
from app.routes.one_collection_routes import get_router_one_collection
from app.routes.vessel_routes import get_vessel_router
from app.routes.analyses_routes import get_analysis_router

# from app.routes.result_update_routes import (
#     result_summary_routes,
# )
from .services.database_service import database_service
from .auth import authorized_user
from fastapi.responses import JSONResponse
from .models.user import User


def get_app(db_serv=None):
    if db_serv is None:
        db_serv = database_service()
    app = FastAPI()
    api = APIRouter(prefix="/api", dependencies=[authorized_user])  #
    vessels_routes = get_vessel_router(db_serv)
    analyses_routes = get_analysis_router(db_serv)
    api.include_router(vessels_routes)
    api.include_router(analyses_routes)
    app.include_router(api)

    @app.get("/user")
    async def user(user: User = authorized_user):
        return JSONResponse(user.model_dump())

    @app.get("/ping")
    def pingpong():
        return "pong"

    return app
