from azure.cosmos import CosmosClient
import uuid


class database_service(object):
    def __init__(self):
        HOST = "https://expert-service-analysis-store-data.documents.azure.com:443/"
        MASTER_KEY = "SfRTCeE27yp00EJ9FjOravq6wuHeD9XCjkNQ3z7XTLbkNksn2z47EacFlsUcrnDheMzLP7ROiupNACDb5M7Vrg=="
        self.client = CosmosClient(HOST, MASTER_KEY)
        self.data_base_proxy = self.client.get_database_client("dynops-store-data")

    def get_one_document_by_id(self, collection_name: str, document_id: str):
        container = self.data_base_proxy.get_container_client(collection_name)
        q_string = 'SELECT * FROM d WHERE  d.id =@id'
        q_results = container.query_items(
            query=q_string,
            parameters=[
                { "name":"@id", "value": document_id }
            ],
            enable_cross_partition_query=True,
        )
        return [_remove_internal_dict_keys(c) for c in list(q_results)][0]

    def delete_one_document_by_id(self, collection_name: str, document_id: str):
        container = self.data_base_proxy.get_container_client(collection_name)
        ret_value = container.delete_item(item=document_id, partition_key=document_id)
        return ret_value

    def get_all_documents(self, collection_name: str):
        container = self.data_base_proxy.get_container_client(collection_name)
        return [_remove_internal_dict_keys(c) for c in container.read_all_items()]

    def replace_one_document(self, collection_name: str, doc_id: str, replace_item: dict):
        container = self.data_base_proxy.get_container_client(collection_name)
        container.replace_item(doc_id, replace_item)

    def post_one_document(self, collection_name: str, document: dict):
        document["id"] = str(uuid.uuid4())
        container = self.data_base_proxy.get_container_client(collection_name)
        ret_value = container.create_item(body=document)
        return_dict = _remove_internal_dict_keys(ret_value)
        return return_dict


def _remove_internal_dict_keys(inp_dict):
    return {
        k: v
        for k, v in inp_dict.items()
        if k not in ["_rid", "_self", "_etag", "_attachments", "_ts"]
    }
