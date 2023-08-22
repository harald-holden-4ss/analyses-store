from fastapi import APIRouter
from ..services.database_service import database_service
from ..models.jsonpatch import json_patch_modify
import jsonpatch
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

    @router.patch(router_str + "/{id}")
    def patch_document(id: str, updates: list[json_patch_modify]):
        """
            Updates one document with the updates given in the body.  All updates are given as
            a dict on the following form:
            [
                {
                    "op": string with the operation to performe ("add", "replace", "remove") 
                    "path": string with the path where the operation should be applied 
                    "value": the value (for replace or add operations)
            
                }
            ] 
        """
        update_document = db_serv.get_one_document_by_id(
            collection_name=collecion_name, document_id=id)
        updates = [dict(c) for c in updates]
        jsonpatch.apply_patch(update_document, updates, in_place=True)
        db_serv.replace_one_document(
            collection_name=collecion_name, 
            doc_id=id,
            replace_item=update_document)
        return update_document

    return router
