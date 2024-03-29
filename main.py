from typing import Optional
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import database.database as db
import database.nonSqlDatabase as mongoDb
import resource.backgrounds as bkg
from resource.tts import getVoicesList, getVoiceOptions, getAudioText
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
                    "format": "ogg"
                }
            ]
        }
    }


class ImageUpload(BaseModel):
    image: UploadFile


@app.get("/")
async def root():
    return {"greeting": "Hello world"}


@app.get("/getUser")
async def getUser(userName: str):
    try:
        result = db.getUser(userName)
    except:
        raise HTTPException(
            status_code=404, detail='Problemas con la base de datos')
    user = {
        "name": result.name,
        "surname": result.surname,
        "username": result.username,
        "email": result.email,
        "subscription": result.subscription
    }

    return user


@app.post("/register")
async def registerUser(data: newUser):
    return db.register_new_user(data.username, data.password, data.email, data.name, data.surname)


@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    return db.login_for_access_token(data)


@app.get("/getVoicesList/")
async def textToSpeech():
    return getVoiceOptions("Spanish")


@app.post("/textToSpeech/")
async def getTextToSpeech(item: itemToSpeech):
    print("paso 1")
    query = {
        "voz": item.voice,
        "text": item.text,
        "format": item.format
    }
    result = mongoDb.find_document(query)
    print(result)

    if result == None:
        print("paso 2")
        # type: ignore
        url_audio, id, visemes, blendShapes = await getAudioText(item.text, item.voice, item.language, item.format)
        response = {
            "url_audio": url_audio,
            "id": id,
            "visemes": visemes,
            "blendShapes": blendShapes
        }
        return response
    else:
        print("paso 3")
        response = {
            "url_audio": result['url_audio'],
            "id": result['_id'],
            "visemes": result['visemes'],
            "blendShapes": result['blendShapes']
        }
        return response


@app.post("/upload_background/")
async def upload_background(image: UploadFile = File(...)):
    print(image)
    result = bkg.uploadBackgrounds(image)
    return result


@app.get("/getBackgrounds/")
async def getBackgrounds():
    result = bkg.getBackgrounds()
    return result


@app.post("/addTheme")
async def addTheme(name: str = Form(...), audio_file: UploadFile = File(...), image_file: UploadFile = File(...)):
    result = bkg.uploadThemes(name, audio_file, image_file)
    return result

@app.get("/getThemes/")
async def getThemes():
    result = db.getThemes()
    return result

@app.post("/addGraphics/")
async def addGraphics(theme_id: str = Form(...), intro: UploadFile = File(...), end: UploadFile = File(...), lowerThird: UploadFile = File(...), transition: UploadFile = File(...)):
    result = bkg.uploadGraphics(theme_id, intro, end,lowerThird, transition)
    return result