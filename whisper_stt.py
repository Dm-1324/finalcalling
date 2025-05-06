import os
import logging
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

def transcribe_with_confidence(file_path):
    try:
        logger.debug(f"Starting Whisper processing: {file_path}")
        
        # Create models directory if not exists
        os.makedirs("./models", exist_ok=True)
        
        model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8",
            download_root="./models"
        )
        
        # Add explicit audio file check
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
            
        segments, info = model.transcribe(file_path, beam_size=5)
        transcript = " ".join([segment.text for segment in segments])
        return transcript, info.language
        
    except Exception as e:
        logger.error(f"Whisper error: {str(e)}")
        raise