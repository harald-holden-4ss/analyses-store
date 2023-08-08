from fastapi import APIRouter
from ..services.database_service import database_service


def get_router_one_collection(
    db_serv: database_service, collecion_name: str, validation_object: object
):
    router = APIRouter(
        prefix=f"/{collecion_name}",
        tags=[collecion_name],
    )
    router_str = f""

    @router.get(router_str)
    def get_all():
        return db_serv.get_all_documents(collecion_name)

    @router.get(router_str + "/{id}")
    def get_one(id: str):
        return db_serv.get_one_document_by_id(collecion_name, id)

    @router.post(router_str)
    def post(validated_body: validation_object):
        return db_serv.post_one_document(collecion_name, validated_body.dict())

    @router.post(router_str)
    def put(validated_body: validation_object):
        return db_serv.post_one_document(collecion_name, validated_body.dict())

    @router.delete(router_str + "/{id}")
    def delete_analysis(id: str):
        return db_serv.delete_one_document_by_id(collecion_name, id)

    return router
