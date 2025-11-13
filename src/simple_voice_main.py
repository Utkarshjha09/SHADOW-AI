# src/simple_voice_main.py
"""
Simple voice-enabled version of SHADOW
"""
import speech_recognition as sr
import pyttsx3
from shadow_core import load_config, ask_shadow
import os

def speak(text):
    """Convert text to speech."""
    engine = pyttsx3.init()
    
    # Configure voice settings
    voices = engine.getProperty('voices')
    # Try to set a male voice for SHADOW
    for voice in voices:
        if 'male' in voice.name.lower() or 'david' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.8)  # Volume level
    
    print(f"SHADOW: {text}")
    engine.say(text)
    engine.runAndWait()

def main():
    """Main voice interaction loop."""
    config = load_config()
    
    print("=" * 50)
    print("    🌑 SHADOW Voice Assistant")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set!")
        print("   SHADOW will have limited functionality.")
    
    # Initialize speech recognition
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    # Calibrate for ambient noise
    print("Calibrating microphone...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    # Start SHADOW
    startup_message = config["signature_phrase"]
    speak(startup_message)
    speak("How can I help you today?")
    
    while True:
        try:
            print("\n🎤 Listening...")
            
            # Listen for audio
            with mic as source:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
            print("Processing speech...")
            
            # Convert speech to text
            user_input = recognizer.recognize_google(audio)
            print(f"You: {user_input}")
            
            # Check for exit commands
            if any(word in user_input.lower() for word in ["exit", "quit", "bye", "goodbye", "stop"]):
                speak("Goodbye!")
                break
            
            # Get SHADOW's response
            reply = ask_shadow(user_input)
            speak(reply)
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected. Say something...")
            continue
        except sr.UnknownValueError:
            print("❓ Could not understand the audio. Please try again.")
            speak("Sorry, I didn't catch that. Could you repeat?")
            continue
        except sr.RequestError as e:
            print(f"🌐 Speech recognition error: {e}")
            speak("I'm having trouble with speech recognition right now.")
            continue
        except KeyboardInterrupt:
            print("\n👋 Shutting down SHADOW...")
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            speak("I encountered an error. Please try again.")

if __name__ == "__main__":
    main()
