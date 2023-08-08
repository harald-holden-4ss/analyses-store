import pytest
from unittest.mock import patch, Mock, MagicMock, call
from app.services.database_service import database_service


@pytest.fixture
@patch("app.services.database_service.os")
@patch("app.services.database_service.CosmosClient")
def mock_sql_client(cosmos_client_mock: MagicMock, os_mock: MagicMock):
    os_mock.getenv.side_effect = ["os_val_1", "os_val_2"]
    return_client = MagicMock()
    return_client.get_database_client.return_value = "dummy"
    cosmos_client_mock.return_value = return_client
    serv = database_service()
    return cosmos_client_mock, os_mock, serv


def test_database_service_constructor(mock_sql_client):
    cosmos_client_mock, os_mock, mocked_serv = mock_sql_client
    cosmos_client_mock.assert_called_once_with("os_val_1", "os_val_2")
    os_getenv_calls = os_mock.getenv.call_args_list
    assert os_getenv_calls[0] == call("SQLAZURECONNSTR_AZURE_COSMOS_DB_HOST")
    assert os_getenv_calls[1] == call("SQLAZURECONNSTR_AZURE_COSMOS_DB_MASTER_KEY")
    mocked_serv.client.get_database_client.assert_called_once_with("dynops-store-data")


@patch("app.services.database_service._remove_internal_dict_keys")
def test_database_service_get_one_document_by_id(
    remove_dict_keys_mock, mock_sql_client
):
    remove_dict_keys_mock.side_effect = ["res_1", "res_2", "res_3", "res_4", "res_5"]
    db_query_results = [{"key1": "key1item1", "key2": "key2item1"}]
    _, _, database_service_mockedDB = mock_sql_client
    database_service_mockedDB.data_base_proxy = MagicMock()
    cosmos_container_client_mock = MagicMock(id="CosmosContainerClientMock")
    database_service_mockedDB.data_base_proxy.get_container_client.return_value = (
        cosmos_container_client_mock
    )
    cosmos_container_client_mock.query_items.return_value = db_query_results
    return_value = database_service_mockedDB.get_one_document_by_id(
        "dummy_collection", "my_id_1"
    )
    assert return_value == "res_1"
    cosmos_container_client_mock.query_items.assert_called_once_with(
        query="SELECT * FROM d WHERE  d.id =@id",
        parameters=[{"name": "@id", "value": "my_id_1"}],
        enable_cross_partition_query=True,
    )
    for call_num, mock_call in enumerate(remove_dict_keys_mock.call_args_list):
        assert call(db_query_results[call_num]) == mock_call
    database_service_mockedDB.data_base_proxy.get_container_client.assert_called_once_with(
        "dummy_collection"
    )


def test_database_service_delete_one_document_by_id(mock_sql_client):
    db_query_results = [{"key1": "key1item1", "key2": "key2item1"}]
    _, _, database_service_mockedDB = mock_sql_client
    database_service_mockedDB.data_base_proxy = MagicMock()
    cosmos_container_client_mock = MagicMock(id="CosmosContainerClientMock")
    database_service_mockedDB.data_base_proxy.get_container_client.return_value = (
        cosmos_container_client_mock
    )
    cosmos_container_client_mock.delete_item.return_value = db_query_results
    return_value = database_service_mockedDB.delete_one_document_by_id(
        "dummy_collection", "my_id_1"
    )
    assert db_query_results == return_value
    cosmos_container_client_mock.delete_item.assert_called_once_with(
        item="my_id_1", partition_key="my_id_1"
    )
    database_service_mockedDB.data_base_proxy.get_container_client.assert_called_once_with(
        "dummy_collection"
    )


@patch("app.services.database_service._remove_internal_dict_keys")
def test_database_service_get_all_documents(remove_dict_keys_mock, mock_sql_client):
    remove_dict_keys_mock.side_effect = ["res_1", "res_2", "res_3", "res_4", "res_5"]
    db_query_results = [
        {"key1": "key1item1", "key2": "key2item1"},
        {"key1": "key1item2", "key2": "key2item2"},
        {"key1": "key1item3", "key2": "key2item3"},
        ]
    _, _, database_service_mockedDB = mock_sql_client
    database_service_mockedDB.data_base_proxy = MagicMock()
    cosmos_container_client_mock = MagicMock(id="CosmosContainerClientMock")
    database_service_mockedDB.data_base_proxy.get_container_client.return_value = (
        cosmos_container_client_mock
    )
    cosmos_container_client_mock.read_all_items.return_value = db_query_results
    return_value = database_service_mockedDB.get_all_documents(
        "dummy_collection"
    )
    assert return_value == ["res_1", "res_2", "res_3"]
    cosmos_container_client_mock.read_all_items.assert_called_once_with( )
    database_service_mockedDB.data_base_proxy.get_container_client.assert_called_once_with(
        "dummy_collection"
    )


@patch("app.services.database_service._remove_internal_dict_keys")
def test_database_service_replace_one_document(remove_dict_keys_mock, mock_sql_client):
    remove_dict_keys_mock.side_effect = ["res_1", "res_2", "res_3", "res_4", "res_5"]
    db_query_results = {"key1": "key1item1", "key2": "key2item1"}
    _, _, database_service_mockedDB = mock_sql_client
    database_service_mockedDB.data_base_proxy = MagicMock()
    cosmos_container_client_mock = MagicMock(id="CosmosContainerClientMock")
    database_service_mockedDB.data_base_proxy.get_container_client.return_value = (
        cosmos_container_client_mock
    )
    cosmos_container_client_mock.replace_item.return_value = db_query_results
    return_value = database_service_mockedDB.replace_one_document(
        collection_name="dummy_collection", 
        doc_id="dummy_doc_id", 
        replace_item={"foo": "bar"}
    )
    assert return_value == db_query_results
    cosmos_container_client_mock.replace_item.assert_called_once_with(
        item="dummy_doc_id", body={"foo": "bar"}
     )
    database_service_mockedDB.data_base_proxy.get_container_client.assert_called_once_with(
        "dummy_collection"
    )
