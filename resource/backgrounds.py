import os
from dotenv import load_dotenv
import requests
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech.audio import AudioOutputConfig, AudioOutputStream
from dotenv import load_dotenv
import datetime
import database.nonSqlDatabase as mongoDb
import resource.blob_functions as blobf
load_dotenv()




def uploadBackgrounds(file):
    print(file)
    url_background = blobf.upload_background(file, file.filename)
    print(url_background)
    data = {
        "url_background" : url_background
    }

    id = mongoDb.insert_background(data)
   
    
    return str(id)

def getBackgrounds():
    backgrounds = mongoDb.getBackgrounds()
    return backgrounds