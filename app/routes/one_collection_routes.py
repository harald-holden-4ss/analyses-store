from fastapi import APIRouter, Response
from ..services.database_service import database_service
from ..models.jsonpatch import json_patch_modify
import json
import jsonpatch
from azure.cosmos.exceptions import (
    CosmosResourceNotFoundError, 
    CosmosHttpResponseError)

def get_router_one_collection(
    db_serv: database_service, 
    collection_name: str, 
    validation_object: object,
    add_route_list = None
):
    router = APIRouter(
        prefix=f"/{collection_name}",
        tags=[collection_name],
    )
    router_str = f""
    if add_route_list is None:
        add_route_list = ['get_all', 'get_by_id', 'post', 'delete', 'patch']
    
    if 'get_all' in add_route_list:
        @router.get(router_str)
        def get_all():
            return db_serv.get_all_documents(collection_name)

    if 'get_by_id' in add_route_list:
        @router.get(router_str + "/{id}")
        def get_one(id: str):
            try:
                return_data = db_serv.get_one_document_by_id(collection_name, id)
                return return_data
            except CosmosResourceNotFoundError:
                return Response(status_code=404,
                                content=f"document with id {id} not found in {collection_name}")
            except CosmosHttpResponseError:
                return Response(status_code=409, 
                                content=f"error response from database")
            except Exception as e:
                raise e

    if 'post' in add_route_list:
        @router.post(router_str)
        def post(validated_body: validation_object):
            return db_serv.post_one_document(
                collection_name, validated_body.model_dump())

    if 'delete' in add_route_list:
        @router.delete(router_str + "/{id}")
        def delete(id: str):
            try:
                return_data = db_serv.delete_one_document_by_id(
                    collection_name, id)
                return return_data
            except CosmosResourceNotFoundError:
                return Response(status_code=404,
                                content=f"document with id {id} not found in {collection_name}")
            except CosmosHttpResponseError:
                return Response(status_code=409, 
                                content=f"error response from database")
            except Exception as e:
                raise e

            
    if 'patch' in add_route_list:
        @router.patch(router_str + "/{id}")
        def patch(id: str, updates: list[json_patch_modify]):
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
            updates = [dict(c) for c in updates]
            try:
                return db_serv.patch_one_document(
                    collection_name=collection_name, 
                    document_id=id,
                    updates=updates)
            except CosmosResourceNotFoundError:
                return Response(status_code=404,
                                content=json.dumps({'error_message':f"document with id {id} not found in {collection_name}"}))
            except CosmosHttpResponseError:
                return Response(status_code=409, 
                                content=json.dumps({'error_message':f"error response from database"}))
            except Exception as e:
                raise e
            
            # update_document = db_serv.get_one_document_by_id(
            #     collection_name=collection_name, document_id=id)
            # updates = [dict(c) for c in updates]
            # jsonpatch.apply_patch(update_document, updates, in_place=True)
            # db_serv.replace_one_document(
            #     collection_name=collection_name, 
            #     doc_id=id,
            #     replace_item=update_document)
            # return update_document

    return router
