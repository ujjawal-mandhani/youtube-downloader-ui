from pymongo import MongoClient
from utility.custom_logger import logger
from bson.json_util import dumps
import json

client = MongoClient(f"mongodb://root:example@mongo:27017/")

def insert_document(collection_name, data, parameters_to_check, db_name="default_db"):
    """
        parameters_to_check to provide in array it will check in mongo db if any document exist of that key
        for example unique keys may be pan, adhar, username, id etc.
    """
    err_mssg = "signup successfully"
    try:
        db = client[db_name]
        collection = db[collection_name]
        for attribute in parameters_to_check:
            attribute_arry = attribute.split('.')
            final_data = None
            for item in attribute_arry:
                final_data = final_data.get(item) if final_data is not None and type(final_data).__name__ == 'dict' else data.get(item)
            query = {attribute: final_data}
            exists = collection.find_one(query) is not None
            if exists:
                err_mssg = "Attribute " + attribute + " existing in databse with value " + final_data
                logger.info(err_mssg)
                raise Exception(err_mssg)
        result = collection.insert_one(data)
        return 200, err_mssg, result.inserted_id
    except Exception as E:
        logger.error("::::Error while inserting data")
        logger.info(E)
    return 400, err_mssg, None

def find_document(collection_name, query, db_name="default_db", skip = None, limit = None):
    err_mssg = ""
    try:
        db = client[db_name]
        collection = db[collection_name]
        document = collection.find(query)
        if skip is not None:
            document = document.skip(skip)
        if limit is not None:
            document = document.limit(limit)
        if limit is None:
            document = next(document, None)
        else:
            document = list(document)
        if document is not None:
            return 200, json.loads(dumps(document))
        else:
            err_mssg = "data does not exist"
            raise Exception(err_mssg)
    except Exception as E:
        logger.error("::::Error while Searching data")
        logger.info(E)
        return 400, err_mssg