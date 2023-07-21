from fastapi import APIRouter
import pandas as pd
from ..models.analyses import (
    update_analyses_summary_input
)
from ..services.analysis_dict_manipulator import (
    update_seastate_summary_results,
    extract_all_summary_results)
from ..services.database_service import database_service

#from ..services.database_service import database_service
def add_detailed_routes(db_serv: database_service, router: APIRouter):

    @router.get("/summary/analyses_metadata")
    def get_result_summary():
        vessel_dict = _get_vessel_dict(db_serv)
        documents = db_serv.get_all_documents("analyses")
        response_values = []
        for d in documents:
            response_values.append({
               'id': d['id'],
                'analysis_type': d['metadata']['analysis_type'],
                'water_depth': d['metadata']['water_depth'],
                'vessel': vessel_dict[d['metadata']['vessel_id']],
                'project_id': d['metadata']['project_id'],
                'well_name': d['metadata']['well']['name'],
                'wave_direction':d['metadata']['wave_direction'],
                'vessel_heading': d['metadata']['vessel_heading'],
                'current': d['metadata']['current'],
                'xt': d['metadata']['xt'],
                'well_boundary_type': d['metadata']['well']['well_boundary_type'],
                **d['general_results']
            })

        return response_values

    @router.get("/summary/result_summary")
    def get_result_summary():
        documents = db_serv.get_all_documents("analyses")
        
        return [{
            'id': c['id'], 
            **c['metadata'], 
            **c['general_results']} for c in documents]


    @router.put("/update/seastate_summary_update")
    def put_update_summary(updates: update_analyses_summary_input):
        """
        Updates seastate summary for one analysis id.  The update should be a list of on or more 
        dicts containing the updates to the analyses summary results.  The result to be updated
        is selected based on hs, tp, location, result_type and method.  The value of the summary results
        will be updated based on the value in the updates.  A new item will be If the given combination
        of selction parameters does not exist  
        """
        id = str(updates.dict()["id"])
        old_document = db_serv.get_one_document_by_id("analyses", id)
        updated_doc = update_seastate_summary_results(
            old_document,
            updates.dict()['updates'])
        return_val = db_serv.replace_one_document("analyses", id, updated_doc)
        return return_val
    

    @router.get("/seastate_results/{id}")
    def get_seastate_summary(id: str):
        doc = db_serv.get_one_document_by_id("analyses", id)
        summary_res = extract_all_summary_results(doc)
        return summary_res
    @router.get("/dynamic_interpolator/{id}")
    def get_seastate_summary(id: str):
        doc = db_serv.get_one_document_by_id("analyses", id)
        return_document = {
            "meta":{ **doc['metadata']},
            "categorical_attributes":['location', 'result_type', 'method'],
            "continuous_attributes": [],
            "scatters":[]}
        
        summary_res = extract_all_summary_results(doc)
        return return_document
    
    return router


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
def _get_vessel_dict(db_serv):
    documents = db_serv.get_all_documents("vessels")
    return {c['id']: c['name'] for c in list(documents)}