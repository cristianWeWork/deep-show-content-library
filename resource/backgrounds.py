from dotenv import load_dotenv
import database.nonSqlDatabase as mongoDb
import resource.blob_functions as blobf
import database.database as db
from datetime import datetime
fecha_actual = datetime.now()
fecha_formateada = fecha_actual.strftime("%Y-%m-%d")
load_dotenv()


def uploadBackgrounds(file):
    url_background = blobf.upload_background(file, file.filename)
    print(url_background)
    data = {
        "url_background": url_background
    }

    id = mongoDb.insert_background(data)

    return str(id)


def getBackgrounds():
    backgrounds = mongoDb.getBackgrounds()
    return backgrounds


def uploadThemes(name, audioFile, imageFile):
    preview_filename = f"{fecha_formateada}_preview_{imageFile.filename}"
    url_preview = blobf.upload_background(imageFile, preview_filename)
    audio_filename = f"{fecha_formateada}_audio_{audioFile.filename}"
    url_sound = blobf.upload_background(audioFile, audio_filename)
    data = {
        "music_url": url_sound,
        "preview": url_preview,
        "name": name
    }
    mongoDb.add_theme(name, url_preview, url_sound)


def uploadGraphics(id, introGraphic, endGraphic, lowerThirdGraphic, transitionGraphic):
    intro_filename = f"{id}_intro_{introGraphic.filename}"
    url_intro = blobf.upload_background(introGraphic, intro_filename)
    mongoDb.add_graphics(id, url_intro, 'intro')

    end_filename = f"{id}_end_{endGraphic.filename}"
    url_end = blobf.upload_background(endGraphic, end_filename)
    mongoDb.add_graphics(id, url_end, 'end')

    lower_third_filename = f"{id}_lower_third_{lowerThirdGraphic.filename}"
    url_lt = blobf.upload_background(lowerThirdGraphic, lower_third_filename)
    mongoDb.add_graphics(id, url_lt, 'lower_third')

    transition_filename = f"{id}_transition_{transitionGraphic.filename}"
    url_transition = blobf.upload_background(
        transitionGraphic, transition_filename)
    mongoDb.add_graphics(id, url_transition, 'url_transition')


def uploadAvatars(name, jsonFile, gender, webmFile, imageFile):
    intro_json = f"{name}_jsonFile_{jsonFile.filename}"
    url_json = blobf.upload_background(jsonFile, intro_json)

    intro_webmFile = f"{name}_webmFile_{webmFile.filename}"
    url_webm = blobf.upload_background(webmFile, intro_webmFile)

    intro_imageFile = f"{name}_imageFile_{imageFile.filename}"
    url_image = blobf.upload_background(imageFile, intro_imageFile)

    result = mongoDb.add_avatars(name, url_image, url_json, url_webm, gender)
    return result


def uploadFile(name, file):
    intro_json = f"{name}_file_{file.filename}"
    url_json = blobf.upload_background(file, intro_json)
    return url_json
