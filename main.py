from typing import Any, Optional
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import database.database as db
import database.nonSqlDatabase as mongoDb
from resource import blob_functions
import resource.backgrounds as bkg
from resource.tts import (
    getAudioTextEleven,
    getVoiceOptionsEleven,
    getVoicesList,
    getVoiceOptions,
    getAudioText,
)

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class newUser(BaseModel):
    username: str
    password: str
    email: str
    name: str
    surname: str


class loginUser(BaseModel):
    username: str
    password: str


class itemToSpeech(BaseModel):
    text: str
    voice: str
    language: str
    format: Optional[str] = "wav"
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "voice": "es-CU-BelkysNeural",
                    "text": "Muy buenas, Bienvenidos a los juegos del hambre",
                    "language": "Spanish (Cuba)",
                    "format": "ogg",
                }
            ]
        }
    }

class VoiceModel(BaseModel):
    voice_id: str
    name: str
    age: str
    accent: str
    gender: str
    preview_url: str

class ShowEmittedModel(BaseModel):
    userId: int
    presenterName: str
    voice: VoiceModel
    avatar: int
    graphics: int
    texto: str
    background: str
    url_show: Optional[str] = None  
    
class itemToSpeechEleven(BaseModel):
    name: str
    text: str
    voice_id: str
    model_id: str
    voice_settings: Any
    format: Optional[str] = "wav"


class ImageUpload(BaseModel):
    image: UploadFile


@app.get("/")
async def root():
    return {"greeting": "Hello world"}


@app.get("/getUser/")
async def getUser(userName: str):
    try:
        result = mongoDb.get_user(userName)
    except:
        raise HTTPException(status_code=404, detail="Problemas con la base de datos")
    user = {
        "id":result["id"],
        "name": result["name"],
        "surname": result["surname"],
        "username": result["username"],
        "email": result["email"],
        "subscription": result["subscription"],
    }

    return user


@app.post("/register/")
async def registerUser(data: newUser):
    return mongoDb.register_new_user(
        data.username, data.password, data.email, data.name, data.surname
    )


@app.post("/login/")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    return mongoDb.login_for_access_token(data)


@app.get("/getVoicesList/")
async def textToSpeech():
    return getVoiceOptions("Spanish")


@app.get("/getElevenVoicesList")
async def getListVoices():
    return getVoiceOptionsEleven()


@app.post("/textToSpeech/")
async def getTextToSpeech(item: itemToSpeech):
    print("paso 1")
    query = {"voz": item.voice, "text": item.text, "format": item.format}
    result = mongoDb.find_document(query)
    print(result)

    if result == None:
        print("paso 2")
        # type: ignore
        url_audio, id, visemes, blendShapes, provider = await getAudioText(
            item.text, item.voice, item.language, item.format
        )
        response = {
            "url_audio": url_audio,
            "id": id,
            "visemes": visemes,
            "blendShapes": blendShapes,
            "provider": provider,
        }
        return response
    else:
        print("paso 3")
        response = {
            "url_audio": result["url_audio"],
            "id": result["_id"],
            "visemes": result["visemes"],
            "blendShapes": result["blendShapes"],
        }
        return response


@app.post("/textToSpeechEleven/")
async def getTextToSpeechEleven(item: itemToSpeechEleven):
    print("paso 1")
    query = {"voz": item.name, "text": item.text, "format": item.format}
    result = mongoDb.find_document(query)
    print(result)

    if result == None:
        print("paso 2")
        # type: ignore
        url_audio, document_id, visemes, provider = await getAudioTextEleven(
            item.text,
            item.voice_id,
            item.voice_settings,
            item.format,
            item.name,
            item.model_id,
        )
        response = {
            "url_audio": url_audio,
            "id": document_id,
            "visemes": visemes,
            "provider": provider,
        }
        return response
    else:
        print("paso 3")
        response = {
            "url_audio": result["url_audio"],
            "id": result["_id"],
            "visemes": result["visemes"],
            "provider": result["provider"],
        }
        return response


@app.post("/upload_background/")
async def upload_background(image: UploadFile = File(...)):
    print(image)
    result = bkg.uploadBackgrounds(image)
    return result

@app.post("/upload_show/")
async def upload_show(show: UploadFile = File(...)):
    result = bkg.uploadShow(show)
    return result
    
@app.get("/getBackgrounds/")
async def getBackgrounds():
    result = bkg.getBackgrounds()
    return result


@app.post("/addTheme/")
async def addTheme(
    name: str = Form(...),
    audio_file: UploadFile = File(...),
    image_file: UploadFile = File(...),
):
    result = bkg.uploadThemes(name, audio_file, image_file)
    return result


@app.post("/addShow/")
async def add_show(show: ShowEmittedModel):
    # Aquí puedes guardar show.dict() en la base de datos o hacer lo que necesites
    result = bkg.addShow(show)
    
    return {"message": "Show guardado correctamente", "data": result}


@app.get("/getThemes/")
async def getThemes():
    result = mongoDb.get_themes()
    return result


@app.post("/addGraphics/")
async def addGraphics(
    theme_id: str = Form(...),
    intro: UploadFile = File(...),
    end: UploadFile = File(...),
    lowerThird: UploadFile = File(...),
    transition: UploadFile = File(...),
):
    result = bkg.uploadGraphics(theme_id, intro, end, lowerThird, transition)
    return result


@app.post("/addAvatar/")
async def addAvatar(
    name: str = Form(...),
    jsonFile: UploadFile = File(...),
    webmFile: UploadFile = File(...),
    imageFile: UploadFile = File(...),
    gender=Form(...),
):
    result = bkg.uploadAvatars(name, jsonFile, gender, webmFile, imageFile)
    return result


@app.get("/getAvatars/")
async def getAvatars():
    return mongoDb.get_avatars()

@app.post("/save_show/")
async def add_show(show: ShowEmittedModel):
    # Aquí puedes guardar show.dict() en la base de datos o hacer lo que necesites
    result = bkg.addShow(show)
    return {"message": "Show guardado correctamente", "data": result}


@app.post("/uploadFile/")
async def postFile(
    name: str = Form(...),
    file: UploadFile = File(...),
):
    return bkg.uploadFile(name, file)

@app.get("/getShowsByUser/")
async def GetShows(
    user_id:int
):
    result = bkg.getShows(user_id)
    return result