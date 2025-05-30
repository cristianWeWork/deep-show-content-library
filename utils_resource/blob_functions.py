import os

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
conne_str = os.getenv('CONN_STRING_BLOB')
account_name = "cristian"

blob_service_client = BlobServiceClient.from_connection_string(str(conne_str))
container_name = "tts-deepshow"
container_client = blob_service_client.get_container_client(container_name)

def upload_File(file, blob_name):
    print("subiendo")
    container_name =  "tts-deepshow"
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    with open(file, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    return blob_client.url

def upload_background(file, blob_name):
    print("subiendo")
    container_name =  "backgrounds-deepshow"
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.file, overwrite=True)
    return blob_client.url

def upload_shows(file, blob_name):
    print("subiendo")
    container_name =  "shows-deepshow"
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.file, overwrite=True)
    return blob_client.url

def upload_avatars(file, blob_name):
    print("subiendo")
    container_name =  "avatars-deepshow"
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.file, overwrite=True)
    return blob_client.url


def upload_blob_directory(name):
    container_name = "emb-databases"
    container_client = blob_service_client.get_container_client(container_name)
    azure_folder_prefix = name + "/"
    blob_client = container_client.get_blob_client(azure_folder_prefix)
    blob_client.upload_blob("", overwrite=True)
    for root, _, files in os.walk(name):
        for file in files:
            local_file_path = os.path.join(root, file)
            azure_blob_name = azure_folder_prefix + os.path.relpath(local_file_path, name)
            blob_client = container_client.get_blob_client(azure_blob_name)
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(data)
                
