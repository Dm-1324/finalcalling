#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Start Flask app in background
echo "Starting Flask app..."
flask run --host=0.0.0.0 --port=5000 &

# Wait for Flask to start
sleep 3

# Start LocalTunnel with subdomain
echo "Starting LocalTunnel at https://mybot.loca.lt"
lt --port 5000 --subdomain mybot
