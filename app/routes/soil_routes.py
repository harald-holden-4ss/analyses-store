from .one_collection_routes import get_router_one_collection
from ..services.database_service import database_service
#from fastapi import Response
#from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError

from app.models.soil import soil_data


def get_soil_router(db_serv: database_service):
    validation_object = soil_data
    ret_router = get_router_one_collection(
        db_serv=db_serv,
        collection_name="soil",
        validation_object=validation_object,
        add_route_list=["get_all", "get_by_id", "post", "patch", "delete"],
    )

    return ret_router
