import requests
import os

VAPI_API_KEY = os.getenv("VAPI_API_KEY")

headers = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json",
}

assistant_payload = {
    "name": "My Custom AI Agent",
    "voice": {
        "provider": "elevenlabs",
        "voice_id": "your-voice-id",
    },
    "tools": [
        {"type": "stt", "endpoint": "https://your-ngrok-url/stt", "override": True},
        {"type": "tts", "endpoint": "https://your-ngrok-url/tts", "override": True},
        {"type": "llm", "endpoint": "https://your-ngrok-url/generate", "override": True},
    ],
    "model": "gpt-3.5-turbo",
}

response = requests.post(
    "https://api.vapi.ai/assistants", headers=headers, json=assistant_payload
)

print(response.json())
