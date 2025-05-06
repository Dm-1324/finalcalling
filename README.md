# Final Calling - Technical Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Component Documentation](#component-documentation)
   - [Flask Web Server (app.py)](#flask-web-server-apppy)
   - [Speech-to-Text Services](#speech-to-text-services)
   - [Text-to-Speech Services](#text-to-speech-services)
   - [Conversational AI](#conversational-ai)
   - [Vapi Integration](#vapi-integration)
4. [API Documentation](#api-documentation)
5. [Language Support](#language-support)
6. [Environment Variables](#environment-variables)
7. [Deployment Guide](#deployment-guide)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)
10. [Performance Optimization](#performance-optimization)
11. [Future Improvements](#future-improvements)

## System Overview

Final Calling is a multilingual voice assistant system designed for handling voice interactions through multiple channels including web interfaces and phone calls. The system integrates multiple AI services to provide:

- Speech-to-text conversion with language detection
- Conversational AI responses
- High-quality text-to-speech synthesis
- Voice call handling through Vapi.ai integration

The system is designed with redundancy in mind, featuring fallback mechanisms for each major component to ensure service reliability.

## Architecture

The application follows a modular architecture with the following high-level components:

```
┌───────────────────────────────────────────────────────────────┐
│                         Client Requests                       │
└───────────────────┬───────────────────────────┬───────────────┘
                    │                           │
┌───────────────────▼───────┐       ┌───────────▼───────────────┐
│    Direct API Access      │       │    Vapi.ai Integration    │
└───────────────────┬───────┘       └───────────┬───────────────┘
                    │                           │
┌───────────────────▼───────────────────────────▼───────────────┐
│                      Flask Web Server                         │
├───────────────────┬───────────────────┬───────────────────────┤
│   Speech-to-Text  │  Conversational   │     Text-to-Speech    │
│      Services     │        AI         │       Services        │
└───────────────────┴───────────────────┴───────────────────────┘
```

Each component is designed to function independently with well-defined interfaces, allowing for easy replacement or upgrading of individual services.

## Component Documentation

### Flask Web Server (app.py)

The Flask application serves as the main entry point and API gateway for all functionality. It handles:

- HTTP request routing
- Service orchestration
- Error handling and logging
- Audio file management

**Key Features:**
- Cross-Origin Resource Sharing (CORS) support
- Health check endpoint
- Temporary file management for audio processing
- Dynamic service selection based on available API keys

**Initialization Process:**
1. Load environment variables
2. Initialize Flask application with CORS
3. Setup logging
4. Create necessary directories (e.g., audio_outputs)

### Speech-to-Text Services

Multiple STT implementations are available to ensure reliability and quality:

#### AssemblyAI STT (assemblyai_stt.py)

Primary cloud-based speech recognition service with excellent language detection capabilities.

**Key Features:**
- High-accuracy transcription
- Automatic language detection
- Script verification for Hindi and Telugu

**Process Flow:**
1. Upload audio file to AssemblyAI API
2. Request transcription with language detection
3. Poll for results with timeout handling
4. Additional language verification based on script detection
5. Return transcript with detected language code

#### Whisper STT (whisper_stt.py)

Local speech recognition using OpenAI's Whisper model as a fallback option.

**Key Features:**
- Offline capabilities
- Multi-language support
- Model download and caching

**Process Flow:**
1. Load or download Whisper model
2. Process audio file with appropriate parameters
3. Extract transcript and language information
4. Return results with error handling

#### Google STT (stt_google.py)

Alternative speech recognition using Google Cloud services.

**Key Features:**
- High-quality speech recognition
- Multiple language support with fallbacks
- Audio preprocessing for optimal results

**Process Flow:**
1. Prepare audio (convert to 16kHz mono WAV)
2. Try English recognition with Hindi fallback
3. Verify language using script detection
4. Re-transcribe with focused language if needed
5. Return transcript with detected language

### Text-to-Speech Services

#### ElevenLabs TTS (elevenlabs_tts.py)

Primary TTS service providing high-quality, natural-sounding voice synthesis.

**Key Features:**
- Multiple voice options for each supported language
- Voice customization settings
- Dynamic voice selection based on language

**Process Flow:**
1. Validate input text and language
2. Select appropriate voice ID based on language
3. Call ElevenLabs API with customized parameters
4. Save audio response to file
5. Return success status

#### gTTS Fallback

Google Text-to-Speech is used as a fallback when ElevenLabs is not configured.

**Key Features:**
- Broad language support
- No API key required
- Simple integration

### Conversational AI

#### OpenAI Chat (openai_chat.py)

Leverages OpenAI's GPT models to generate conversational responses.

**Key Features:**
- Context-aware responses through message history
- Model selection through environment variables
- Language-specific error handling

**Process Flow:**
1. Format conversation history for OpenAI API
2. Call OpenAI ChatCompletion API
3. Extract and return response content
4. Handle errors with appropriate language-based fallbacks

### Vapi Integration

#### Auto-start and Setup (autostart_and_setup_vapi.py)

Automates the process of setting up and connecting to Vapi.ai for voice calls.

**Key Features:**
- Flask server auto-start
- ngrok tunnel configuration
- Vapi assistant webhook URL update

**Process Flow:**
1. Start Flask application in background
2. Initialize ngrok tunnel
3. Fetch ngrok public URL
4. Update Vapi assistant configuration with webhook URL
5. Keep processes running until interrupted

## API Documentation

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok"
}
```

### Speech-to-Text

**Endpoint:** `POST /stt`

**Request:**
- Content-Type: `multipart/form-data`
- Body: `audio` - Audio file (WAV, MP3, etc.)

**Response:**
```json
{
  "text": "Transcribed text content",
  "language": "en",
  "status": "success"
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

### Text-to-Speech

**Endpoint:** `POST /tts`

**Request:**
- Content-Type: `application/json`
- Body:
  ```json
  {
    "text": "Text to convert to speech",
    "language": "en"
  }
  ```

**Response:**
```json
{
  "audio_url": "https://your-domain.com/audio/filename.mp3",
  "status": "success"
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

### AI Response Generation

**Endpoint:** `POST /generate`

**Request:**
- Content-Type: `application/json`
- Body:
  ```json
  {
    "messages": [
      {"role": "user", "content": "Hello, how are you?"},
      {"role": "assistant", "content": "I'm doing well, thank you!"},
      {"role": "user", "content": "What's the weather like today?"}
    ]
  }
  ```

**Response:**
```json
{
  "response": "I don't have real-time weather information, but I can help you find weather forecasts if you tell me your location.",
  "status": "success"
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

### Vapi Webhook

**Endpoint:** `POST /vapi-webhook`

**Request:**
- Content-Type: `application/json`
- Body: (Vapi.ai webhook payload)
  ```json
  {
    "transcript": "User message from call",
    "language": "en"
  }
  ```

**Response:**
```json
{
  "text": "AI response text",
  "audioUrl": "https://your-domain.com/audio/response.mp3"
}
```

**Error Response:**
```json
{
  "text": "Oops! Something went wrong.",
  "audioUrl": null
}
```

### Serve Audio

**Endpoint:** `GET /audio/<filename>`

**Response:**
- Audio file with MIME type `audio/mpeg`

## Language Support

The system is designed to support multiple languages with special focus on:

### English
- Default language
- Used for fallback when other languages cannot be determined

### Hindi
- Identified by Devanagari script detection (`\u0900-\u097F`)
- Dedicated ElevenLabs voice ID
- Language-specific error messages

### Telugu
- Identified by Telugu script detection (`\u0C00-\u0C7F`)
- Dedicated ElevenLabs voice ID
- Language-specific error messages

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ELEVENLABS_API_KEY` | API key for ElevenLabs TTS | None | For ElevenLabs TTS |
| `HINDI_VOICE_ID` | ElevenLabs voice ID for Hindi | Zp1aWhL05Pi5BkhizFC3 | No |
| `TELUGU_VOICE_ID` | ElevenLabs voice ID for Telugu | ktIdXisRrub2VKRszryF | No |
| `ENGLISH_VOICE_ID` | ElevenLabs voice ID for English | bajNon13EdhNMndG3z05 | No |
| `OPENAI_API_KEY` | API key for OpenAI services | None | Yes |
| `OPENAI_MODEL` | OpenAI model to use | gpt-4 | No |
| `ASSEMBLYAI_API_KEY` | API key for AssemblyAI STT | None | For AssemblyAI STT |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google Cloud credentials | google_creds.json | For Google STT |
| `VAPI_API_KEY` | API key for Vapi.ai | None | For Vapi integration |
| `ASSISTANT_ID` | Vapi assistant ID | None | For Vapi integration |
| `PORT` | Port for Flask server | 5000 | No |
| `HOSTED_URL` | URL where service is hosted | request.host_url | For production |
| `FLASK_ENV` | Flask environment | production | No |
| `TTS_TIMEOUT` | Timeout for TTS API calls | 30 | No |

## Deployment Guide

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file with required variables.

3. Run the Flask server:
   ```bash
   python app.py
   ```
   
4. For Vapi integration with local tunnel:
   ```bash
   python autostart_and_setup_vapi.py
   ```

### Production Deployment

#### Railway

The application is configured for deployment on Railway with the following steps:

1. Connect your GitHub repository to Railway
2. Set all required environment variables in Railway dashboard
3. Set `HOSTED_URL` to your Railway app URL
4. Deploy the application

#### Custom Server

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables
4. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```

## Troubleshooting

### Common Issues

#### Speech Recognition Failures

**Symptoms:**
- Empty or incorrect transcriptions
- Language detection issues

**Solutions:**
1. Check audio quality and format
2. Verify API keys for speech services
3. Check logs for specific error messages
4. Try alternative STT service by setting/unsetting API keys

#### Text-to-Speech Failures

**Symptoms:**
- Missing audio files
- Error messages from TTS services

**Solutions:**
1. Verify ElevenLabs API key
2. Check voice ID configurations
3. Ensure `audio_outputs` directory is writable
4. Verify text is not empty or invalid

#### Vapi Integration Issues

**Symptoms:**
- Assistant not responding to calls
- Webhook errors

**Solutions:**
1. Check ngrok is running and accessible
2. Verify Vapi API key and assistant ID
3. Ensure webhook URL is correctly configured
4. Check Flask server is running and accessible

### Logging

The application uses Python's built-in logging module. Log level is set to `INFO` by default, which can be adjusted in `app.py`.

Important log messages include:
- STT and TTS service usage and outcomes
- API errors with service providers
- Webhook request handling
- File management operations

## Security Considerations

### API Key Management

- All API keys are stored in environment variables
- Keys are never exposed in responses
- `.gitignore` is configured to prevent accidental key commits

### File Management

- Temporary files are created with proper permissions
- Audio files are cleaned up after processing
- Output directory is created with appropriate permissions

### Input Validation

- All API endpoints validate input parameters
- Audio files are processed in a controlled manner
- JSON payloads are validated before processing

## Performance Optimization

### Speech-to-Text

- Whisper model is loaded once and reused
- AssemblyAI is preferred for cloud-based processing
- Audio files are processed as streams when possible

### Text-to-Speech

- Generated audio files are named based on content hash
- Audio files are served directly from disk
- Voice IDs are cached for efficient reuse

### Conversational AI

- OpenAI model is configurable for cost/performance balance
- Response tokens are limited to manage API costs
- Error handling includes appropriate fallbacks

## Future Improvements

### Technical Enhancements

1. **Caching System**
   - Implement Redis for response caching
   - Cache frequent TTS outputs

2. **Database Integration**
   - Store conversation history
   - Track user preferences and language settings

3. **Authentication**
   - Add API key authentication
   - Implement user account system

4. **Monitoring**
   - Add Prometheus metrics
   - Set up alerting for service failures

### Feature Additions

1. **Additional Languages**
   - Expand beyond current language support
   - Add language-specific conversation handlers

2. **Voice Customization**
   - Allow user-selected voices
   - Implement voice cloning for personalization

3. **Extended Conversation Capabilities**
   - Add knowledge base integration
   - Implement specialized domains (banking, healthcare, etc.)

4. **Analytics**
   - Call duration and quality metrics
   - User satisfaction tracking
   - Performance analytics dashboard
