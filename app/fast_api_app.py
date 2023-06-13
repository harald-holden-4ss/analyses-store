from fastapi import FastAPI, APIRouter
from app.routes.one_collection_routes import get_router_one_collection
from app.routes.result_update_routes import (
    get_advanced_analyses_results_routes)
from app.models.analyses import analysis_result, vessel
from .services.database_service import database_service



def get_app():
    db_serv = database_service()
    app = FastAPI()
    api = APIRouter(prefix="/api")
    vessels_routes = get_router_one_collection(db_serv, "vessels", vessel)
    analyses_base_routes = get_router_one_collection(db_serv, "analyses", analysis_result)
    analyses_advanced_routes = get_advanced_analyses_results_routes(db_serv,
        "analysesresults")
    api.include_router(vessels_routes)
    api.include_router(analyses_base_routes)
    api.include_router(analyses_advanced_routes)
    app.include_router(api)

    @app.get("/ping")
    def pingpong():
        return "pong"

    return app
