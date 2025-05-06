import subprocess
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not VAPI_API_KEY or not ASSISTANT_ID:
    print("❌ Please set VAPI_API_KEY and ASSISTANT_ID in your .env file.")
    exit(1)

# Start Flask app
print("✅ Starting app.py...")
app_process = subprocess.Popen(["python", "app.py"])

# Wait for Flask to start
time.sleep(3)

# Start ngrok
print("🌐 Starting ngrok tunnel...")
ngrok_process = subprocess.Popen(["ngrok", "http", "5000"])

# Wait for ngrok to initialize
time.sleep(5)

# Fetch ngrok public URL
try:
    resp = requests.get("http://localhost:4040/api/tunnels")
    tunnels = resp.json().get("tunnels", [])
    public_url = next(t["public_url"] for t in tunnels if t["proto"] == "https")

    print(f"✅ ngrok URL: {public_url}")
except Exception as e:
    print(f"❌ Failed to get ngrok URL: {e}")
    app_process.terminate()
    ngrok_process.terminate()
    exit(1)

# Fetch assistant details
print("📡 Fetching assistant details...")
headers = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}

assistant_resp = requests.get(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=headers)

if assistant_resp.status_code == 200:
    assistant_data = assistant_resp.json()
    print(f"🤖 Using Assistant: {assistant_data.get('name')} (ID: {ASSISTANT_ID})")
else:
    print("❌ Failed to fetch assistant info. Please check the ASSISTANT_ID.")
    print(assistant_resp.text)
    app_process.terminate()
    ngrok_process.terminate()
    exit(1)

# Update Vapi Assistant server URL
print("🔄 Updating Vapi Assistant server URL...")
body = {
    "serverUrl": f"{public_url}/vapi-webhook"
}

response = requests.patch(
    f"https://api.vapi.ai/assistant/{ASSISTANT_ID}",
    headers=headers,
    json=body
)

if response.status_code == 200:
    print(f"✅ Webhook updated successfully: {public_url}/vapi-webhook")
elif response.status_code == 404:
    print("❌ Assistant not found. Double-check the ASSISTANT_ID.")
    print(response.text)
else:
    print(f"❌ Failed to update webhook: {response.text}")

print("🚀 All systems running. Press Ctrl+C to stop.")

# Keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Stopping...")
    app_process.terminate()
    ngrok_process.terminate()
