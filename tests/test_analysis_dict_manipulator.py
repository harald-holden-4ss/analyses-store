import pytest
from unittest.mock import patch

from app.services.analysis_dict_manipulator import (
    extract_summary_result_types,
    extract_availible_summary_results_methods_one_result_set,
    _update_summary_value_list,
    update_one_seastate_sumamry_value,
    update_seastate_summary_results,
    _filter_dict_list,
)


@pytest.fixture
def test_dict():
    return {
        "id": "683807f5-5823-49fe-95fb-f3a3a1cebdb4",
        "metadata": {
            "responsible_engineer": "jonny loggon",
            "project_id": 1001,
            "well_name": "wellewell",
            "well_location": {"longitude": 2.0, "latitude": 5.0},
            "version": "testversion",
            "analysis_type": "string",
            "simulation_lenght": 1800.0,
            "water_depth": 150.0,
            "wave_direction": 55.0,
            "vessel_heading": 62.0,
            "current": "None",
            "vessel_id": "61ecac4b-b2ba-48cc-8646-fabb1e9fd44b",
            "xt": True,
            "soil_profile": "suppesoil1",
            "overpull": 490500.0,
            "drillpipe_tension": 738750.0,
        },
        "general_results": {"m_eq_dominant_direction": 1000.0},
        "all_seastate_results": [
            {
                "meta": {
                    "location": "wh_datum",
                    "result_type": "bending moment local x",
                    "unit": "kNm",
                },
                "data": [
                    {
                        "hs": 0.5,
                        "tp": 5.5,
                        "result": {
                            "summary_values": [{"method": "std", "value": 120.5}],
                            "time_series_id": "3fa85f64-5717-4562-b3fc-2c963f66afa1",
                        },
                    },
                    {
                        "hs": 1.5,
                        "tp": 5.5,
                        "result": {
                            "summary_values": [{"method": "std", "value": 134.5}],
                            "time_series_id": "3fa85f64-5717-4562-b3fc-2c963f66afa2",
                        },
                    },
                    {
                        "hs": 0.5,
                        "tp": 2.5,
                        "result": {
                            "summary_values": [{"method": "std", "value": 152.5}],
                            "time_series_id": "3fa85f64-5717-4562-b3fc-2c963f66afa3",
                        },
                    },
                ],
            },
            {
                "meta": {
                    "location": "wh_datum",
                    "result_type": "bending moment local y",
                    "unit": "kNm",
                },
                "data": [
                    {
                        "hs": 0.5,
                        "tp": 5.5,
                        "result": {
                            "summary_values": [{"method": "std", "value": 20.5}],
                            "time_series_id": "3fa85f64-5717-4562-b3fc-2c963f66afa4",
                        },
                    },
                    {
                        "hs": 1.5,
                        "tp": 5.5,
                        "result": {
                            "summary_values": [
                                {"method": "std", "value": 34.5},
                                {"method": "min", "value": 40.5},
                            ],
                            "time_series_id": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
                        },
                    },
                    {
                        "hs": 0.5,
                        "tp": 2.5,
                        "result": {
                            "summary_values": [{"method": "std", "value": 52.5}],
                            "time_series_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        },
                    },
                ],
            },
        ],
        "_rid": "EDQjAIEknl8BAAAAAAAAAA==",
        "_self": "dbs/EDQjAA==/colls/EDQjAIEknl8=/docs/EDQjAIEknl8BAAAAAAAAAA==/",
        "_etag": '"0800f664-0000-3c00-0000-646dfe100000"',
        "_attachments": "attachments/",
        "_ts": 1684930064,
    }


def test_extract_availible_summary_results_methods_one_result_set(test_dict):
    assert sorted(
        extract_availible_summary_results_methods_one_result_set(
            test_dict["all_seastate_results"][1]
        )
    ) == [
        "min",
        "std",
    ]
    assert extract_availible_summary_results_methods_one_result_set(
        test_dict["all_seastate_results"][0]
    ) == [
        "std",
    ]
    test_value_no_summary_results = {
        "meta": {
            "location": "wh_datum",
            "result_type": "bending moment local y",
            "unit": "kNm",
        },
        "data": [
            {
                "hs": 0.5,
                "tp": 5.5,
                "result": {
                    "summary_values": [],
                    "time_series_id": "3fa85f64-5717-4562-b3fc-2c963f66afa4",
                },
            },
            {
                "hs": 1.5,
                "tp": 5.5,
                "result": {
                    "summary_values": [],
                    "time_series_id": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
                },
            },
            {
                "hs": 0.5,
                "tp": 2.5,
                "result": {
                    "summary_values": [],
                    "time_series_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                },
            },
        ],
    }
    assert (
        extract_availible_summary_results_methods_one_result_set(
            test_value_no_summary_results
        )
        == []
    )


def test_extract_summary_result_types(test_dict):
    expected_result = [
        {"location": "wh_datum", "result_type": "bending moment local y"},
        {"location": "wh_datum", "result_type": "bending moment local x"},
    ]
    for di in extract_summary_result_types(test_dict):
        correct_res = [
            c
            for c in expected_result
            if (
                (c["location"] == di["location"])
                & (c["result_type"] == di["result_type"])
            )
        ]
        assert len(correct_res) == 1


@pytest.mark.parametrize(
    "dict, method, value,expected_result",
    [
        (
            [{"method": "std", "value": 1}, {"method": "max", "value": 2}],
            "min",
            3,
            [
                {"method": "std", "value": 1},
                {"method": "max", "value": 2},
                {"method": "min", "value": 3},
            ],
        ),
        (
            [{"method": "std", "value": 1}, {"method": "max", "value": 2}],
            "max",
            5,
            [{"method": "std", "value": 1}, {"method": "max", "value": 5}],
        ),
        ([], "max", 5, [{"method": "max", "value": 5}]),
    ],
)
def test__update_summary_value_list(dict, method, value, expected_result):
    result = _update_summary_value_list(dict, method, value)
    for di in result:
        correct_res = [
            c
            for c in expected_result
            if ((c["method"] == di["method"]) & (c["value"] == di["value"]))
        ]
        assert len(correct_res) == 1


@pytest.mark.parametrize(
    "inp_list_of_dict, filter_dict, sub_level, expected_result",
    [
        (
            [
                {"p1": 1, "p2": 2, "p3": 3},
                {"p1": 2, "p2": 3, "p3": 4},
                {"p1": 3, "p2": 4, "p3": 5},
            ],
            {"p1": 2},
            None,
            [{"p1": 2, "p2": 3, "p3": 4}],
        ),
        (
            [
                {"p1": 1, "p2": 2, "p3": 3},
                {"p1": 2, "p2": 3, "p3": 4},
                {"p1": 3, "p2": 4, "p3": 5},
            ],
            {"p1": 6},
            None,
            [],
        ),
        (
            [
                {"p1": 1, "p2": 2, "p3": 3},
                {"p1": 2, "p2": 3, "p3": 4},
                {"p1": 3, "p2": 4, "p3": 5},
            ],
            {"p7": 2},
            None,
            [],
        ),
        (
            [
                {"p1": 1, "p2": 2, "p3": 3},
                {"p1": 2, "p2": 3, "p3": 4, "p6": 6},
                {"p1": 3, "p2": 4, "p3": 5},
            ],
            {"p6": 6, "p1": 2},
            None,
            [{"p1": 2, "p2": 3, "p3": 4, "p6": 6}],
        ),
        (
            [
                {"p1": 1, "p2": 2, "p3": 3},
                {"p1": 2, "p2": 3, "p3": 4, "p6": 6},
                {"p1": 3, "p2": 4, "p3": 5},
            ],
            {},
            None,
            [
                {"p1": 1, "p2": 2, "p3": 3},
                {"p1": 2, "p2": 3, "p3": 4, "p6": 6},
                {"p1": 3, "p2": 4, "p3": 5},
            ],
        ),
        (
            [
                {"meta": {"m1": 10, "m2": 11}, "p1": 1, "p2": 2, "p3": 3},
                {
                    "meta": {"m1": 11, "m2": 12, "m3": 14},
                    "p1": 2,
                    "p2": 3,
                    "p3": 4,
                    "p6": 6,
                },
                {"meta": {"m1": 12, "m2": 13}, "p1": 3, "p2": 4, "p3": 5},
            ],
            {"m1": 11, "m2": 12},
            "meta",
            [
                {
                    "meta": {"m1": 11, "m2": 12, "m3": 14},
                    "p1": 2,
                    "p2": 3,
                    "p3": 4,
                    "p6": 6,
                }
            ],
        ),
    ],
)
def test__filter_dict_list(inp_list_of_dict, filter_dict, sub_level, expected_result):
    result = _filter_dict_list(inp_list_of_dict, filter_dict, sub_level=sub_level)
    assert result == expected_result


@patch("app.services.analysis_dict_manipulator._update_summary_value_list")
@patch("app.services.analysis_dict_manipulator._filter_dict_list")
def test_update_one_seastate_sumamry_value(filter_dict_mock, update_summary_mock):
    update_summary_mock.return_value = "hei"
    mock_dict = {
        "all_seastate_results": [
            {
                "foo": "one",
                "data": [
                    "data_one",
                    {"result": {"summary_values": None}},
                    "data_three",
                ],
            },
            "one",
            "two",
        ]
    }
    filter_dict_mock.side_effect = [
        [
            {
                "foo": "one",
                "data": [
                    "data_one",
                    {"result": {"summary_values": None}},
                    "data_three",
                ],
            }
        ],
        [{"result": {"summary_values": None}}],
    ]

    result = update_one_seastate_sumamry_value(
        document=mock_dict,
        hs=3.5,
        tp=5.5,
        location="foo_loc",
        result_type="bar_res",
        method="dummy_method",
        value=1.0,
    )

    print(result)
