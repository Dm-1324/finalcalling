import os
import requests
from dotenv import load_dotenv
import time
import logging

load_dotenv()
logger = logging.getLogger(__name__)

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
BASE_URL = "https://api.assemblyai.com/v2"

def is_devanagari(char):
    return '\u0900' <= char <= '\u097F'

def is_telugu(char):
    return '\u0C00' <= char <= '\u0C7F'

def transcribe_audio(file_path):
    try:
        # Upload file
        with open(file_path, 'rb') as f:
            upload_response = requests.post(
                f"{BASE_URL}/upload",
                headers={"authorization": ASSEMBLYAI_API_KEY},
                files={"file": f}
            )
            upload_url = upload_response.json()['upload_url']

        # Start transcription (auto language detection)
        transcript_response = requests.post(
            f"{BASE_URL}/transcript",
            headers={"authorization": ASSEMBLYAI_API_KEY},
            json={"audio_url": upload_url, "language_detection": True}
        )
        transcript_id = transcript_response.json()['id']

        # Poll for results
        for _ in range(30):
            result_response = requests.get(
                f"{BASE_URL}/transcript/{transcript_id}",
                headers={"authorization": ASSEMBLYAI_API_KEY}
            )
            result = result_response.json()
            
            if result['status'] == 'completed':
                transcript = result['text']
                lang_code = result['language_code']
                
                # Adjust for mixed language
                if 'en' in lang_code.lower():
                    if any(is_devanagari(c) for c in transcript):
                        lang_code = 'hi'
                    elif any(is_telugu(c) for c in transcript):
                        lang_code = 'te'
                
                return transcript, lang_code
            elif result['status'] == 'error':
                raise RuntimeError(result.get('error', 'Transcription failed'))
            
            time.sleep(2)

        raise TimeoutError("Transcription timeout")
    
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise