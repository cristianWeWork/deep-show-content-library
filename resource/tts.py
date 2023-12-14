
import os
from dotenv import load_dotenv
import requests


load_dotenv()
speechKey = os.getenv('SPEECHKEY')


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

