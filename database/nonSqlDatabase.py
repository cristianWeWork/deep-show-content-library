import pymongo
import os

bbdd_conn = os.getenv('BBDD_MONGO')
myclient = pymongo.MongoClient(bbdd_conn)

mydb = myclient["WeWork"]
collection = mydb["TTS_COLLECTION"]

def showDBlist():
    print(myclient.list_database_names)
    return myclient.list_database_names
    
# Create (Crear)
def insert_document(data):
    inserted_doc = collection.insert_one(data)
    print(f"Documento insertado con ID: {inserted_doc.inserted_id}")
    return inserted_doc.inserted_id

# Read (Leer)
def find_document(query):
    result = collection.find_one(query, sort=[("_id", -1)])
    print (result)
    if result and "_id" in result:
         result["_id"] = str(result['_id'])

    return result
    

# Update (Actualizar)
def update_document(query, data):
    updated_doc = collection.update_one(query, {"$set": data})
    return updated_doc.modified_count

def update_url_audio(query, data):
    updated_doc = collection.update_one(query, {"$set" : data})
    return updated_doc.modified_count
# Delete (Borrar)
def delete_document(query):
    deleted_doc = collection.delete_one(query)
    return deleted_doc.deleted_count
    