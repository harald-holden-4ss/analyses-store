from .one_collection_routes import get_router_one_collection
from ..services.database_service import database_service
from fastapi import Response
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
import json
from app.models.analyses import vessel


def get_vessel_router(db_serv: database_service):
    validation_object = vessel
    ret_router = get_router_one_collection(
        db_serv=db_serv,
        collection_name="vessels",
        validation_object=validation_object,
        add_route_list=["get_all", "get_by_id", "post", "patch"],
    )

    @ret_router.delete("/{id}")
    def delete(id: str):
        try:
            print(db_serv)
            analyses_with_vessel = db_serv.get_analysis_id_by_vesselid(id)
            num_analyses_with_vessel = len(analyses_with_vessel)

            if num_analyses_with_vessel == 0:
                return_data = db_serv.delete_one_document_by_id("vessels", id)
                return return_data
            else:
                return_dict = {
                    "error_message": f"document with id {id} cannot be deleted, the vessel is refered to in {num_analyses_with_vessel} analyses",
                    "analyses_ids": [c["id"] for c in analyses_with_vessel],
                }
                return Response(status_code=409, content=json.dumps(return_dict))
        except CosmosResourceNotFoundError:
            return Response(
                status_code=404, content=f"document with id {id} not found in vessels"
            )
        except CosmosHttpResponseError:
            return Response(status_code=409, content=f"error response from database")
        except Exception as e:
            raise e

    return ret_router
