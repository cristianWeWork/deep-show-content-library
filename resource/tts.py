import base64
import json
import os
from typing import Any
from dotenv import load_dotenv
import requests
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech.audio import AudioOutputConfig, AudioOutputStream
from dotenv import load_dotenv
import datetime
import database.nonSqlDatabase as mongoDb
import resource.blob_functions as blobf

load_dotenv()

load_dotenv()
speechKey = os.getenv("SPEECHKEY")
elevenKey = os.getenv("ELEVENKEY")
date = datetime.datetime.now()


def getVoicesList():
    requestUrl = (
        "https://westeurope.tts.speech.microsoft.com/cognitiveservices/voices/list"
    )
    headers = {
        "Ocp-Apim-Subscription-Key": speechKey,
        "Content-type": "application/json",
    }
    request: object = requests.get(requestUrl, headers=headers)

    if request.status_code == 200:
        response_data = request.json()
        locale_names = [item["LocaleName"] for item in response_data]

        # Imprimir el array resultante
        list_set = set(locale_names)
        result_list = list(list_set)
        result = sorted(result_list)
        return result
    else:
        print("La solicitud no fue exitosa. Código de estado:", request.status_code)


def getVoiceOptions(nationality: str):
    requestUrl = (
        "https://westeurope.tts.speech.microsoft.com/cognitiveservices/voices/list"
    )
    headers = {
        "Ocp-Apim-Subscription-Key": speechKey,
        "Content-type": "application/json",
    }
    request: object = requests.get(requestUrl, headers=headers)

    if request.status_code == 200:
        response_data = request.json()
        resultados = [
            objeto for objeto in response_data if nationality in objeto["LocaleName"]
        ]
        return resultados
    else:
        print("La solicitud no fue exitosa. Código de estado:", request.status_code)
        return []


def getVoiceOptionsEleven():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": elevenKey}

    response = requests.get(url, headers=headers)
    voices_data = response.json()

    # Lista para almacenar los resultados procesados
    filtered_voices = []

    # Procesar cada voz y extraer solo los datos necesarios
    for voice in voices_data["voices"]:
        filtered_voice = {
            "voice_id": voice["voice_id"],
            "name": voice["name"],
            "age": voice["labels"].get(
                "age", "Unknown"
            ),  # Utiliza 'Unknown' si 'age' no está disponible
            "accent": voice["labels"].get(
                "accent", "Unknown"
            ),  # Utiliza 'Unknown' si 'accent' no está disponible
            "gender": voice["labels"].get(
                "gender", "Unknown"
            ),  # Utiliza 'Unknown' si 'gender' no está disponible
            "preview_url": voice.get(
                "preview_url", ""
            ),  # Devuelve cadena vacía si 'preview_url' no está disponible
        }
        filtered_voices.append(filtered_voice)

    return filtered_voices


async def getAudioText(text: str, voice: str, language: str, format: str):
    provider = "Azure"
    aos = AudioOutputStream(None)
    speech_config = speechsdk.SpeechConfig(subscription=speechKey, region="westeurope")
    print("paso 5")
    if format == "mp3":
        file_name = "outputaudio.mp3"
    elif format == "ogg":
        file_name = "outputaudio.ogg"
    else:
        file_name = "outputaudio.wav"

    file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)  # type: ignore
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=file_config
    )
    speech_config.speech_synthesis_voice_name = voice
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=file_config
    )
    ssml = ssmlCreator(text, voice)
    blendShapes = []
    visemes = []

    def viseme_cb(evt):
        # print("Viseme event received: audio offset: {}ms, viseme id: {}.".format(
        #     evt.audio_offset / 10000, evt.viseme_id))
        nonlocal blendShapes, visemes
        visemes.append(
            {"audio_offsett": evt.audio_offset / 10000, "viseme_id": evt.viseme_id}
        )
        blendShapes.append(evt.animation)
        print("paso 6")

    speech_synthesizer.viseme_received.connect(viseme_cb)
    result = speech_synthesizer.speak_ssml_async(ssml).get()
    data = {
        "voz": voice,
        "text": text,
        "idioma": language,
        "format": format,
        "url_audio": "",
        "blendShapes": blendShapes,
        "visemes": visemes,
        "created_at": date,
        "provider": provider,
    }
    print("paso 7")
    print(data)
    id = mongoDb.insert_document(data)
    print(id)
    url_audio = blobf.upload_File(file_name, "{}.{}".format(id, format))
    print(url_audio)
    mongoDb.update_url_audio({"_id": id}, {"url_audio": url_audio})

    return url_audio, str(id), visemes, blendShapes, provider


def ssmlCreator(text: str, voiceL: str):
    return """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="es-ES">
            <voice name="{}">
               <mstts:viseme type="FacialExpression"/>
               {}
            </voice>
                </speak>""".format(
        voiceL, text
    )


async def getAudioTextEleven(text, voice_id, voiceSettings, format, name, eleven_model):
    provider = "ElevenLab"
    # Establecer el URL con el voice_id correcto
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"

    # Configuración del encabezado con la API key adecuada
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenKey,
    }

    # Datos para la solicitud
    data = {"text": text, "model_id": eleven_model, "voice_settings": voiceSettings}

    # Determinar el nombre del archivo basado en el formato deseado
    file_name = f"outputaudio.{format}"

    # Realizar la petición POST
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        json_string = response.content.decode("utf-8")
        response_dict = json.loads(json_string)
        audio_bytes = base64.b64decode(response_dict["audio_base64"])
        with open(file_name, "wb") as f:
            f.write(audio_bytes)
    else:
        print(f"Error: {response.status_code}")
        return None

    # Aquí agregamos el manejo de base de datos y almacenamiento, ejemplo con MongoDB y Azure Blob Storage
    print("Guardando en la base de datos y almacenamiento en la nube...")
    created_at = datetime.datetime.now()

    # Parseito que parseo Visemas -> estandarizacion Azure
    visemes = convert_eleven_labs_to_azure(response_dict["alignment"])

    # Suponemos una función para guardar en MongoDB
    document_id = mongoDb.insert_document(
        {
            "voice_id": voice_id,
            "voz": name,
            "text": text,
            "idioma": "es",
            "format": format,
            "url_audio": "",
            "created_at": created_at,
            "provider": provider,
            "visemes": visemes,
        }
    )

    # Suponemos una función para subir el archivo a Blob Storage
    url_audio = blobf.upload_File(file_name, f"{document_id}.{format}")

    # Actualizar la base de datos con la URL del audio
    mongoDb.update_url_audio({"_id": document_id}, {"url_audio": url_audio})

    return url_audio, str(document_id), visemes, provider


def convert_eleven_labs_to_azure(eleven_labs_data):
    characters = eleven_labs_data["characters"]
    character_start_times_seconds = eleven_labs_data["character_start_times_seconds"]
    character_end_times_seconds = eleven_labs_data["character_end_times_seconds"]

    visemes = [
        {"audio_offset": start_time * 1000, "char": char}  # Convertir a milisegundos
        for char, start_time in zip(characters, character_start_times_seconds)
    ]

    return visemes
