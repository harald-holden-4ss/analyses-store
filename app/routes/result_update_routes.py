from fastapi import APIRouter
from ..models.analyses import (
    update_analyses_summary_input
)
from ..services.analysis_dict_manipulator import (
    update_seastate_summary_results,
    extract_all_summary_results)
from ..services.database_service import database_service

#from ..services.database_service import database_service

def get_advanced_analyses_results_routes(db_serv: database_service, prefix: str):
    router = APIRouter(
        prefix= "/" +prefix,
        tags=["seastate_summary"],
    )
    @router.get("/seastate_summary_results/{id}")
    def get_seastate_summary(id: str):
        doc = db_serv.get_one_document_by_id("analyses", id)
        summary_res = extract_all_summary_results(doc)
        return summary_res

        
    @router.get("/analysesmeta")
    def get_analysesmeta():
        documents = db_serv.get_all_documents("analyses")
        
        return [{
            'id': c['id'], 
            **c['metadata'], 
            **c['general_results']} for c in documents]


    @router.put("/seastate_summary_update")
    def put_update_summary(updates: update_analyses_summary_input):
        id = str(updates.dict()["id"])
        old_document = db_serv.get_one_document_by_id("analyses", id)
        updated_doc = update_seastate_summary_results(
            old_document,
            updates.dict()['updates'])
        return_val = db_serv.replace_one_document("analyses", id, updated_doc)
        return return_val

    return router
