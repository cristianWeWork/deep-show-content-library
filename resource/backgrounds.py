from dotenv import load_dotenv
import database.nonSqlDatabase as mongoDb
import resource.blob_functions as blobf
import database.database as db

load_dotenv()




def uploadBackgrounds(file):
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


def uploadThemes(name, audioFile, imageFile):
    print("Subiendo preview")
    url_preview = blobf.upload_background(imageFile, imageFile.filename)
    print("Subiendo preview")
    url_sound = blobf.upload_background(audioFile, audioFile.filename)
    data = {
        "music_url" : url_sound,
        "preview": url_preview,
        "name": name
    }
    db.AddTheme(name,url_preview,url_sound)
    
