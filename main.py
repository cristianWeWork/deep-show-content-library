from calendar import c
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import database.database as db
from resource.tts import getVoicesList, getVoiceOptions
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
    username:str
    password:str
    email:str
    name:str
    surname:str

class loginUser(BaseModel):
    username:str
    password:str

@app.get("/")
async def root():
 return {"greeting":"Hello world"}

@app.get("/getUser")
async def getUser(userName : str):
    try:
        result = db.getUser(userName)
    except:
         raise HTTPException(status_code=404, detail='Problemas con la base de datos')
    user = {
        "name": result.name,
        "surname": result.surname,
        "username": result.username,
        "email": result.email,
        "subscription" : result.subscription
    }
    
    return user
    
   

@app.post("/register")
async def registerUser(data: newUser):
    return db.register_new_user(data.username, data.password,data.email,data.name,data.surname)

@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    return db.login_for_access_token(data)


@app.get("/getVoicesList/")
async def textToSpeech():
    return getVoiceOptions("Spanish")

