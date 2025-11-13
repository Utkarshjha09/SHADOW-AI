"""
Wake word detection module for SHADOW voice assistant
Enhanced with multiple wake words and language detection
"""
import speech_recognition as sr
from fuzzywuzzy import fuzz
import threading
import time
from .wake_words import DEFAULT_WAKE_WORDS, is_wake_word as check_wake_word, detect_language

class WakeWordDetector:
    def __init__(self, wake_words=None, threshold=75):
        """
        Initialize wake word detector
        
        Args:
            wake_words (list): List of wake words to detect (uses DEFAULT_WAKE_WORDS if None)
            threshold (int): Similarity threshold for fuzzy matching (0-100)
        """
        self.wake_words = wake_words or DEFAULT_WAKE_WORDS
        self.wake_words = [word.lower() for word in self.wake_words]
        self.threshold = threshold
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.detected_language = 'en'
        
        # Adjust for ambient noise
        print("🎙️ Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready!")
    
    def is_wake_word(self, text):
        """
        Check if the given text contains a wake word
        
        Args:
            text (str): Text to check for wake words
            
        Returns:
            tuple: (bool, str) - (is_wake_word_detected, detected_language)
        """
        if not text:
            return False, 'en'
        
        detected, lang = check_wake_word(text, self.wake_words, self.threshold)
        
        # If wake word detected, also check overall language of the text
        if detected:
            text_lang = detect_language(text)
            # Use text language if it's Hindi, otherwise use wake word language
            final_lang = text_lang if text_lang == 'hi' else lang
            self.detected_language = final_lang
            return True, final_lang
        
        return False, 'en'
    
    def listen_for_wake_word(self, callback=None, timeout=None):
        """
        Continuously listen for wake words
        
        Args:
            callback (function): Function to call when wake word is detected (receives text and language)
            timeout (int): Timeout in seconds (None for infinite)
            
        Returns:
            tuple: (bool, str) - (wake_word_detected, detected_language)
        """
        self.is_listening = True
        start_time = time.time()
        
        print("👂 Listening for wake words...")
        print(f"📝 Say: {', '.join(self.wake_words[:5])}...")
        
        while self.is_listening:
            if timeout and (time.time() - start_time) > timeout:
                break
                
            try:
                with self.microphone as source:
                    # Quick ambient noise adjustment
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    # Listen for audio with a short timeout
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=4)
                
                # Recognize speech (en-IN supports both English and Hindi)
                text = self.recognizer.recognize_google(audio, language='en-IN')
                print(f"👂 Heard: {text}")
                
                is_wake, lang = self.is_wake_word(text)
                if is_wake:
                    print(f"✨ Wake word detected! Language: {lang.upper()}")
                    if callback:
                        callback(text, lang)
                    return True, lang
                        
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                pass
            except sr.UnknownValueError:
                # Could not understand audio
                pass
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                time.sleep(1)
            except KeyboardInterrupt:
                print("\n⚠️ Wake word detection stopped by user")
                break
                
        return False, 'en'
    
    def stop_listening(self):
        """Stop the wake word detection"""
        self.is_listening = False
    
    def get_microphone_input(self, timeout=5):
        """
        Get microphone input for a specified duration
        
        Args:
            timeout (int): Maximum time to wait for input
            
        Returns:
            str: Recognized text or empty string if no speech detected
        """
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("No speech detected")
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return ""
