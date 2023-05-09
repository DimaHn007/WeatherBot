import requests
import json

def translation_city(city):
    url = 'https://translation-api.translate.com/translate/v1/mt'

    headers = {
    'x-api-key': '16426d5d15a33f',
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        'text': city,
        'source_language': 'uk',
        'translation_language': 'en'
    }

    response = requests.post(url, headers=headers, data=payload)
    translated_text = json.loads(response.content.decode())['translation']
    return translated_text