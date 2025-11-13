# SHADOW Voice Assistant

A bilingual AI voice assistant supporting English and Hindi with wake word detection, web interface, and mobile app.

## Features

- Voice recognition with wake word support (Hey Shadow, Sunn Shadow)
- High-quality Hindi text-to-speech using Google TTS
- Web interface with two microphone modes
- Bilingual chat (English/Hindi/Hinglish)
- Mobile app (Flutter)
- Ollama AI integration

## Installation

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

**Desktop Voice Assistant:**
```bash
python run_enhanced_voice.py
```

**Web Interface:**
```bash
start_voice_web.bat
# Open http://localhost:8000/voice
```

**Hindi Voice Demo:**
```bash
python demo_hindi_voice.py
```

## Web Interface

The web interface offers two modes:

- **Normal Mode**: Auto-start listening when page opens (no wake word needed)
- **Standard Mode**: Background listening with wake word activation

Access settings via the gear icon to switch modes and configure wake sound.

## Wake Words

English: "Hey Shadow", "Hi Shadow", "Hello Shadow", "Ok Shadow"

Hindi: "Sunn Shadow", "Suno Shadow", "Bol Shadow", "Kya Shadow"

## Project Structure

```
SHADOW/
├── src/
│   ├── ai_backends/      # AI integration
│   ├── voice/            # Speech engine
│   ├── web/              # Web server
│   └── utils/            # Utilities
├── mobile_app/           # Flutter app
├── config/               # Config files
└── tests/                # Tests
```

## Requirements

- Python 3.8+
- Microphone
- Internet (for Google TTS)

## Development

Run tests:
```bash
python test_enhanced_voice.py
python test_hindi_speech.py
```

## License

MIT
