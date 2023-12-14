import os
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from dotenv import load_dotenv
from unittest.mock import create_autospec
import pytest
from app.services.database_service import database_service
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError


@pytest.fixture
def app():
    # db_serv_mock = MagicMock(name="test")
    db_serv_mock = create_autospec(database_service)
    load_dotenv()
    os.environ["ENVIRONMENT"] = "development"
    from app.fast_api_app import get_app

    app = get_app(db_serv=db_serv_mock)
    return {"app": app, "db_serv": db_serv_mock}


def test_pingpong(app):
    client = TestClient(app["app"])
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "pong"


def test_get_user(app):
    client = TestClient(app["app"])
    response = client.get("/user")
    assert response.status_code == 200
    assert response.json() == {
        "name": "John Doe",
        "email": "john@doe.com",
        "organizationId": "2c4ee562-6261-4018-a1b1-8837ab526944",
    }


@pytest.mark.parametrize(
    "route, called_with",
    [
        ("/api/vessels", "vessels"),
        ("/api/analyses", "analyses"),
    ],
)
def test_get_vessels(app, route, called_with):
    client = TestClient(app["app"])
    db_response = [{"foo": "bar"}]
    app["db_serv"].get_all_documents.return_value = db_response
    response = client.get(route)
    app["db_serv"].get_all_documents.assert_called_once_with(called_with)
    assert response.status_code == 200
    assert response.json() == db_response


@pytest.mark.parametrize(
    "route, called_with, dbserv_sideeffect, status_code, response_text",
    [
        (
            "/api/vessels",
            "vessels",
            CosmosResourceNotFoundError,
            404,
            "document with id my_id not found in vessels",
        ),
        (
            "/api/analyses",
            "analyses",
            CosmosResourceNotFoundError,
            404,
            "document with id my_id not found in analyses",
        ),
        (
            "/api/vessels",
            "vessels",
            CosmosHttpResponseError,
            409,
            "error response from database",
        ),
        (
            "/api/analyses",
            "analyses",
            CosmosHttpResponseError,
            409,
            "error response from database",
        ),
    ],
)
def test_get_vessel_not_in_db(
    app, route, called_with, dbserv_sideeffect, status_code, response_text
):
    client = TestClient(app["app"])
    #    db_response = {'foo': 'bar'}
    app["db_serv"].get_one_document_by_id.side_effect = dbserv_sideeffect
    response = client.get(route + r"/my_id")
    app["db_serv"].get_one_document_by_id.assert_called_once_with(called_with, "my_id")
    assert response.status_code == status_code
    assert response.text == response_text


@pytest.mark.parametrize(
    "route, called_with",
    [
        ("/api/vessels", "vessels"),
        ("/api/analyses", "analyses"),
    ],
)
def test_get_vessel(app, route, called_with):
    client = TestClient(app["app"])
    db_response = {"foo": "bar"}
    app["db_serv"].get_one_document_by_id.return_value = db_response
    response = client.get(route + r"/my_vessel_id")
    app["db_serv"].get_one_document_by_id.assert_called_once_with(
        called_with, "my_vessel_id"
    )
    assert response.status_code == 200
    assert response.json() == db_response


@pytest.mark.parametrize(
    "route, called_with, obj_to_post",
    [
        ("/api/vessels", "vessels", {"name": "test_1", "imo": 12345, 'year_built': None}),
        (
            "/api/analyses",
            "analyses",
            {
                "metadata": {
                    "responsible_engineer": "Jonny Yess",
                    'analysis_input_id': None,
                    "project_id": 1234,
                    "well": {
                        "name": "well1",
                        "well_id_4insight": None,
                        "well_boundary_type": "well_included",
                        "design_type": "satelite",
                        "location": {"longitude": 7.5, "latitude": 62.5},
                        "stiffness": 0,
                        "feature": None,
                        "soil": {
                            "soil_type": "api",
                            "soil_version": "low",
                            "soil_sensitivity": "clay",
                        },
                    },
                    "version": "base",
                    "analysis_type": "fatigue",
                    "simulation_length": 1,
                    "water_depth": 212,
                    "wave_direction": 0,
                    "vessel_heading": 0,
                    "current": "10pct",
                    "vessel_id": "fb6df3a5-536a-4d13-994b-69693e46436e",
                    "xt": False,
                    "soil_profile": "calypsoapilowclay",
                    "overpull": 300,
                    "drillpipe_tension": 500,
                    "comment": "blablabla",
                    "offset_percent_of_wd": 0,
                    "client": "Har alltid rett AS",
                },
                "general_results": {
                    "m_eq_dominant_direction": 1,
                    "m_eq_local_scatter_dom_dir": 2,
                    "m_eq_NORSOK_scatter_dom_dir": 3,
                    "m_extreme_drilling": 4,
                    "m_extreme_nondrilling": 5,
                },
                "all_seastate_results": [],
            },
        ),
    ],
)
def test_post_vessels(app, route, called_with, obj_to_post):
    client = TestClient(app["app"])
    db_response = [{"foo": "bar"}]
    app["db_serv"].post_one_document.return_value = db_response
    response = client.post(route, json=obj_to_post)
    #    print(response.json())
    #    print(app['db_serv'].post_one_document.call_args_list)
    app["db_serv"].post_one_document.assert_called_once_with(
        called_with, {**obj_to_post, "id": None}
    )
    assert response.status_code == 200
    assert response.json() == db_response


def test_delete_analysis_id_not_in_db(app):
    app["db_serv"].delete_one_document_by_id.side_effect = CosmosResourceNotFoundError()
    client = TestClient(app["app"])
    response = client.delete("/api/analyses/my_id")
    assert response.status_code == 404
    assert response.text == "document with id my_id not found in analyses"
    app["db_serv"].delete_one_document_by_id.assert_called_once_with(
        "analyses", "my_id"
    )


def test_delete_analysis_error_from_db(app):
    app["db_serv"].delete_one_document_by_id.side_effect = CosmosHttpResponseError()
    client = TestClient(app["app"])
    response = client.delete("/api/analyses/my_id")
    assert response.status_code == 409
    assert response.text == "error response from database"
    app["db_serv"].delete_one_document_by_id.assert_called_once_with(
        "analyses", "my_id"
    )


def test_post_vessels_error_in_post_doc(app):
    client = TestClient(app["app"])
    obj_to_post = {"name": "test_rig", "id": "asdgha"}
    db_response = [{"foo": "bar"}]
    app["db_serv"].post_one_document.return_value = db_response
    response = client.post("/api/vessels", json=obj_to_post)
    assert response.status_code == 422


def test_delete_vessel_id_not_found(app):
    app["db_serv"].delete_one_document_by_id.side_effect = CosmosResourceNotFoundError()
    app["db_serv"].get_analysis_id_by_vesselid.return_value = []
    client = TestClient(app["app"])
    response = client.delete("/api/vessels/my_id")
    assert response.status_code == 404
    assert response.text == "document with id my_id not found in vessels"
    app["db_serv"].delete_one_document_by_id.assert_called_once_with("vessels", "my_id")
    app["db_serv"].get_analysis_id_by_vesselid.assert_called_once_with("my_id")


def test_delete_vessel_(app):
    app["db_serv"].delete_one_document_by_id.side_effect = [
        {"title": "response_from_delete"}
    ]
    app["db_serv"].get_analysis_id_by_vesselid.return_value = []
    print(app["db_serv"])
    client = TestClient(app["app"])
    response = client.delete("/api/vessels/my_id")
    assert response.status_code == 200
    assert response.json() == {"title": "response_from_delete"}
    app["db_serv"].delete_one_document_by_id.assert_called_once_with("vessels", "my_id")


def test_delete_vessel_vessel_refered_to_in_analyses(app):
    app["db_serv"].delete_one_document_by_id.side_effect = [
        {"title": "response_from_delete"}
    ]
    app["db_serv"].get_analysis_id_by_vesselid.return_value = [
        {"id": "my_id_1"},
        {"id": "my_id_2"},
    ]
    client = TestClient(app["app"])
    response = client.delete("/api/vessels/my_id")
    assert response.status_code == 409
    assert response.json() == {
        "error_message": "document with id my_id cannot be deleted, the vessel is refered to in 2 analyses",
        "analyses_ids": ["my_id_1", "my_id_2"],
    }


#    app['db_serv'].delete_one_document_by_id.assert_called_once_with("vessels", "my_id")


@pytest.mark.parametrize(
    "patch_list, dbserv_response, expected_status_code, expected_json",
    [
        (
            [{"op": "replace", "path": "test/dummypath", "value": "newvalue"}],
            CosmosHttpResponseError(),
            409,
            {"error_message": "error response from database"},
        ),
        (
            [{"op": "replace", "path": "test/dummypath", "value": "newvalue"}],
            CosmosResourceNotFoundError(),
            404,
            {"error_message": "document with id my_id not found in vessels"},
        ),
        (
            [{"op": "replace", "path": "test/dummypath", "value": "newvalue"}],
            [{"foo": "bar"}],
            200,
            {"foo": "bar"},
        ),
    ],
)
def test_patch_vessel(
    app, patch_list, dbserv_response, expected_status_code, expected_json
):
    app["db_serv"].patch_one_document.side_effect = dbserv_response
    client = TestClient(app["app"])
    response = client.patch("/api/vessels/my_id", json=patch_list)
    #    print(response.status_code, response.json())
    assert response.status_code == expected_status_code
    assert response.json() == expected_json
