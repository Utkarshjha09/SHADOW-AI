# SHADOW Voice Assistant

A bilingual AI voice assistant supporting English and Hindi with wake word detection, web interface, and mobile app.

## Features

- 🎤 Voice recognition with wake word support (Hey Shadow, Sunn Shadow)
- 🗣️ High-quality Hindi text-to-speech using Google TTS
- 🌐 Web interface with two microphone modes (Normal/Standard)
- 💬 Bilingual chat (English/Hindi/Hinglish)
- 📱 Mobile app (Flutter)
- 🤖 AI integration (Ollama) with fallback responses

## Quick Start

### Step 1: Prerequisites

Ensure you have:
- **Python 3.8+** (Python 3.13 recommended)
- **Git** installed
- **Microphone** (for voice input)
- **Internet connection** (for Google TTS)

### Step 2: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/SHADOW.git
cd SHADOW
```

### Step 3: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you encounter PyAudio installation errors on Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

### Step 5: Run SHADOW

**Option A - Web Interface (Recommended):**
```bash
# Windows
start_voice_web.bat

# Linux/Mac
python src/web/api_server.py
```
Then open: http://localhost:8000/voice

**Option B - Desktop Voice Assistant:**
```bash
python run_enhanced_voice.py
```

**Option C - Hindi Voice Demo:**
```bash
python demo_hindi_voice.py
```

## Web Interface Guide

The web interface offers two microphone modes:

### Normal Mode (Default)
- ✅ Auto-start listening when page loads
- ✅ No wake word needed
- ✅ Best for active use
- Click "Stop Listening" to pause

### Standard Mode
- ✅ Background listening
- ✅ Requires wake word to activate
- ✅ Best for hands-free operation
- Say wake word to start conversation

**Access Settings:** Click the gear icon (⚙️) in the top-right corner

## Wake Words

**English:** "Hey Shadow", "Hi Shadow", "Hello Shadow", "Ok Shadow"

**Hindi:** "Sunn Shadow", "Suno Shadow", "Bol Shadow", "Kya Shadow"

**Hinglish:** Works with both languages mixed

## Deployment to Render (Free)

### Step 1: Push to GitHub

```bash
# If not already done
git remote add origin https://github.com/YOUR_USERNAME/SHADOW.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 3: Deploy Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your **SHADOW** repository
3. Configure:
   - **Name:** shadow-voice-assistant
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python src/web/api_server.py`
   - **Plan:** Free
4. Click **"Create Web Service"**

### Step 4: Access Your App

Once deployed (2-3 minutes), visit:
```
https://shadow-voice-assistant.onrender.com/voice
```

**Note:** Free tier on Render:
- ✅ Web interface works
- ✅ Voice recognition works
- ✅ Hindi TTS works
- ⚠️ Ollama AI not available (uses fallback responses)
- ⚠️ App sleeps after 15 minutes of inactivity

For full AI features, see [DEPLOYMENT.md](DEPLOYMENT.md)

## Environment Variables (Optional)

For Render deployment, add these environment variables:

```bash
HOST=0.0.0.0
PORT=10000
DEBUG=False
OLLAMA_HOST=http://localhost:11434
```

## Project Structure

```
SHADOW/
├── src/
│   ├── ai_backends/          # Ollama AI integration
│   ├── voice/                # Speech engines
│   │   ├── hindi_speech.py   # Hindi TTS/STT
│   │   ├── speech_engine.py  # Main speech engine
│   │   └── wake_words.py     # Wake word detection
│   ├── web/                  # Flask web server
│   │   ├── api_server.py     # Main API server
│   │   └── templates/        # HTML templates
│   └── utils/                # Utilities
├── mobile_app/               # Flutter mobile app
├── config/                   # Configuration files
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── Procfile                  # Deployment config
└── runtime.txt               # Python version
```

## Requirements

### System Requirements
- Python 3.8+ (3.13 recommended)
- 4GB RAM minimum
- Microphone for voice input
- Internet connection

### Python Packages
See [requirements.txt](requirements.txt) for full list:
- **Core:** Flask, PyYAML, Requests
- **Speech:** SpeechRecognition, pyttsx3, PyAudio, gTTS
- **AI:** OpenAI, Torch, Whisper
- **Hindi:** indic-transliteration, googletrans, langdetect
- **Utils:** fuzzywuzzy, python-levenshtein

## Troubleshooting

### PyAudio Installation Error (Windows)
```bash
pip install pipwin
pipwin install pyaudio
```

### Microphone Not Working
- Check browser permissions (Chrome/Edge recommended)
- Enable microphone access in Windows Settings
- Use HTTPS or localhost (required for Web Speech API)

### Hindi TTS Not Working
- Check internet connection (gTTS requires online)
- Verify `gtts` package is installed
- Server endpoint `/api/tts/hindi` should be accessible

### Ollama Connection Error
- Install Ollama: https://ollama.com/download
- Run: `ollama serve`
- Pull model: `ollama pull phi3:mini`
- Or use fallback responses (automatic)

## Testing

```bash
# Test voice assistant
python test_enhanced_voice.py

# Test Hindi speech
python test_hindi_speech.py

# Test web API
python test_voice_api.py
```

## Development

### Run in Debug Mode
```bash
python src/web/api_server.py
```

### Modify Wake Words
Edit `src/voice/wake_words.py`:
```python
WAKE_WORDS = [
    "hey shadow",
    "your custom wake word",
]
```

### Add New Language
1. Update `detect_language()` in `src/voice/wake_words.py`
2. Add TTS support in `src/voice/hindi_speech.py`
3. Update web interface language detection

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
- Review troubleshooting section above

## Acknowledgments

- Google Text-to-Speech for Hindi TTS
- Ollama for local AI inference
- Web Speech API for browser voice recognition
- Flutter team for mobile framework
