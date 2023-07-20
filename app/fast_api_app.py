from fastapi import FastAPI, APIRouter
from app.routes.one_collection_routes import get_router_one_collection
from app.routes.result_update_routes import (
    get_advanced_analyses_results_routes,
    add_detailed_routes
    )
from app.models.analyses import analysis_result, vessel
from .services.database_service import database_service
from .auth import authorized_user
from fastapi.responses import JSONResponse
from .models.user import User


def get_app():
    db_serv = database_service()
    print(db_serv)
    app = FastAPI()
    api = APIRouter(prefix="/api")#
    vessels_routes = get_router_one_collection(db_serv, "vessels", vessel)
    analyses_base_routes = get_router_one_collection(db_serv, "analyses", analysis_result)
    analyses_routes = add_detailed_routes(db_serv,analyses_base_routes)
    analyses_advanced_routes = get_advanced_analyses_results_routes(db_serv,
        "analysesresults")
    api.include_router(vessels_routes)
    api.include_router(analyses_routes)
    api.include_router(analyses_advanced_routes)
    app.include_router(api)

    @app.get("/user")
    async def user(user: User = authorized_user):
        return JSONResponse(user.dict())
  
    @app.get("/ping")
    def pingpong():
        return "pong"

    return app
