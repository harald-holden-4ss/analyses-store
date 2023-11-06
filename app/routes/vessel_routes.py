from .one_collection_routes import get_router_one_collection
from ..services.database_service import database_service


def get_vessel_router(
        db_serv: database_service
        validation_object: object):
    ret_router = get_router_one_collection(
        db_serv=db_serv,
        collecion_name="vessels", 
        validation_object=validation_object)
    return ret_router