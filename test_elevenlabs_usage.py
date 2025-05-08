import os
import logging
from elevenlabs_tts import generate_speech, get_voice_id  # Uses your existing code
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_tts_call(language="hi", test_text="नमस्ते, आप कैसे हैं?", test_output="test_output.mp3"):
    print(f"\n🧪 Testing ElevenLabs TTS for language: {language}")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not set in .env")
        return

    try:
        voice_id = get_voice_id(language)
        print(f"✅ Using Voice ID: {voice_id}")
    except Exception as e:
        print(f"❌ Failed to get voice ID: {str(e)}")
        return

    success = generate_speech(test_text, language, output_path=test_output)

    if success and os.path.exists(test_output):
        size_kb = round(os.path.getsize(test_output) / 1024, 2)
        print(f"✅ Speech generation successful. File saved: {test_output} ({size_kb} KB)")
    else:
        print("❌ Speech generation failed.")

if __name__ == "__main__":
    # You can call this with different languages
    test_tts_call("en", "Hello! This is a test message.")
    test_tts_call("hi", "नमस्ते! यह एक परीक्षण संदेश है।")
    test_tts_call("te", "హలో! ఇది ఒక పరీక్షా సందేశం.")
