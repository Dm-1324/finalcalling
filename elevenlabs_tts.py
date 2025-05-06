import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

FALLBACK_VOICES = {
    'en': 'bajNon13EdhNMndG3z05',
    'hi': 'Zp1aWhL05Pi5BkhizFC3',
    'te': 'ktIdXisRrub2VKRszryF'
}

def validate_text(text, language):
    if not text.strip():
        raise ValueError("Empty text provided")
    
    if language == 'hi':
        if not any('\u0900' <= c <= '\u097F' for c in text):
            logger.warning("Hindi text validation failed.")
    elif language == 'te':
        if not any('\u0C00' <= c <= '\u0C7F' for c in text):
            logger.warning("Telugu text validation failed.")

def get_voice_id(language):
    language = language.lower()[:2]
    
    env_var_mapping = {
        'en': 'ENGLISH_VOICE_ID',
        'hi': 'HINDI_VOICE_ID',
        'te': 'TELUGU_VOICE_ID'
    }
    
    env_var_name = env_var_mapping.get(language)
    if env_var_name:
        voice_id = os.getenv(env_var_name)
    else:
        voice_id = None

    # fallback to default hardcoded if not found
    voice_id = voice_id or FALLBACK_VOICES.get(language)
    
    if not voice_id:
        raise ValueError(f"No voice available for {language}")
    
    logger.info(f"Using voice ID: {voice_id[:4]}... for {language}")
    return voice_id

def generate_speech(text, language, output_path="response.mp3"):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        logger.info(f"Generating {language} speech...")
        validate_text(text, language)
        voice_id = get_voice_id(language)

        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.7,
                    "similarity_boost": 0.8,
                    "speed": 0.95 if language == 'hi' else 1.0
                }
            },
            timeout=int(os.getenv("TTS_TIMEOUT", 30))
        )
        
        if response.status_code != 200:
            try:
                error_msg = response.json().get('detail', {}).get('message') or response.text
            except Exception:
                error_msg = response.text
            logger.error(f"TTS API Error {response.status_code}: {error_msg}")
            return False

        with open(output_path, "wb") as f:
            f.write(response.content)
        
        logger.info(f"Generated {os.path.getsize(output_path)} bytes to {output_path}")
        return True

    except Exception as e:
        logger.error(f"TTS failed: {str(e)}", exc_info=True)
        return False
