import subprocess
import re
import time

# 1. Start Flask server
flask_process = subprocess.Popen(["python", "app.py"])
print("✅ Started app.py")

# Wait a few seconds for server to be ready
time.sleep(3)

# 2. Start localtunnel
print("🌐 Starting LocalTunnel...")
tunnel_process = subprocess.Popen(
    ["npx.cmd", "localtunnel", "--port", "5000", "--subdomain", "loclabot"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
)


public_url = None
for line in iter(tunnel_process.stdout.readline, ""):
    print(line.strip())

    match = re.search(r"https://[a-z0-9]+\.loca\.lt", line)
    if match:
        public_url = match.group(0)
        break

if public_url:
    print(f"\n🚀 Public URL: {public_url}")
    print("\n🔗 Now update this URL in your Vapi assistant config!")
else:
    print("❌ Failed to get localtunnel URL")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping processes...")
    flask_process.terminate()
    tunnel_process.terminate()
