from typing import Annotated
from fastapi import Depends, HTTPException, status
import pymongo
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson import ObjectId
from datetime import datetime, timedelta
TODAY = datetime.now()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

bbdd_conn = os.getenv('BBDD_MONGO')
myclient = pymongo.MongoClient(bbdd_conn)

mydb = myclient["deep-show-db"]
collection = mydb["tts_collection"]
graphics_collection = mydb["graphics"]
subs_collection = mydb["subscription"]
themes_collection = mydb["themes"]
users_collection = mydb["users"]
avatars_collection = mydb["avatars"]
avatar_video_shot_collection = mydb["avatar_video_shot"]
shows_collection = mydb["shows"]
background_collection = mydb["background_collection"]
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
    print(collection)
    result = collection.find_one(query, sort=[("_id", -1)])
    print(result)
    if result and "_id" in result:
        result["_id"] = str(result['_id'])

    return result


# Update (Actualizar)
def update_document(query, data):
    updated_doc = collection.update_one(query, {"$set": data})
    return updated_doc.modified_count


def update_url_audio(query, data):
    updated_doc = collection.update_one(query, {"$set": data})
    return updated_doc.modified_count
# Delete (Borrar)


def delete_document(query):
    deleted_doc = collection.delete_one(query)
    return deleted_doc.deleted_count


def insert_background(data):
    collectionBkg = mydb["background_collection"]
    inserted_doc = collectionBkg.insert_one(data)
    print(f"Documento insertado con ID: {inserted_doc.inserted_id}")
    return inserted_doc.inserted_id


def getBackgrounds():
    collectionBkg = mydb["background_collection"]

    backgrounds_list = []

    for x in collectionBkg.find():

        x["_id"] = str(x["_id"])
        backgrounds_list.append(x)

    return backgrounds_list

def get_next_user_id():
    # Obtener el último ID registrado
    last_user = users_collection.find_one(sort=[("id", -1)])  # Encuentra el usuario con el mayor ID
    if last_user:
        return last_user["id"] + 1  # Incrementa el último ID en 1
    else:
        return 1  # Si no hay usuarios, el primer ID será 1

def register_new_user(username, password, email, name, surname):
    # Obtener el siguiente ID para el nuevo usuario
    user_id = get_next_user_id()

    # Hashear la contraseña
    hashed_pass = pwd_context.hash(password)

    # Crear el nuevo usuario
    new_user = {
        "id": user_id,  # ID auto-incremental
        "username": username,
        "password": hashed_pass,
        "email": email,
        "name": name,
        "surname": surname,
        "created_at": TODAY,
        "subscription": 1,
    }

    # Insertar el nuevo usuario en la colección
    usuario_inserted = users_collection.insert_one(new_user)
    
    return {"message": f"Usuario insertado con id: {usuario_inserted.inserted_id}"}


def authenticate_user(username: str, password: str):
    user = get_user_login(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


def get_user_login(username: str):
    try:
        user = users_collection.find_one({"username": username})
        if user:

            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        print(f"Error al obtener el usuario: {e}")
        return None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    try:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError as e:
        print(f"Error al codificar el token: {e}")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        print(f"Error al codificar el token: {e}")


def add_theme(name: str, preview: str, music_url: str):
    # Buscar el documento con el id más alto
    ultimo_producto = themes_collection.find().sort("id", -1).limit(1)

    ultimo_id = 1
    for producto in ultimo_producto:
        if 'id' in producto:
            ultimo_id = producto['id'] + 1
            break

    new_theme = {
        "id": ultimo_id,
        "name": name,
        "preview": preview,
        "music_url": music_url
    }

    themes_collection.insert_one(new_theme)
    return {"message": f"Tema añadido correctamente con ID: {ultimo_id}"}



def get_themes():
    themes_list = list(themes_collection.find())
    for theme in themes_list:
        theme["_id"] = str(theme["_id"])
        theme["graphics"] = get_graphics_for_theme(theme["_id"])

    return themes_list


def get_graphics_for_theme(theme_id):
    graphics_list = list(graphics_collection.find({"theme_id": theme_id}))
    for graphic in graphics_list:
        graphic["_id"] = str(graphic["_id"])
    print(graphics_list)
    return graphics_list


def add_graphics(theme_id: str, url: str, graphic_type: str):
    new_graphic = {
        "theme_id": theme_id,
        "url": url,
        "type": graphic_type
    }
    graphic_inserted = graphics_collection.insert_one(new_graphic)
    return {"message": f"Gráfico añadido correctamente con ID: {graphic_inserted.inserted_id}"}


def get_user(username):
    try:
        user = users_collection.find_one({"username": username})
        if user:
            user["_id"] = str(user["_id"])
            return user
        else:
            raise Exception("No se encuentra ese usuario, mi niño")
    except Exception as e:
        return str(e)


def add_user(theme_id: str, url: str, graphic_type: str):
    new_graphic = {
        "theme_id": theme_id,
        "url": url,
        "type": graphic_type
    }
    graphic_inserted = graphics_collection.insert_one(new_graphic)
    return {"message": f"Gráfico añadido correctamente con ID: {graphic_inserted.inserted_id}"}

avatars_collection.create_index([("id_avatar", pymongo.ASCENDING)])

def add_avatars(name: str, url_img: str, url_json: str, url_webm: str, gender: str):
  # Obtener el último ID insertado y autoincrementar
    last_avatar = avatars_collection.find_one(sort=[("id_avatar", -1)])
    new_id = last_avatar["id_avatar"] + 1 if last_avatar else 1

    # Insertar en avatars_collection
    new_avatar = {
        "nombre": name,
        "genero": gender,
        "id_avatar": new_id
    }
    avatar_inserted = avatars_collection.insert_one(new_avatar)

    # Insertar en avatar_video_shot_collection
    new_avatar_video_shot = {
        "url_img": url_img,
        "url_json": url_json,
        "url_video": url_webm,
        "id_avatar": new_id
    }
    avatar_video_shot_collection.insert_one(new_avatar_video_shot)

    return {"message": f"Avatar añadido correctamente con ID: {new_id}"}


def add_show(show_data):
    # Obtener el último ID y autoincrementar
    last_show = shows_collection.find_one(sort=[("id_show", -1)])
    new_id = last_show["id_show"] + 1 if last_show else 1

    fecha_creacion = datetime.now().strftime("%d-%m-%Y")


    new_show = {
        "id_show": new_id,
        "user_id": show_data.userId,
        "presenter_name": show_data.presenterName,
        "voice": show_data.voice.dict(),  
        "id_avatar": show_data.avatar,
        "id_graphics": show_data.graphics,
        "texto": show_data.texto,
        "id_background": show_data.background,
        "url_show": show_data.url_show,
        "fecha_creacion": fecha_creacion
    }

    # Insertar en la colección
    shows_collection.insert_one(new_show)

    return {"message": f"Show guardado correctamente con ID: {new_id}"}



def get_avatars():
   
    avatars = avatars_collection.find()


    combined_avatars = []

    for avatar in avatars:
        id_avatar = avatar.get("id_avatar")
        video_shot = avatar_video_shot_collection.find_one({"id_avatar": id_avatar})
        
        if video_shot:
            combined_avatar = {
                "nombre": avatar.get("nombre"),
                "genero": avatar.get("genero"),
                "id_avatar": id_avatar,
                "url_img": video_shot.get("url_img"),
                "url_json": video_shot.get("url_json"),
                "url_video": video_shot.get("url_video")
            }
            combined_avatars.append(combined_avatar)

    return combined_avatars


def get_shows(user_id):
    print(user_id)
    shows = list(shows_collection.find({"user_id": user_id}))
    
    for show in shows:
        show["_id"] = str(show["_id"])

        # Obtener url_background desde background_collection
        try:
            background_id = ObjectId(show["id_background"])
            background = background_collection.find_one({"_id": background_id})
            show["url_background"] = background.get("url_background") if background else None
        except Exception as e:
            print(f"Error con id_background: {e}")
            show["url_background"] = None

        # Obtener url_img del avatar desde avatar_video_shot_collection
        avatar = avatar_video_shot_collection.find_one({"id_avatar": show["id_avatar"]})
        show["url_img_avatar"] = avatar.get("url_img") if avatar else None

    return shows
