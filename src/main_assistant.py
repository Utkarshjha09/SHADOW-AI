import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from voice.voice_main import VoiceAssistant
from voice.wake_word import WakeWordDetector
from ai_backends.ollama_backend import OllamaAI
from tools.system_tools import get_microphone_input
from utils.language_utils import detect_language, translate_wake_words

# Wake words for activation
WAKE_WORDS = translate_wake_words()

def main():
    print("Personal Voice Assistant (Ollama, Hindi/English)")
    print("Supported wake words:", WAKE_WORDS[:5], "...")  # Show first 5
    
    wake_detector = WakeWordDetector(WAKE_WORDS)
    assistant = VoiceAssistant()
    ollama_ai = OllamaAI()
    
    # Check if Ollama is available
    if not ollama_ai.is_available():
        print("Warning: Ollama server not available. Please start Ollama first.")
    
    print("Starting voice assistant...")
    
    while True:
        try:
            print("\nListening for wake word...")
            spoken = get_microphone_input()
            
            if wake_detector.is_wake_word(spoken):
                print("Wake word detected!")
                assistant.speak("Yes, how can I help you?")
                
                print("Listening for query...")
                query = get_microphone_input()
                
                if query:
                    lang = detect_language(query)
                    print(f"Detected language: {lang}")
                    
                    response = ollama_ai.get_response(query, lang)
                    assistant.speak(response, lang)
                else:
                    assistant.speak("I didn't hear anything. Please try again.")
                    
        except KeyboardInterrupt:
            print("\nShutting down voice assistant...")
            assistant.speak("Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()