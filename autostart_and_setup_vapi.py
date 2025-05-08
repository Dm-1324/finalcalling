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

# Configure headers for VAPI API
headers = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Update VAPI Assistant server URL
print("🔄 Updating VAPI Assistant server URL...")
body = {
    "server": {
        "url": f"{public_url.rstrip('/')}/vapi-webhook"
    }
}

response = requests.patch(
    f"https://api.vapi.ai/assistant/{ASSISTANT_ID}",
    headers=headers,
    json=body
)

if response.status_code == 200:
    updated_data = response.json()
    if updated_data.get('server', {}).get('url') == f"{public_url.rstrip('/')}/vapi-webhook":
        print(f"✅ Webhook updated successfully: {updated_data['server']['url']}")
        
        # Verify the update
        verify_response = requests.get(
            f"https://api.vapi.ai/assistant/{ASSISTANT_ID}",
            headers=headers
        )
        print("Current assistant config:", verify_response.json())
    else:
        print("❌ Webhook URL not updated as expected")
        print(f"Response: {updated_data}")
elif response.status_code == 404:
    print("❌ Assistant not found. Double-check the ASSISTANT_ID.")
    print(response.text)
else:
    print(f"❌ Failed to update webhook (HTTP {response.status_code}): {response.text}")

print("🚀 All systems running. Press Ctrl+C to stop.")

# Keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Stopping...")
    app_process.terminate()
    ngrok_process.terminate()