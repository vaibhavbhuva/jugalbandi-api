import json
import base64
import os
import requests
from pydub import AudioSegment
from google.cloud import texttospeech, speech, translate
from urllib.parse import urlparse

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_encoded_string(url):
    if is_url(url):
        local_filename = "local_file.mp3"
        with requests.get(url) as r:
            with open(local_filename, 'wb') as f:
                f.write(r.content)
    else:
        local_filename = url

    given_audio = AudioSegment.from_file(local_filename)
    given_audio = given_audio.set_frame_rate(16000)
    given_audio = given_audio.set_channels(1)
    given_audio.export("temp.wav", format="wav", codec="pcm_s16le")
    with open("temp.wav", "rb") as wav_file:
        wav_file_content = wav_file.read()
    encoded_string = base64.b64encode(wav_file_content)
    encoded_string = str(encoded_string, 'ascii', 'ignore')
    os.remove(local_filename)
    os.remove("temp.wav")
    return encoded_string, wav_file_content

def google_speech_to_text(wav_file_content, input_language):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=wav_file_content)
    language_code = input_language + "-IN"
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
    )
    response = client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript

def speech_to_text(encoded_string, input_language):
    data = {"config": {"language": {"sourceLanguage": f"{input_language}"},
                       "transcriptionFormat": {"value": "transcript"},
                       "audioFormat": "wav",
                       "samplingRate": "16000",
                       "postProcessors": None
                       },
            "audio": [{"audioContent": encoded_string}]
            }
    api_url = "https://asr-api.ai4bharat.org/asr/v1/recognize/" + input_language
    response = requests.post(api_url, data=json.dumps(data))
    text = json.loads(response.text)["output"][0]["source"]
    return text

def google_translate_text(text, source, destination, project_id="indian-legal-bert"):
    client = translate.TranslationServiceClient()
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": source,
            "target_language_code": destination,
        }
    )
    return response.translations[0].translated_text

def indic_translation(text, source, destination):
    try:
        data = {
            "source_language": source,
            "target_language": destination,
            "text": text
        }
        api_url = "https://nmt-api.ai4bharat.org/translate_sentence"
        response = requests.post(api_url, data=json.dumps(data), timeout=60)
        indic_text = json.loads(response.text)
    except:
        indic_text = google_translate_text(text, source, destination)
    return indic_text['text']

def google_text_to_speech(text, language):
    try:
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )
        audio_content = response.audio_content
    except:
        audio_content = None
    return audio_content

def text_to_speech(language, text, gender='female'):
    try:
        api_url = "https://tts-api.ai4bharat.org/"
        payload = {"input": [{"source": text}], "config": {"gender": gender, "language": {"sourceLanguage": language}}}
        response = requests.post(api_url, json=payload, timeout=60)
        audio_content = response.json()['audio'][0]['audioContent']
        audio_content = base64.b64decode(audio_content)
    except:
        audio_content = google_text_to_speech(text, language)
    return audio_content

def audio_input_to_text(audio_file, input_language):
    encoded_string, wav_file_content = get_encoded_string(audio_file)
    try:
        indic_text = google_speech_to_text(wav_file_content, input_language)
    except:
        indic_text = speech_to_text(encoded_string, input_language)
    return indic_text
