from google.cloud import speech
from google.cloud import translate_v2 as translate
import io
from pydub import AudioSegment
import re

def is_hindi(text):
    """Check for Hindi characters (Unicode range \u0900-\u097F)"""
    return bool(re.search(r'[\u0900-\u097F]', text))

def prepare_audio(input_path):
    """Convert any audio to 16kHz mono WAV"""
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    prepared_path = "prepared.wav"
    audio.export(prepared_path, format="wav")
    return prepared_path

def transcribe_audio(file_path):
    client = speech.SpeechClient.from_service_account_file('google_creds.json')
    prepared_path = prepare_audio(file_path)
    
    with io.open(prepared_path, "rb") as f:
        content = f.read()

    # PHASE 1: Try English with Hindi fallback
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        alternative_language_codes=["hi-IN"],
        enable_automatic_punctuation=True,
        model="latest_long"
    )
    
    response = client.recognize(config=config, audio={"content": content})
    
    if response.results:
        transcript = " ".join(r.alternatives[0].transcript for r in response.results)
        
        # PHASE 2: Language verification
        if is_hindi(transcript):
            # Re-transcribe with Hindi focus if we detect Hindi chars
            config.language_code = "hi-IN"
            config.alternative_language_codes = []
            response = client.recognize(config=config, audio={"content": content})
            if response.results:
                return " ".join(r.alternatives[0].transcript for r in response.results), "hi"
        
        return transcript, "en"
    
    # PHASE 3: Fallback to Hindi-only if English fails
    config.language_code = "hi-IN"
    config.alternative_language_codes = []
    response = client.recognize(config=config, audio={"content": content})
    if response.results:
        transcript = " ".join(r.alternatives[0].transcript for r in response.results)
        return transcript, "hi"
    
    return "", "en"  # Ultimate fallback