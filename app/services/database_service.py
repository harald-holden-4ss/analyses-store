from azure.cosmos import CosmosClient
import uuid
import os
from ..models.jsonpatch import json_patch_modify
import jsonpatch

class database_service(object):
    """Service object to handle data stored in the azure cosmos db document
    database

    Parameters
    ----------
    object : _type_
        _description_
    """
    def __init__(self):
        HOST = os.getenv("SQLAZURECONNSTR_AZURE_COSMOS_DB_HOST")
        MASTER_KEY = os.getenv("SQLAZURECONNSTR_AZURE_COSMOS_DB_MASTER_KEY")

        self.client = CosmosClient(HOST, MASTER_KEY)
        self.data_base_proxy = self.client.get_database_client("dynops-store-data")

    def get_one_document_by_id(self, collection_name: str, document_id: str):
        """Gets one document from the azure cosmos document database

        Parameters
        ----------
        collection_name : str
            The name of the container to extract documents from.  Can be one of the 
            following["analyses", "vessels", "settings"]
        document_id : str
            The id of the document to extract

        Returns
        -------
        dict
            A dictionarry containing the document with the document id.  The key 
            value pairs of internal azure database dict keys ("_rid", "_self", 
            "_etag", "_attachments", "_ts") are removed.
        """
        container = self.data_base_proxy.get_container_client(collection_name)
        q_string = "SELECT * FROM d WHERE  d.id =@id"
        q_results = container.query_items(
            query=q_string,
            parameters=[{"name": "@id", "value": document_id}],
            enable_cross_partition_query=True,
        )
        q_results = list(q_results)
        if len(q_results) < 1:
            return []
        else:
            return [_remove_internal_dict_keys(c) for c in list(q_results)][0]

    def delete_one_document_by_id(self, collection_name: str, document_id: str):
        """Deletes one document

        Parameters
        ----------
        collection_name : str
            The name of the container to extract documents from.  Can be one of the 
            following["analyses", "vessels", "settings"]
        document_id : str
            The id of the document to delete

        Returns
        -------
        _type_
            _description_
        """
        container = self.data_base_proxy.get_container_client(collection_name)
        ret_value = container.delete_item(item=document_id, partition_key=document_id)
        return ret_value
            

    def get_all_documents_short(self, collection_name: str, selected_keys: list):
        """Gets all docuemtns from the given collection, returning only the document
        keys in the selected_keys list

        Parameters
        ----------
        collection_name : str
            The name of the container to extract documents from.  Can be one of the 
            following["analyses", "vessels", "settings"]

        Returns
        -------
        list
            A list of dictionarry containing all the documents in the given collection
            
        """
        container = self.data_base_proxy.get_container_client(collection_name)
        q_string = 'SELECT VALUE {'
        firstiter = True
        for selected_key in selected_keys:
            if firstiter:
                firstiter = False
            else:
                q_string += ","
                
            q_string += f'{selected_key}: d.{selected_key}'
        q_string += "} FROM d"
        items = container.query_items(
                query=q_string,
                parameters=[],
                enable_cross_partition_query=True,
            )

        return list(items)

    def get_all_documents(self, collection_name: str):
        """_summary_

        Parameters
        ----------
        collection_name : str
            The name of the container to extract documents from.  Can be one of the 
            following["analyses", "vessels", "settings"]

        Returns
        -------
        list
            A list of dictionarry containing all the documents in the given collection
            The key value pairs of internal azure database dict keys ("_rid", "_self", 
            "_etag", "_attachments", "_ts") are removed.
        """
        container = self.data_base_proxy.get_container_client(collection_name)
        return [_remove_internal_dict_keys(c) for c in container.read_all_items()]

    def replace_one_document(
        self, collection_name: str, doc_id: str, replace_item: dict
    ):
        """_summary_

        Parameters
        ----------
        collection_name : str
            The name of the container to extract documents from.  Can be one of the 
            following["analyses", "vessels", "settings"]
        document_id : str
            The id of the document to be replaced
        replace_item : dict
            Dictionarry containing the elements to be replaced.  All dict keys in 
            the replace_item dict will be replaced, dict keys in the database object 
            not in the replace_item dict will be unchanged.

        Returns
        -------
        dict
            Dictionarry containing the complete document after the given 
            key-value pairs have been replaced
        """
        container = self.data_base_proxy.get_container_client(collection_name)
        return container.replace_item(item=doc_id, body=replace_item)

    def post_one_document(self, collection_name: str, document: dict):
        """Post a new documnet into the database.  A new document id will
        be created, and the "id" will be set to this value (if the "id" key
        exists it will be overwritten)

        Parameters
        ----------
         collection_name : str
            The name of the container to extract documents from.  Can be one of the 
            following["analyses", "vessels", "settings"]
        document : dict
            The document to be posted into the database

        Returns
        -------
        dict
            A dict containing the document inserted into the database
        """
        document["id"] = str(uuid.uuid4())
        container = self.data_base_proxy.get_container_client(collection_name)
        ret_value = container.create_item(body=document)
        return_dict = _remove_internal_dict_keys(ret_value)
        return return_dict

    def patch_one_document(self, collection_name: str, 
                           document_id: str, updates: list[dict]):
        """Patch a documnet in the database using the RFC 6902 patch syntax 

        Parameters
        ----------
         collection_name : str
            The name of the container to extract documents from.  Can be one of the 
            following["analyses", "vessels", "settings"]
        document_id : str
            a string containing the guid of the document to be patched
        updates: list[dict]
            a list of dicts containing the patches to be done.  All updates are given as
            a dict on the following form:
                [
                    {
                        "op": string with the operation to performe ("add", "replace", "remove") 
                        "path": string with the path where the operation should be applied 
                        "value": the value (for replace or add operations)
                
                    }
                ] 

        Returns
        -------
        dict
            A dict containing the document inserted into the database
        """
        update_document = self.get_one_document_by_id(
                collection_name=collection_name, document_id=document_id)
        
        update_document = jsonpatch.apply_patch(update_document, updates)
        
        return self.replace_one_document(
            collection_name=collection_name, 
            doc_id=document_id,
            replace_item=update_document)
    def get_analysis_id_by_vesselid(self, vessel_id):
        """Patch a documnet in the database using the RFC 6902 patch syntax 

        Parameters
        ----------
         collection_name : str
            The name of the container to extract documents from.  Can be one of the 
            following["analyses", "vessels", "settings"]
        document_id : str
            a string containing the guid of the document to be patched
        updates: list[dict]
            a list of dicts containing the patches to be done.  All updates are given as
            a dict on the following form:
                [
                    {
                        "op": string with the operation to performe ("add", "replace", "remove") 
                        "path": string with the path where the operation should be applied 
                        "value": the value (for replace or add operations)
                
                    }
                ] 

        Returns
        -------
        dict
            A dict containing the document inserted into the database
        """
        container = self.data_base_proxy.get_container_client("analyses")
        q_string = "SELECT d.id, d.metadata.vessel_id FROM d WHERE  d.metadata.vessel_id =@vessel_id"
        q_results = container.query_items(
            query=q_string,
            parameters=[{"name": "@vessel_id", "value": vessel_id}],
            enable_cross_partition_query=True,
        )
        q_results = list(q_results)
        if len(q_results) < 1:
            return []
        else:
            return q_results
    


def _remove_internal_dict_keys(inp_dict):
    return {
        k: v
        for k, v in inp_dict.items()
        if k not in ["_rid", "_self", "_etag", "_attachments", "_ts"]
    }
