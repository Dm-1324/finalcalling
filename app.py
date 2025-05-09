from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
import logging
from dotenv import load_dotenv
import nltk


nltk.download('punkt', quiet=True) 
# Initialize
load_dotenv()
app = Flask(__name__)
CORS(app)  # Allow CORS for all routes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Health Check Endpoint ---
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# --- Speech-to-Text Endpoint ---
# In app.py, modify the stt() function:
@app.route('/stt', methods=['POST'])
def stt():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    try:
        # Create a temp file with explicit permissions
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'audio_input.wav')
        
        audio_file = request.files['audio']
        audio_file.save(temp_path)
        
        if os.getenv("ASSEMBLYAI_API_KEY"):
            from assemblyai_stt import transcribe_audio
            transcript, lang = transcribe_audio(temp_path)
        else:
            from whisper_stt import transcribe_with_confidence
            transcript, lang = transcribe_with_confidence(temp_path)
            
        # Clean up
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        return jsonify({
            "text": transcript,
            "language": lang,
            "status": "success"
        })

    except Exception as e:
        logger.error(f"STT failed: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- Text-to-Speech Endpoint ---
# In app.py, modify the tts() function:
@app.route('/tts', methods=['POST'])
def tts():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing text"}), 400

    try:
        text = data['text']
        lang = data.get('language', 'en')
        output_file = f"tts_{hash(text)}.mp3"
        output_path = os.path.join("audio_outputs", output_file)
        
        # Ensure directory exists
        os.makedirs("audio_outputs", exist_ok=True)

        if os.getenv("ELEVENLABS_API_KEY"):
            from elevenlabs_tts import generate_speech
            success = generate_speech(text, lang, output_path)
            if not success:
                raise Exception("TTS generation failed")
        else:
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang)
            tts.save(output_path)

        return jsonify({
            "audio_url": f"{os.getenv('HOSTED_URL', request.host_url)}/audio/{output_file}",
            "status": "success"
        })

    except Exception as e:
        logger.error(f"TTS failed: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- AI Response Endpoint ---
# In app.py, modify the generate() function:
@app.route('/generate', methods=['POST'])
def generate():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({"error": "Missing messages"}), 400

    try:
        from openai_chat import get_ai_response
        if not isinstance(data['messages'], list):
            raise ValueError("Messages must be a list")
            
        response = get_ai_response(data['messages'])
        return jsonify({
            "response": response,
            "status": "success"
        })

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- Serve Audio Files ---
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    try:
        return send_from_directory(
            os.path.abspath('audio_outputs'),
            filename,
            mimetype='audio/mpeg',
            as_attachment=False
        )
    except Exception as e:
        logger.error(f"Audio serve failed: {str(e)}")
        return jsonify({"error": "File not found"}), 404

# --- VAPI Webhook Endpoint ---
# ... [keep all previous code until the vapi-webhook endpoint] ...

@app.route('/vapi-webhook', methods=['POST'])
def vapi_webhook():
    try:
        logger.info("🔥 VAPI WEBHOOK TRIGGERED 🔥")
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        logger.info(f"📦 Received payload type: {data.get('message', {}).get('type')}")
        
        # Handle different message types
        message_type = data.get('message', {}).get('type')
        
        if message_type == 'conversation-update':
            conversation = data['message'].get('conversation', [])
            last_user_msg = next((m for m in reversed(conversation) if m.get('role') == 'user'), None)
            
            if last_user_msg:
                user_text = last_user_msg.get('content', '')
                logger.info(f"💬 Processing user message: {user_text}")
                
                # Generate response
                from openai_chat import get_ai_response
                ai_text = get_ai_response([{"role": "user", "content": user_text}])
                
                # Generate audio
                output_file = f"tts_{hash(ai_text)}.mp3"
                output_path = os.path.join("audio_outputs", output_file)
                os.makedirs("audio_outputs", exist_ok=True)
                
                if os.getenv("ELEVENLABS_API_KEY"):
                    from elevenlabs_tts import generate_speech
                    if not generate_speech(ai_text, 'en', output_path):
                        raise Exception("TTS generation failed")
                
                return jsonify({
                    "type": "audio",
                    "message": ai_text,
                    "audioUrl": f"{os.getenv('HOSTED_URL', request.host_url)}audio/{output_file}"
                })
        
        # For status updates or other message types
        return jsonify({"status": "handled"})

    except Exception as e:
        logger.error(f"❌ Webhook error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500





if __name__ == '__main__':
    os.makedirs("audio_outputs", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
