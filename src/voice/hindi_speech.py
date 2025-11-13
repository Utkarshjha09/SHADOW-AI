"""
Enhanced Hindi Speech Recognition and Synthesis Module
Provides better Hindi language support for SHADOW
"""
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
import os
import tempfile
import platform
from pathlib import Path

class HindiSpeechEngine:
    """Enhanced speech engine with proper Hindi support"""
    
    def __init__(self):
        """Initialize Hindi speech engine"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize TTS engines
        self.pyttsx3_engine = pyttsx3.init()
        self.setup_pyttsx3_hindi()
        
        # Adjust recognition settings for better Hindi
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def setup_pyttsx3_hindi(self):
        """Setup pyttsx3 for Hindi (if Hindi voice available)"""
        try:
            voices = self.pyttsx3_engine.getProperty('voices')
            
            # Look for Hindi voice
            hindi_voice = None
            for voice in voices:
                # Check for Hindi voice (Microsoft Hemant, Microsoft Heera, etc.)
                if 'hindi' in voice.name.lower() or 'hemant' in voice.name.lower() or 'heera' in voice.name.lower():
                    hindi_voice = voice.id
                    break
            
            if hindi_voice:
                self.pyttsx3_engine.setProperty('voice', hindi_voice)
                print(f"✅ Hindi voice found: {hindi_voice}")
            else:
                print("⚠️ No dedicated Hindi voice found, using default")
            
            # Set speech rate for Hindi (slower for better clarity)
            self.pyttsx3_engine.setProperty('rate', 140)
            self.pyttsx3_engine.setProperty('volume', 0.9)
            
        except Exception as e:
            print(f"⚠️ Error setting up Hindi voice: {e}")
    
    def recognize_hindi(self, timeout=5, phrase_time_limit=10):
        """
        Recognize Hindi speech using Google Speech Recognition
        
        Args:
            timeout (int): Seconds to wait for speech to start
            phrase_time_limit (int): Maximum seconds for phrase
            
        Returns:
            tuple: (success, text, language)
        """
        try:
            with self.microphone as source:
                print("🎤 सुन रहा हूँ... (Listening for Hindi...)")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Try Hindi recognition first
            try:
                print("🔍 Hindi में पहचान रहा हूँ... (Recognizing in Hindi...)")
                text = self.recognizer.recognize_google(
                    audio, 
                    language='hi-IN'  # Hindi (India)
                )
                print(f"✅ Hindi में सुना: {text}")
                return (True, text, 'hi')
                
            except sr.UnknownValueError:
                # If Hindi fails, try English
                print("🔍 English में कोशिश कर रहा हूँ... (Trying English...)")
                text = self.recognizer.recognize_google(
                    audio, 
                    language='en-IN'  # English (India) - better for Hinglish
                )
                print(f"✅ English में सुना: {text}")
                return (True, text, 'en')
                
        except sr.WaitTimeoutError:
            print("⏱️ कोई आवाज़ नहीं सुनी (No speech detected)")
            return (False, "", "")
        except sr.UnknownValueError:
            print("❌ समझ नहीं आया (Could not understand)")
            return (False, "", "")
        except sr.RequestError as e:
            print(f"❌ सेवा में त्रुटि (Service error): {e}")
            return (False, "", "")
        except Exception as e:
            print(f"❌ अज्ञात त्रुटि (Unknown error): {e}")
            return (False, "", "")
    
    def recognize_bilingual(self, timeout=5, phrase_time_limit=10):
        """
        Recognize speech in both Hindi and English (Hinglish support)
        
        Args:
            timeout (int): Seconds to wait for speech to start
            phrase_time_limit (int): Maximum seconds for phrase
            
        Returns:
            tuple: (success, text, language)
        """
        try:
            with self.microphone as source:
                print("🎤 Listening... (Hindi/English)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Try with en-IN first (best for Hinglish)
            try:
                text = self.recognizer.recognize_google(
                    audio, 
                    language='en-IN'  # English (India) - understands both
                )
                
                # Detect if response contains Hindi characters
                has_hindi = any('\u0900' <= c <= '\u097F' for c in text)
                lang = 'hi' if has_hindi else 'en'
                
                print(f"✅ Recognized ({lang}): {text}")
                return (True, text, lang)
                
            except sr.UnknownValueError:
                print("❌ Could not understand")
                return (False, "", "")
                
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected")
            return (False, "", "")
        except Exception as e:
            print(f"❌ Error: {e}")
            return (False, "", "")
    
    def speak_hindi_gtts(self, text):
        """
        Speak text in Hindi using Google Text-to-Speech (better Hindi pronunciation)
        
        Args:
            text (str): Text to speak in Hindi
        """
        try:
            print(f"🔊 बोल रहा हूँ (Speaking): {text}")
            
            # Create gTTS object for Hindi
            tts = gTTS(text=text, lang='hi', slow=False)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            tts.save(temp_file.name)
            
            # Play the audio
            if platform.system() == 'Windows':
                os.system(f'start /min "" "{temp_file.name}"')
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'afplay "{temp_file.name}"')
            else:  # Linux
                os.system(f'mpg123 "{temp_file.name}"')
            
            # Wait for audio to finish (approximate)
            import time
            time.sleep(len(text) * 0.1)  # Rough estimate
            
            # Cleanup
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
        except Exception as e:
            print(f"❌ gTTS error: {e}, falling back to pyttsx3")
            self.speak_hindi_pyttsx3(text)
    
    def speak_hindi_pyttsx3(self, text):
        """
        Speak text in Hindi using pyttsx3 (offline, but may have accent issues)
        
        Args:
            text (str): Text to speak in Hindi
        """
        try:
            print(f"🔊 Speaking (pyttsx3): {text}")
            self.pyttsx3_engine.say(text)
            self.pyttsx3_engine.runAndWait()
        except Exception as e:
            print(f"❌ pyttsx3 error: {e}")
    
    def speak(self, text, language='auto', use_gtts=True):
        """
        Speak text in appropriate language
        
        Args:
            text (str): Text to speak
            language (str): Language code ('hi', 'en', 'auto')
            use_gtts (bool): Use gTTS for Hindi (better quality) or pyttsx3 (offline)
        """
        # Auto-detect language if needed
        if language == 'auto':
            has_hindi = any('\u0900' <= c <= '\u097F' for c in text)
            language = 'hi' if has_hindi else 'en'
        
        # Speak based on language
        if language == 'hi' and use_gtts:
            self.speak_hindi_gtts(text)
        elif language == 'hi':
            self.speak_hindi_pyttsx3(text)
        else:
            # English using pyttsx3
            try:
                # Set English voice
                voices = self.pyttsx3_engine.getProperty('voices')
                for voice in voices:
                    if 'english' in voice.name.lower() or 'david' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.pyttsx3_engine.setProperty('voice', voice.id)
                        break
                
                self.pyttsx3_engine.setProperty('rate', 165)
                self.pyttsx3_engine.say(text)
                self.pyttsx3_engine.runAndWait()
            except Exception as e:
                print(f"❌ English TTS error: {e}")


# Quick test function
if __name__ == "__main__":
    print("🎤 Hindi Speech Engine Test")
    print("=" * 50)
    
    engine = HindiSpeechEngine()
    
    # Test Hindi TTS
    print("\n1. Testing Hindi Text-to-Speech...")
    engine.speak("नमस्ते! मैं शैडो हूँ। आप कैसे हैं?", language='hi')
    
    # Test English TTS
    print("\n2. Testing English Text-to-Speech...")
    engine.speak("Hello! I am SHADOW. How are you?", language='en')
    
    # Test recognition
    print("\n3. Testing Hindi Speech Recognition...")
    print("बोलिए (Speak now)...")
    success, text, lang = engine.recognize_bilingual()
    
    if success:
        print(f"✅ Recognized ({lang}): {text}")
        engine.speak(f"आपने कहा: {text}", language='hi')
    else:
        print("❌ Recognition failed")
    
    print("\n✅ Test complete!")
