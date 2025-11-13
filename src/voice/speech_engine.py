# src/voice/speech_engine.py
import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import os
import winsound  # For Windows beep sound

class SpeechEngine:
    def __init__(self, config=None):
        self.config = config or {}
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Speech queue for handling concurrent requests
        self.speech_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        
        # Calibrate microphone for ambient noise
        self.calibrate_microphone()
        
        # Current language setting
        self.current_language = 'en'
    
    def setup_tts(self):
        """Configure text-to-speech settings."""
        voices = self.tts_engine.getProperty('voices')
        
        # Try to set a male voice for SHADOW
        for voice in voices:
            if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 165)  # Speed of speech (increased for responsiveness)
        self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
    
    def play_wakeup_sound(self):
        """Play a pleasant wake-up beep sound."""
        try:
            # Play two-tone beep: higher pitch then lower pitch
            winsound.Beep(1000, 100)  # 1000 Hz for 100ms
            time.sleep(0.05)
            winsound.Beep(800, 150)   # 800 Hz for 150ms
        except Exception as e:
            print(f"Could not play wake-up sound: {e}")
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        print("Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Microphone calibrated.")
    
    def listen_for_speech(self, timeout=5, phrase_timeout=3, language='en-IN'):
        """
        Listen for speech input and return transcribed text.
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_timeout: Maximum time for a phrase
            language: Language code for recognition (en-IN supports English & Hindi)
        """
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                # Adjust for ambient noise briefly
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_timeout)
                
            print("⚙️ Processing speech...")
            # Try to recognize speech using Google's service with language support
            # en-IN supports both English and Hindi
            text = self.recognizer.recognize_google(audio, language=language)
            print(f"✅ You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected within timeout period.")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"❌ Error with speech recognition service: {e}")
            return None
    
    def speak(self, text, priority=False, language='en'):
        """
        Add text to speech queue or speak immediately if priority.
        
        Args:
            text: Text to speak
            priority: If True, speak immediately
            language: 'en' for English, 'hi' for Hindi
        """
        if priority:
            self._speak_now(text, language)
        else:
            self.speech_queue.put((text, language))
    
    def _speak_now(self, text, language='en'):
        """
        Immediately speak the given text.
        
        Args:
            text: Text to speak
            language: 'en' for English, 'hi' for Hindi
        """
        print(f"💬 SHADOW ({language.upper()}): {text}")
        
        # Adjust voice properties for Hindi if needed
        if language == 'hi':
            # Slightly slower for Hindi
            self.tts_engine.setProperty('rate', 150)
        else:
            # Normal speed for English
            self.tts_engine.setProperty('rate', 165)
        
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def _speech_worker(self):
        """Worker thread to handle speech queue."""
        while True:
            try:
                item = self.speech_queue.get(timeout=1)
                if isinstance(item, tuple):
                    text, language = item
                else:
                    text, language = item, 'en'
                self._speak_now(text, language)
                self.speech_queue.task_done()
            except queue.Empty:
                continue
    
    def wait_for_speech_completion(self):
        """Wait for all queued speech to complete."""
        self.speech_queue.join()
    
    def stop(self):
        """Stop the speech engine."""
        self.tts_engine.stop()
