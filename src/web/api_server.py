"""
Web API server for SHADOW Voice Assistant
Provides REST endpoints for web and mobile clients
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import tempfile
import base64
from werkzeug.utils import secure_filename

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_backends.ollama_backend import OllamaAI
from utils.language_utils import detect_language, get_greeting, get_error_message
from voice.wake_words import is_wake_word, DEFAULT_WAKE_WORDS
from memory.conversation_memory import ConversationMemory
from voice.hindi_speech import HindiSpeechEngine

app = Flask(__name__)
CORS(app)

# Initialize components
ollama_ai = OllamaAI()
memory = ConversationMemory()
WAKE_WORDS = DEFAULT_WAKE_WORDS
hindi_engine = HindiSpeechEngine()  # Initialize Hindi speech engine

# OpenAI client removed - using local speech recognition instead
openai_client = None

# Simple detector: questions about who built/created the assistant
def is_creator_question(text: str) -> bool:
    if not text:
        return False
    t = text.strip().lower()
    triggers = [
        # English
        'who created you', 'who made you', 'who built you', 'your creator', 'who is your creator',
        'who developed you', 'who is developer', 'who is the developer',
        # Hindi (roman)
        'kisne banaya', 'kisne tumhe banaya', 'tumhe kisne banaya', 'tumhe kisne banayaa', 'kisne tumko banaya',
        'kisne banaya hai', 'kisne develop kiya', 'kisne banaya tha',
        # Hindi (devanagari)
        'किसने बनाया', 'तुम्हें किसने बनाया', 'तुमको किसने बनाया', 'किसने बनाया है', 'किसने डेवलप किया'
    ]
    return any(p in t for p in triggers)

def creator_answer(lang: str) -> str:
    return (
        'It is created by Utkarsh Jha.' if lang != 'hi' else 'इसे उत्कर्ष झा द्वारा बनाया गया है।'
    )

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ollama_status = ollama_ai.is_available()
    return jsonify({
        'status': 'ok',
        'ollama_available': ollama_status,
        'services': {
            'web_api': True,
            'ollama': ollama_status,
            'memory': True
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Text chat endpoint"""
    try:
        data = request.json
        message = data.get('message', '')
        language = data.get('language', 'auto')
        
        if not message:
            return jsonify({'success': False, 'error': 'No message provided'})
        
        # Auto-detect language if not specified
        if language == 'auto':
            language = detect_language(message)
        
        # Shortcut: creator question override
        if is_creator_question(message):
            answer = creator_answer(language if language != 'auto' else detect_language(message))
            memory.add_message('user', message)
            memory.add_message('assistant', answer)
            return jsonify({ 'success': True, 'response': answer, 'language': detect_language(message) })

        # Store user message
        memory.add_message('user', message)
        
        # Get response from Ollama (with fallback if not available)
        if ollama_ai.is_available():
            response = ollama_ai.get_response(message, language)
        else:
            # Fallback responses when Ollama is not running
            response = get_fallback_response(message, language)
        
        # Store assistant response
        memory.add_message('assistant', response)
        
        return jsonify({
            'success': True,
            'response': response,
            'language': language,
            'detected_language': detect_language(message)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_fallback_response(message, language):
    """Generate fallback response when Ollama is not available"""
    msg_lower = message.lower()
    
    # Common greetings
    greetings = ['hello', 'hi', 'hey', 'नमस्ते', 'हैलो', 'हाय', 'kaise ho', 'kaisa hai']
    if any(g in msg_lower for g in greetings):
        if language == 'hi':
            return "नमस्ते! मैं SHADOW हूँ, आपका AI सहायक। मैं आपकी कैसे मदद कर सकता हूँ?"
        else:
            return "Hello! I'm SHADOW, your AI assistant. How can I help you?"
    
    # Time questions
    if any(w in msg_lower for w in ['time', 'samay', 'समय', 'kitne baje']):
        from datetime import datetime
        now = datetime.now()
        if language == 'hi':
            return f"अभी समय है {now.strftime('%I:%M %p')} बजे।"
        else:
            return f"The current time is {now.strftime('%I:%M %p')}."
    
    # Date questions
    if any(w in msg_lower for w in ['date', 'today', 'aaj', 'आज', 'tarikh', 'तारीख']):
        from datetime import datetime
        now = datetime.now()
        if language == 'hi':
            return f"आज की तारीख है {now.strftime('%d %B %Y')}।"
        else:
            return f"Today's date is {now.strftime('%B %d, %Y')}."
    
    # Name questions
    if any(w in msg_lower for w in ['your name', 'naam', 'नाम', 'who are you', 'kaun ho']):
        if language == 'hi':
            return "मेरा नाम SHADOW है। मैं आपका व्यक्तिगत AI सहायक हूँ।"
        else:
            return "My name is SHADOW. I'm your personal AI assistant."
    
    # Help questions
    if any(w in msg_lower for w in ['help', 'madad', 'मदद', 'what can you do', 'kya kar sakte']):
        if language == 'hi':
            return "मैं आपसे बात कर सकता हूँ, सवालों के जवाब दे सकता हूँ, और आपकी मदद कर सकता हूँ। बेहतर जवाब के लिए Ollama शुरू करें।"
        else:
            return "I can chat with you, answer questions, and help you. For better responses, please start Ollama."
    
    # Default response
    if language == 'hi':
        return f"मैं समझ गया। लेकिन विस्तृत जवाब के लिए मुझे Ollama AI की जरूरत है। अभी मैं बुनियादी सवालों का जवाब दे सकता हूँ - जैसे समय, तारीख, अभिवादन आदि।"
    else:
        return f"I understand. However, for detailed responses, I need Ollama AI. Currently, I can answer basic questions like time, date, greetings, etc."

@app.route('/api/voice', methods=['POST'])
def voice():
    """Voice input endpoint
    Expects multipart/form-data with 'audio' file (webm/ogg/wav) and optional 'language'.
    Uses local speech recognition instead of OpenAI.
    """
    audio_path = None
    wav_path = None
    try:
        print(f"[VOICE] Received request - Content-Type: {request.content_type}")
        print(f"[VOICE] Form data keys: {list(request.form.keys())}")
        print(f"[VOICE] Files keys: {list(request.files.keys())}")
        
        if 'audio' not in request.files:
            print("[VOICE] ERROR: No audio file in request")
            return jsonify({'success': False, 'error': 'No audio file provided'}), 200

        audio_file = request.files['audio']
        language = request.form.get('language', 'auto')
        
        print(f"[VOICE] Audio file info - Name: {audio_file.filename}, Size: {len(audio_file.read())} bytes")
        audio_file.seek(0)  # Reset file pointer after reading size

        if len(audio_file.read()) == 0:
            print("[VOICE] ERROR: Audio file is empty")
            return jsonify({'success': False, 'error': 'Audio file is empty'}), 200
        
        audio_file.seek(0)  # Reset file pointer again

        temp_dir = tempfile.gettempdir()
        filename = secure_filename(audio_file.filename or 'audio.webm')
        audio_path = os.path.join(temp_dir, filename)
        
        print(f"[VOICE] Saving audio to: {audio_path}")
        audio_file.save(audio_path)
        
        # Verify file was saved correctly
        if not os.path.exists(audio_path):
            print(f"[VOICE] ERROR: Failed to save audio file to {audio_path}")
            return jsonify({'success': False, 'error': 'Failed to save audio file'}), 200
            
        file_size = os.path.getsize(audio_path)
        print(f"[VOICE] Saved file size: {file_size} bytes")

        transcript = ""
        wav_path = None
        errors = []
        # Pre-check ffmpeg in PATH for clearer diagnostics (for pydub path)
        ffmpeg_ok = any(
            os.path.exists(os.path.join(p, 'ffmpeg.exe')) for p in os.getenv('PATH', '').split(os.pathsep)
        ) if os.name == 'nt' else any(
            os.path.exists(os.path.join(p, 'ffmpeg')) for p in os.getenv('PATH', '').split(os.pathsep)
        )
        print(f"[VOICE] ffmpeg on PATH: {ffmpeg_ok}")

        print(f"[VOICE] Processing audio file: {filename}, language: {language}")

        # Helper: try Whisper first (best support for WebM)
        def try_whisper(first_choice: bool = False):
            nonlocal transcript, language
            try:
                import whisper
                print(f"[VOICE] Trying local Whisper{' (priority)' if first_choice else ''}...")
                model = whisper.load_model("base")
                # Force CPU-friendly settings if no GPU
                kwargs = { 'fp16': False }
                if language in ('hi', 'en'):
                    result = model.transcribe(audio_path, language=language, **kwargs)
                else:
                    result = model.transcribe(audio_path, **kwargs)
                transcript_local = (result.get("text") or "").strip()
                detected_lang = result.get("language", language)
                if transcript_local:
                    transcript = transcript_local
                    print(f"[VOICE] Whisper success: '{transcript}' (detected: {detected_lang})")
                    if language == 'auto' and detected_lang:
                        language = 'hi' if detected_lang in ['hi', 'hindi'] else 'en'
                else:
                    errors.append("Whisper returned empty transcript")
            except ImportError:
                print("[VOICE] Whisper not installed")
                errors.append("Whisper not installed")
            except Exception as e:
                print(f"[VOICE] Whisper error: {e}")
                errors.append(f"Whisper error: {e}")

        # Prefer Whisper first for compressed formats
        ext = os.path.splitext(audio_path)[1].lower()
        compressed_exts = {'.webm', '.ogg', '.mp3', '.m4a', '.mp4'}
        if ext in compressed_exts:
            try_whisper(first_choice=True)

        # If Whisper didn't work, try SpeechRecognition with WAV conversion
        if not transcript:
            try:
                import speech_recognition as sr
                r = sr.Recognizer()

                audio_file_path = None
                try:
                    import pydub
                    print("[VOICE] Converting audio to WAV format via pydub/ffmpeg...")
                    audio_seg = pydub.AudioSegment.from_file(audio_path)
                    wav_path = audio_path.replace(ext, '.wav')
                    audio_seg.export(wav_path, format='wav')
                    audio_file_path = wav_path
                    print(f"[VOICE] Converted to WAV: {wav_path}")
                except Exception as conv_err:
                    extra = " (ffmpeg missing?)" if not ffmpeg_ok else ""
                    msg = f"WAV conversion failed: {conv_err}{extra}"
                    print(f"[VOICE] {msg}")
                    errors.append(msg)

                if audio_file_path:
                    with sr.AudioFile(audio_file_path) as source:
                        print("[VOICE] Reading WAV for SpeechRecognition...")
                        r.adjust_for_ambient_noise(source, duration=0.4)
                        audio_data = r.record(source)

                    # Try Google first
                    try:
                        print("[VOICE] Trying Google Web Speech API...")
                        lang_code = 'hi-IN' if language == 'hi' else 'en-US'
                        transcript = r.recognize_google(audio_data, language=lang_code)
                        print(f"[VOICE] Google success: '{transcript}'")
                    except Exception as e:
                        errors.append(f"Google STT: {e}")
                        print(f"[VOICE] Google STT error: {e}")

                    # Try Sphinx last
                    if not transcript:
                        try:
                            print("[VOICE] Trying offline Sphinx...")
                            transcript = r.recognize_sphinx(audio_data)
                            print(f"[VOICE] Sphinx success: '{transcript}'")
                        except Exception as e:
                            errors.append(f"Sphinx: {e}")
                            print(f"[VOICE] Sphinx error: {e}")
            except ImportError:
                msg = 'SpeechRecognition not installed. Run: pip install SpeechRecognition'
                print(f"[VOICE] {msg}")
                errors.append(msg)
            except Exception as e:
                errors.append(f"SpeechRecognition pipeline error: {e}")
                print(f"[VOICE] SpeechRecognition pipeline error: {e}")

        # If still nothing, try Whisper again as a final attempt (maybe ext wasn't in list)
        if not transcript:
            try_whisper(first_choice=False)

        if not transcript or not transcript.strip():
            print("[VOICE] ERROR: No transcript generated from any method")
            error_msg = 'Could not transcribe audio. '
            if file_size < 1000:
                error_msg += 'Audio file seems too short. '
            # Add most relevant troubleshooting hint
            hint = 'Make sure ffmpeg is installed and the terminal was restarted.'
            error_msg += f'Please speak clearly and ensure microphone is working. {hint}'
            return jsonify({'success': False, 'error': error_msg, 'details': {
                'filename': filename,
                'size_bytes': file_size,
                'ext': ext,
                'attempt_errors': errors
            }}), 200

        print(f"[VOICE] Final transcript: '{transcript}'")

        # Detect wake word presence in recognized text (for client UX)
        wake_hit = is_wake_word(transcript)
        print(f"[VOICE] Wake word detected: {wake_hit}")

        # Auto-detect language from transcript if requested
        if language == 'auto':
            language = detect_language(transcript)
            print(f"[VOICE] Language detected: {language}")

        # If user asked who created you, short-circuit
        if is_creator_question(transcript):
            response_text = creator_answer(language)
            result = {
                'success': True,
                'transcript': transcript,
                'response': response_text,
                'language': language,
                'wake_word_detected': wake_hit
            }
            print(f"[VOICE] Creator Q detected, short answer returned")
            return jsonify(result)

        # Query Ollama for a response
        print(f"[VOICE] Querying Ollama for response...")
        response_text = ollama_ai.get_response(transcript, language)
        print(f"[VOICE] Ollama response length: {len(response_text)} chars")

        result = {
            'success': True,
            'transcript': transcript,
            'response': response_text,
            'language': language,
            'wake_word_detected': wake_hit
        }
        print(f"[VOICE] Returning successful response")
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        # Clean up temp files
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception:
            pass
        try:
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
        except Exception:
            pass

@app.route('/api/test-voice', methods=['POST'])
def test_voice():
    """Test endpoint for voice debugging"""
    try:
        print(f"[TEST] Content-Type: {request.content_type}")
        print(f"[TEST] Form keys: {list(request.form.keys())}")
        print(f"[TEST] Files keys: {list(request.files.keys())}")
        
        if 'audio' in request.files:
            audio_file = request.files['audio']
            print(f"[TEST] Audio filename: {audio_file.filename}")
            print(f"[TEST] Audio content type: {audio_file.content_type}")
            content = audio_file.read()
            print(f"[TEST] Audio size: {len(content)} bytes")
            print(f"[TEST] First 20 bytes: {content[:20]}")
            
        return jsonify({
            'success': True,
            'message': 'Test endpoint working',
            'received_files': list(request.files.keys()),
            'received_form': dict(request.form)
        })
        
    except Exception as e:
        print(f"[TEST] Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/wake-word', methods=['POST'])
def check_wake_word():
    """Check if text contains wake word"""
    try:
        data = request.json
        text = data.get('text', '')
        is_wake = is_wake_word(text)

        return jsonify({
            'success': True,
            'is_wake_word': is_wake,
            'text': text
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    """Get conversation history"""
    try:
        history = memory.get_recent_messages(10)  # Get last 10 messages
        return jsonify({
            'success': True,
            'messages': history
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conversation', methods=['DELETE'])
def clear_conversation():
    """Clear conversation history"""
    try:
        memory.clear()
        return jsonify({
            'success': True,
            'message': 'Conversation cleared'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get assistant configuration"""
    return jsonify({
        'success': True,
        'config': {
            'name': 'SHADOW',
            'supported_languages': ['en', 'hi'],
            'wake_words': WAKE_WORDS,
            'features': {
                'voice_input': True,
                'text_input': True,
                'multilingual': True,
                'wake_word_detection': True,
                'hindi_tts': True
            }
        }
    })

@app.route('/api/tts/hindi', methods=['POST'])
def hindi_tts():
    """Generate Hindi speech audio using gTTS"""
    try:
        data = request.json
        text = data.get('text', '')
        language = data.get('language', 'hi')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'})
        
        print(f"[HINDI TTS] Generating audio for: {text} (lang: {language})")
        
        # Generate speech using gTTS
        from gtts import gTTS
        import base64
        
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.close()
        tts.save(temp_file.name)
        
        # Read and encode as base64
        with open(temp_file.name, 'rb') as f:
            audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Cleanup
        os.unlink(temp_file.name)
        
        return jsonify({
            'success': True,
            'audio': audio_base64,
            'format': 'mp3',
            'language': language
        })
        
    except Exception as e:
        print(f"[HINDI TTS] Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/voice')
def voice_interface():
    """Serve enhanced voice interface"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    return send_from_directory(template_dir, 'voice_enhanced.html')

# Serve React app in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React app for production"""
    react_build_dir = os.path.join(os.path.dirname(__file__), 'react-app', 'dist')
    
    if path != "" and os.path.exists(os.path.join(react_build_dir, path)):
        return send_from_directory(react_build_dir, path)
    else:
        return send_from_directory(react_build_dir, 'index.html')

if __name__ == '__main__':
    print("Starting SHADOW Web API Server...")
    print("React app will be available at: http://localhost:8000")
    print("API endpoints available at: http://localhost:8000/api/")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )
