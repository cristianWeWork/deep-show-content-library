
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

load_dotenv()
speechKey = os.getenv('SPEECHKEY')

date = datetime.datetime.now()

def getVoicesList():
    requestUrl = "https://westeurope.tts.speech.microsoft.com/cognitiveservices/voices/list"
    headers = {
        'Ocp-Apim-Subscription-Key': speechKey,
        'Content-type': 'application/json',

    }
    request: object = requests.get(requestUrl,  headers=headers)

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
    requestUrl = "https://westeurope.tts.speech.microsoft.com/cognitiveservices/voices/list"
    headers = {
        'Ocp-Apim-Subscription-Key': speechKey,
        'Content-type': 'application/json',

    }
    request: object = requests.get(requestUrl,  headers=headers)
    
    if request.status_code == 200:
        response_data = request.json()
        resultados = [
            objeto for objeto in response_data if nationality in objeto["LocaleName"]]
        return resultados
    else:
        print("La solicitud no fue exitosa. Código de estado:", request.status_code)
        return []

async def getAudioText(text: str, voice: str, language: str, format: str ):
    aos = AudioOutputStream(None)
    speech_config = speechsdk.SpeechConfig(
        subscription=speechKey, region="westeurope")
    print(format)
    if format == "mp3":
        file_name = "outputaudio.mp3"
    elif format == "ogg":
        file_name = "outputaudio.ogg"
    else:
        file_name = "outputaudio.wav"
    
    file_config = speechsdk.audio.AudioOutputConfig(
        filename=file_name)  # type: ignore
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=file_config)
    speech_config.speech_synthesis_voice_name = voice
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=file_config)
    ssml = ssmlCreator(text, voice)
    blendShapes = []
    visemes = []
    def viseme_cb(evt):
        # print("Viseme event received: audio offset: {}ms, viseme id: {}.".format(
        #     evt.audio_offset / 10000, evt.viseme_id))
        nonlocal blendShapes, visemes
        visemes.append({"audio_offsett": evt.audio_offset /
                       10000, "viseme_id": evt.viseme_id})
        blendShapes.append(evt.animation)

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
        "created_at": date
    }
    
    id = mongoDb.insert_document(data)
    
    url_audio =  blobf.upload_File(file_name, "{}.{}".format(id, format))
    
    mongoDb.update_url_audio({"_id" : id}, {"url_audio": url_audio})
    
    return url_audio,  str(id)


def ssmlCreator(text: str, voiceL: str):
    return """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="es-ES">
            <voice name="{}">
               <mstts:viseme type="FacialExpression"/>
               {}
            </voice>
                </speak>""".format(voiceL, text)
