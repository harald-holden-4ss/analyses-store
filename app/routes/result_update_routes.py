from fastapi import APIRouter
import pandas as pd
import jsonpatch
from ..models.analyses import update_analyses_summary_input
from ..models.jsonpatch import json_patch_modify
from ..services.analysis_dict_manipulator import (
    update_seastate_summary_results,
    extract_all_summary_results,
)
from ..services.database_service import database_service
from typing import Literal


# from ..services.database_service import database_service
def add_detailed_routes( db_serv: database_service, router: APIRouter):
    @router.get("/summary/result_summary")
    def get_result_summary(result_type: Literal["simple", "detailed", "full"] = None):
        if result_type is None:
            result_type = "simple"
        vessel_dict = _get_vessel_dict(db_serv)
        documents = db_serv.get_all_documents("analyses")

        response_values = []
        for d in documents:
            if result_type == "simple":
                response_values.append(
                    {
                        "id": d["id"],
                        "analysis_type": d["metadata"]["analysis_type"],
                        "water_depth": d["metadata"]["water_depth"],
                        "vessel": vessel_dict[d["metadata"]["vessel_id"]],
                        "project_id": d["metadata"]["project_id"],
                        "well_name": d["metadata"]["well"]["name"],
                        "wave_direction": d["metadata"]["wave_direction"],
                        "vessel_heading": d["metadata"]["vessel_heading"],
                        "current": d["metadata"]["current"],
                        # "xt": d["metadata"]["xt"],
                        # "overpull": d["metadata"]["overpull"],
                        # "drillpipe_tension": d["metadata"]["drillpipe_tension"],
                        # "comment": d["metadata"]["comment"],
                        # "offset_percent_of_wd":d["metadata"]["offset_percent_of_wd"],
                        # "client":d["metadata"]["client"],
                        # "well_boundary_type": d["metadata"]["well"]["well_boundary_type"],
                        **d["general_results"],
                    }
                )
            elif result_type == "detailed":
                response_values.append(
                    {
                        "id": d["id"],
                        "analysis_type": d["metadata"]["analysis_type"],
                        "water_depth": d["metadata"]["water_depth"],
                        "vessel": vessel_dict[d["metadata"]["vessel_id"]],
                        "project_id": d["metadata"]["project_id"],
                        "well_name": d["metadata"]["well"]["name"],
                        "wave_direction": d["metadata"]["wave_direction"],
                        "vessel_heading": d["metadata"]["vessel_heading"],
                        "current": d["metadata"]["current"],
                        "xt": d["metadata"]["xt"],
                        "overpull": d["metadata"]["overpull"],
                        "drillpipe_tension": d["metadata"]["drillpipe_tension"],
                        "comment": d["metadata"]["comment"],
                        "offset_percent_of_wd":d["metadata"]["offset_percent_of_wd"],
                        "client":d["metadata"]["client"],
                        "well_boundary_type": d["metadata"]["well"]["well_boundary_type"],
                        **d["general_results"],
                    }
                )
            else:
                response_values.append({"id": d["id"], **d["metadata"],
                                         **d["general_results"]})
            
        return response_values

    # @router.get("/summary/result_summary_allmeta")
    # def get_result_summary():
    #     documents = db_serv.get_all_documents("analyses")
    #     return [
    #         {"id": c["id"], **c["metadata"], **c["general_results"]} for c in documents
    #     ]
    @router.put("/update/update_one/{id}")
    def put_modify_document(id: str, 
                            updates: list[json_patch_modify]):
        update_document = db_serv.get_one_document_by_id(
            collection_name="analyses", document_id=id)
        updates = [dict(c) for c in updates]
        jsonpatch.apply_patch(update_document, updates, in_place=True)
        db_serv.replace_one_document(
            collection_name="analyses", 
            doc_id=id, 
            replace_item=update_document)
        return update_document
 

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
            old_document, updates.dict()["updates"]
        )
        return_val = db_serv.replace_one_document("analyses", id, updated_doc)
        return return_val

    @router.get("/seastate_results/{id}")
    def get_seastate_summary(id: str):
        doc = db_serv.get_one_document_by_id("analyses", id)
        summary_res = extract_all_summary_results(doc)
        return summary_res

    @router.get("/dynamic_interpolator/{id}")
    def get_dynamic_interpolator(id: str):
        doc = db_serv.get_one_document_by_id("analyses", id)

        summary_res = pd.DataFrame(extract_all_summary_results(doc))
        summary_res["res_id"] = summary_res["location"].str.cat(
            summary_res["result_type"].str.cat(summary_res["method"], sep="__"),
            sep="__",
        )
        return_documents = []

        for res_id, one_res_id_data in summary_res.groupby("res_id"):
            return_document = {
                "meta": {
                    "location": one_res_id_data["location"].unique()[0],
                    "result_type": one_res_id_data["result_type"].unique()[0],
                    "method": one_res_id_data["method"].unique()[0],
                },
                # "categorical_attributes": ["location", "result_type", "method"],
                # "continuous_attributes": [],
                "scatters": [],
            }
            one_scatter = {
                "meta": {},
                "data": [],
            }
            for _, one_seastate in one_res_id_data.iterrows():
                one_scatter["data"].append(
                    {
                        "Hs": one_seastate["hs"],
                        "Tp": one_seastate["tp"],
                        "z": one_seastate["value"],
                    }
                )

            return_document["scatters"].append(one_scatter)
            return_documents.append(return_document)

        return return_documents

    return router


def get_advanced_analyses_results_routes(db_serv: database_service, prefix: str):
    router = APIRouter(
        prefix="/" + prefix,
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

        return [
            {"id": c["id"], **c["metadata"], **c["general_results"]} for c in documents
        ]

    @router.put("/seastate_summary_update")
    def put_update_summary(updates: update_analyses_summary_input):
        id = str(updates.dict()["id"])
        old_document = db_serv.get_one_document_by_id("analyses", id)
        updated_doc = update_seastate_summary_results(
            old_document, updates.dict()["updates"]
        )
        return_val = db_serv.replace_one_document("analyses", id, updated_doc)
        return return_val

    return router


def _get_vessel_dict(db_serv):
    documents = db_serv.get_all_documents("vessels")
    return {c["id"]: c["name"] for c in list(documents)}
