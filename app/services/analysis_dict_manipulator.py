from copy import deepcopy
from ..models.analyses import DEFAULT_UNITS


def extract_summary_result_types(document):
    unique_responses = list(
        set(
            [
                f"{c['meta']['location']}__{c['meta']['result_type']}"
                for c in document["all_seastate_results"]
            ]
        )
    )
    return [
        {"location": c.split("__")[0], "result_type": c.split("__")[1]}
        for c in unique_responses
    ]


def extract_availible_summary_results_methods_one_result_set(one_seastate_results):
    return list(
        set(
            [
                d["method"]
                for c in one_seastate_results["data"]
                for d in c["result"]["summary_values"]
            ]
        )
    )


def _update_summary_value_list(summary_value_list, method, value):
    existing_methods = list(set([c["method"] for c in summary_value_list]))
    if method in existing_methods:
        one_value = [c for c in summary_value_list if c["method"] == method][0]
        one_value_index = summary_value_list.index(one_value)
        summary_value_list[one_value_index] = {"method": method, "value": value}
        return summary_value_list
    else:
        summary_value_list.append({"method": method, "value": value})
        return summary_value_list


def _filter_dict_list(dict_list, filter_dict, sub_level=None):
    if sub_level is None:
        short_filter_dict = list(
            filter(
                lambda one_dict: all(fk in one_dict for fk in filter_dict), dict_list
            )
        )
        return list(
            filter(
                lambda one_dict: all(
                    (k in filter_dict and one_dict[k] == v)
                    for k, v in filter_dict.items()
                ),
                short_filter_dict,
            )
        )

    short_filter_dict = list(
        filter(
            lambda one_dict: all(fk in one_dict[sub_level] for fk in filter_dict),
            dict_list,
        )
    )
    return list(
        filter(
            lambda one_dict: all(
                (k in filter_dict and one_dict[sub_level][k] == v)
                for k, v in filter_dict.items()
            ),
            short_filter_dict,
        )
    )


def update_seastate_summary_results(document, list_of_updates):
    return_document = deepcopy(document)
    for update in list_of_updates:
        return_document = update_one_seastate_sumamry_value(
            document=return_document,
            hs=update['hs'],
            tp=update['tp'],
            location=update['location'],
            result_type=update['result_type'],
            method=update['method'], 
            value=update['value'])
    return return_document


def update_one_seastate_timeseriesid(
    document, hs, tp, location, result_type, timeseries_id, unit=None    
):
    output_document = deepcopy(document)
    all_seastate_results = output_document["all_seastate_results"].copy()
    one_result = _filter_dict_list(
        all_seastate_results,
        {"result_type": result_type, "location": location},
        sub_level="meta",
    )

    if len(one_result) == 1:
        one_result = one_result[0].copy()
        one_result_index = all_seastate_results.index(one_result)
        one_seastate_results = _filter_dict_list(
            one_result["data"],
            {"hs": hs, "tp": tp},
        )
        if len(one_seastate_results) == 1:
            one_seastate_results = one_seastate_results[0].copy()
            one_seastate_results_index = one_result["data"].index(one_seastate_results)
            one_seastate_results["result"]["time_series_id"] = timeseries_id
            one_result["data"][one_seastate_results_index] = one_seastate_results
        else:
            one_result["data"].append(
                {
                    "hs": hs,
                    "tp": tp,
                    "result": {"time_series_id": timeseries_id, "summary_values":[]},
                }
            )
        #            raise KeyError(f"Data for hs = {hs} and tp = {tp} not found")
        output_document["all_seastate_results"][one_result_index] = one_result
        
    else:
        if unit is None:
            unit = _get_default_unit(result_type=result_type)
        one_result = {
            'meta': {
                'location': location,
                'result_type': result_type,
                'unit': unit},
            'data':[{
                    "hs": hs,
                    "tp": tp,
                    "result": {"time_series_id": timeseries_id, "summary_values":[]}}]
            }
        output_document["all_seastate_results"].append(one_result)
    return output_document

    
def update_one_seastate_sumamry_value(
    document, hs, tp, location, result_type, method, value, unit=None
):
    output_document = deepcopy(document)
    all_seastate_results = output_document["all_seastate_results"].copy()
    one_result = _filter_dict_list(
        all_seastate_results,
        {"result_type": result_type, "location": location},
        sub_level="meta",
    )

    if len(one_result) == 1:
        one_result = one_result[0].copy()
        one_result_index = all_seastate_results.index(one_result)
        one_seastate_results = _filter_dict_list(
            one_result["data"],
            {"hs": hs, "tp": tp},
        )
        #    one_seastate_results = [c for c in one_result['data'] if ((c['hs']==hs)&(c['tp']==tp))]
        if len(one_seastate_results) == 1:
            one_seastate_results = one_seastate_results[0].copy()
            one_seastate_results_index = one_result["data"].index(one_seastate_results)
            one_seastate_results["result"][
                "summary_values"
            ] = _update_summary_value_list(
                one_seastate_results["result"]["summary_values"], method, value
            )
            one_result["data"][one_seastate_results_index] = one_seastate_results
        else:
            one_result["data"].append(
                {
                    "hs": hs,
                    "tp": tp,
                    "result": {"summary_values": [{"method": method, "value": value}]},
                }
            )
        #            raise KeyError(f"Data for hs = {hs} and tp = {tp} not found")
        output_document["all_seastate_results"][one_result_index] = one_result
        
    else:
        if unit is None:
            unit = _get_default_unit(result_type=result_type)
        one_result = {
            'meta': {
                'location': location,
                'result_type': result_type,
                'unit': unit},
            'data':[{
                    "hs": hs,
                    "tp": tp,
                    "result": {"summary_values": [{"method": method, "value": value}]},
                }]
            }
        output_document["all_seastate_results"].append(one_result)
    return output_document
        # raise KeyError(
        #     f"Data for location = {location} and result type = {result_type} not found"
        # )


def _get_default_unit(result_type):
    return DEFAULT_UNITS[result_type]


def extract_all_summary_results(document):
    return [
        {
            "hs": one_seastate["hs"],
            "tp": one_seastate["tp"],
            **one_result["meta"],
            **one_summary_res,
        }
        for one_result in document["all_seastate_results"]
        for one_seastate in one_result["data"]
        for one_summary_res in one_seastate["result"]["summary_values"]
    ]
