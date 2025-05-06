@echo off
:: Upgrade pip and install packages in order
pip install --upgrade pip setuptools wheel
pip install Flask==2.3.2 flask-cors==4.0.0 python-dotenv==1.0.0 gunicorn==20.1.0 requests==2.31.0
pip install numpy==1.26.4 protobuf==4.25.7 onnxruntime==1.17.1 --prefer-binary
pip install soundfile==0.12.1 pydub==0.25.1 --prefer-binary
pip install faster-whisper==0.9.0
pip install google-cloud-speech==2.21.0 google-cloud-translate==2.0.1
pip install nltk==3.8.1 langdetect==1.0.9 gTTS==2.3.2
pip install elevenlabs==0.2.27 openai==0.27.8

echo All packages installed successfully!
pause



:: To run this file 1. create virtual environment python -m venv venv
:: 2. Activate the virtual environment source venv/bin/activate
:: 3. run this command ./install_dependencies.bat