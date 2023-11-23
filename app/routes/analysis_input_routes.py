from .one_collection_routes import get_router_one_collection
from ..services.database_service import database_service
#from fastapi import Response
#from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError

from app.models.analysis_input import analysis_input


def get_analysis_input_router(db_serv: database_service):
    ret_router = get_router_one_collection(
        db_serv=db_serv,
        collection_name="analysis_input",
        validation_object=analysis_input,
        add_route_list=["get_all", "get_by_id", "post", "patch", "delete"],
    )

    return ret_router
