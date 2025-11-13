"""
Enhanced Voice Assistant for SHADOW with multi-language support and wake words
"""
import sys
import os
from .speech_engine import SpeechEngine
from .wake_word import WakeWordDetector
from .wake_words import DEFAULT_WAKE_WORDS, detect_language

class EnhancedVoiceAssistant:
    def __init__(self, ai_backend=None):
        """
        Initialize the enhanced voice assistant
        
        Args:
            ai_backend: AI backend instance for processing queries (optional)
        """
        print("🚀 Initializing SHADOW Enhanced Voice Assistant...")
        self.speech_engine = SpeechEngine()
        self.wake_detector = WakeWordDetector(wake_words=DEFAULT_WAKE_WORDS, threshold=75)
        self.ai_backend = ai_backend
        self.is_active = False
        self.current_language = 'en'
        
        # Greeting messages in different languages
        self.greetings = {
            'en': [
                "Yes, I'm listening!",
                "How can I help you?",
                "I'm here!",
                "What can I do for you?"
            ],
            'hi': [
                "Haan, main sun raha hoon!",
                "Kaise madad kar sakta hoon?",
                "Main yahaan hoon!",
                "Kya chahiye?"
            ]
        }
        
        print("✅ SHADOW is ready!")
    
    def speak(self, text, language=None, priority=False):
        """
        Speak text in the specified language
        
        Args:
            text: Text to speak
            language: Language code ('en' or 'hi'), uses current_language if None
            priority: If True, speak immediately
        """
        lang = language or self.current_language
        self.speech_engine.speak(text, priority=priority, language=lang)
    
    def listen(self, timeout=5, language_hint=None):
        """
        Listen for voice input
        
        Args:
            timeout: Maximum time to wait for input
            language_hint: Expected language ('en-IN' supports both)
            
        Returns:
            tuple: (text, detected_language)
        """
        lang_code = language_hint or 'en-IN'
        text = self.speech_engine.listen_for_speech(timeout=timeout, phrase_timeout=5, language=lang_code)
        
        if text:
            # Detect language of the spoken text
            detected_lang = detect_language(text)
            self.current_language = detected_lang
            return text, detected_lang
        
        return None, self.current_language
    
    def get_greeting(self, language='en'):
        """Get a greeting message in the specified language"""
        import random
        greetings = self.greetings.get(language, self.greetings['en'])
        return random.choice(greetings)
    
    def process_query(self, query, language='en'):
        """
        Process a voice query using AI backend or provide a default response
        
        Args:
            query: The user's query
            language: Language of the query
            
        Returns:
            str: The assistant's response
        """
        try:
            # If AI backend is available, use it
            if self.ai_backend and hasattr(self.ai_backend, 'process_query'):
                response = self.ai_backend.process_query(query, language=language)
                return response
            
            # Default responses based on language
            if language == 'hi':
                return f"Aapne kaha: {query}. Main iska jawab de raha hoon."
            else:
                return f"You said: {query}. I'm processing your request."
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            if language == 'hi':
                return "Maaf kijiye, kuch gadbad ho gayi."
            else:
                return "Sorry, I encountered an error."
    
    def wait_for_wake_word(self):
        """
        Wait for wake word to be spoken
        
        Returns:
            tuple: (detected, language)
        """
        print("\n" + "="*60)
        print("🌟 SHADOW is now listening for wake words...")
        print("📝 Try saying:")
        print("   English: 'Hey Shadow', 'Hi Shadow', 'Ok Shadow'")
        print("   Hindi: 'Sunn Shadow', 'Bol Shadow', 'Kya Shadow'")
        print("="*60 + "\n")
        
        detected, lang = self.wake_detector.listen_for_wake_word()
        
        if detected:
            # Play wake-up sound
            self.speech_engine.play_wakeup_sound()
            self.current_language = lang
            return True, lang
        
        return False, 'en'
    
    def run_conversation_loop(self):
        """Run a single conversation after wake word is detected"""
        try:
            # Greet the user in their language
            greeting = self.get_greeting(self.current_language)
            self.speak(greeting, priority=True)
            
            # Listen for the actual query
            query, query_lang = self.listen(timeout=10)
            
            if query:
                # Update language based on query
                self.current_language = query_lang
                
                # Process the query
                response = self.process_query(query, query_lang)
                
                # Respond in the same language
                self.speak(response, language=query_lang, priority=True)
            else:
                # No query detected
                if self.current_language == 'hi':
                    self.speak("Maaf kijiye, maine kuch nahi suna.", priority=True)
                else:
                    self.speak("I didn't catch that.", priority=True)
                    
        except Exception as e:
            print(f"❌ Error in conversation loop: {e}")
            self.speak("Sorry, an error occurred.", priority=True)
    
    def start(self):
        """Start the voice assistant main loop"""
        self.is_active = True
        
        print("\n" + "🌟"*30)
        print("  SHADOW Enhanced Voice Assistant - Now Running!")
        print("🌟"*30 + "\n")
        
        try:
            while self.is_active:
                # Wait for wake word
                detected, lang = self.wait_for_wake_word()
                
                if detected:
                    # Run conversation
                    self.run_conversation_loop()
                    
                    # Small pause before listening for next wake word
                    import time
                    time.sleep(0.5)
                    
        except KeyboardInterrupt:
            print("\n\n⚠️ SHADOW shutting down...")
            self.stop()
    
    def stop(self):
        """Stop the voice assistant"""
        self.is_active = False
        self.wake_detector.stop_listening()
        
        if self.current_language == 'hi':
            self.speak("Alvida! Phir milenge.", priority=True)
        else:
            self.speak("Goodbye! See you later.", priority=True)
        
        print("👋 SHADOW has been stopped.")


if __name__ == "__main__":
    # Run the enhanced voice assistant
    assistant = EnhancedVoiceAssistant()
    assistant.start()
