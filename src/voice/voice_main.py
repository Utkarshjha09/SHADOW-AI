"""
Voice Assistant main class for SHADOW
"""
import os
import sys
from .speech_engine import SpeechEngine
from ..memory.conversation_memory import ConversationMemory

class VoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant"""
        self.speech_engine = SpeechEngine()
        self.memory = ConversationMemory()
        self.is_active = False
    
    def speak(self, text, language='en'):
        """
        Speak the given text in the specified language
        
        Args:
            text (str): Text to speak
            language (str): Language code ('en' for English, 'hi' for Hindi)
        """
        try:
            self.speech_engine.speak(text, language)
        except Exception as e:
            print(f"Error speaking text: {e}")
    
    def listen(self, timeout=5):
        """
        Listen for voice input
        
        Args:
            timeout (int): Maximum time to wait for input
            
        Returns:
            str: Recognized text or empty string
        """
        try:
            return self.speech_engine.listen(timeout)
        except Exception as e:
            print(f"Error listening: {e}")
            return ""
    
    def process_query(self, query, language='en'):
        """
        Process a voice query
        
        Args:
            query (str): The user's query
            language (str): Language of the query
            
        Returns:
            str: The assistant's response
        """
        # Store the conversation in memory
        self.memory.add_message("user", query)
        
        # Process the query (this would integrate with your AI backend)
        response = f"I heard you say: {query}"
        
        # Store the response in memory
        self.memory.add_message("assistant", response)
        
        return response
    
    def start_conversation(self):
        """Start a voice conversation"""
        self.is_active = True
        self.speak("Hello! I'm SHADOW, your personal assistant. How can I help you?")
        
        while self.is_active:
            query = self.listen()
            if query:
                response = self.process_query(query)
                self.speak(response)
            else:
                self.speak("I didn't catch that. Could you please repeat?")
    
    def stop_conversation(self):
        """Stop the voice conversation"""
        self.is_active = False
        self.speak("Goodbye!")
