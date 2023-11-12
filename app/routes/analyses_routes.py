import pandas as pd
import numpy as np
from .one_collection_routes import get_router_one_collection
from ..services.database_service import database_service
from app.models.analyses import analysis_result
from ..services.analysis_dict_manipulator import (
    update_seastate_summary_results,
    extract_all_summary_results,
)

# from ..services.database_service import database_service
from typing import Literal
from ..auth import authorized_user
from ..models.user import User
from ..models.analyses import update_analyses_summary_input


def get_analysis_router(db_serv: database_service):
    router = get_router_one_collection(db_serv, "analyses", analysis_result)
    #    return_routes = result_summary_routes(db_serv, analyses_base_routes)

    @router.get("/{id}/seastate_results")
    def get_seastate_results(id: str):
        doc = db_serv.get_one_document_by_id("analyses", id)
        summary_res = extract_all_summary_results(doc)
        return summary_res

    @router.get("/{id}/drio_time_series_ids")
    def get_drio_time_series_ids(id: str):
        doc = db_serv.get_one_document_by_id("analyses", id)
        all_time_series_with_drio_key = {}
        for one_analysis in doc["all_seastate_results"]:
            dict_key = f"{one_analysis['meta']['location']}__{one_analysis['meta']['result_type']}"

            all_time_series_with_drio_key[dict_key] = {
                _get_hs_tp_string(hs=c["hs"], tp=c["tp"]): {
                    "hs": c["hs"],
                    "tp": c["tp"],
                    "time_series_id": c["result"]["time_series_id"],
                    **one_analysis["meta"],
                }
                for c in one_analysis["data"]
                if c["result"]["time_series_id"] is not None
            }
        return all_time_series_with_drio_key

    @router.get("/{id}/dynamic_interpolator")
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

    @router.get("/summary/result_summary")
    def get_result_summary(
        result_type: Literal["simple", "detailed", "full"] = None,
        user: User = authorized_user,
    ):
        if result_type is None:
            result_type = "simple"
        vessel_dict = _get_vessel_dict(db_serv)
        documents = db_serv.get_all_documents_short(
            "analyses", ["id", "metadata", "general_results"]
        )

        response_values = []
        for d in documents:
            if result_type == "simple":
                if d["metadata"]["xt"]:
                    xt_string = "Yes"
                else:
                    xt_string = "No"
                if "m_eq_dominant_direction" in d["general_results"]:
                    m_eq = d["general_results"]["m_eq_dominant_direction"]
                else:
                    m_eq = None
                #                print(i, d["id"],d["metadata"]["vessel_id"])
                response_values.append(
                    {
                        "id": d["id"],
                        "analysis_type": d["metadata"]["analysis_type"],
                        "water_depth": d["metadata"]["water_depth"],
                        "vessel": vessel_dict[d["metadata"]["vessel_id"]],
                        "project_id": d["metadata"]["project_id"],
                        "well_name": d["metadata"]["well"]["name"],
                        "version": d["metadata"]["version"],
                        "wave_direction_relative_to_rig": float(
                            np.abs(
                                d["metadata"]["wave_direction"]
                                - d["metadata"]["vessel_heading"]
                            )
                        ),
                        "current": d["metadata"]["current"],
                        "xt": xt_string,
                        "overpull": d["metadata"]["overpull"],
                        "well_data": _get_well_summary(d["metadata"]["well"]),
                        "comment": d["metadata"]["comment"],
                        "client": d["metadata"]["client"],
                        "m_eq_dominant_direction": m_eq,
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
                        "offset_percent_of_wd": d["metadata"]["offset_percent_of_wd"],
                        "client": d["metadata"]["client"],
                        "well_boundary_type": d["metadata"]["well"][
                            "well_boundary_type"
                        ],
                        **d["general_results"],
                    }
                )
            else:
                response_values.append(
                    {"id": d["id"], **d["metadata"], **d["general_results"]}
                )
        return response_values

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

    return router


def _get_vessel_dict(db_serv):
    documents = db_serv.get_all_documents("vessels")
    return {c["id"]: c["name"] for c in list(documents)}


def _get_hs_tp_string(hs, tp):
    return f"H{int(hs*100):04d}_T{int(tp*100):04d}"


def _get_well_summary(well):
    ret_str = f"name: {well['name']}\n"
    ret_str += f"boundary-type: {well['well_boundary_type']}\n"
    ret_str += f"well-design-type: {well['design_type']}\n"
    ret_str += f"well-stiffness: {well['stiffness']}\n"
    ret_str += f"support-feature: {well['feature']}\n"
    ret_str += f"support-feature: {well['feature']}\n"
    if type(well["soil"]) is dict:
        ret_str += f"soil-type: {well['soil']['soil_type']}\n"
        ret_str += f"soil-version: {well['soil']['soil_version']}\n"
        ret_str += f"soil-sensitivity: {well['soil']['soil_sensitivity']}\n"
    else:
        ret_str += "soil-type: None\n"
    return ret_str
