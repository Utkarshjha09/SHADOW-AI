"""
Hindi Voice Assistant - Simple Demo
Shows how to use the new Hindi Speech Module
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from voice.hindi_speech import HindiSpeechEngine

def main():
    print("=" * 60)
    print("🎤 SHADOW - Hindi Voice Assistant Demo")
    print("=" * 60)
    
    # Initialize
    engine = HindiSpeechEngine()
    
    # Welcome message
    print("\n🌟 Welcome! मैं SHADOW हूँ!")
    engine.speak("नमस्ते! मैं शैडो हूँ, आपका हिंदी सहायक।", language='hi', use_gtts=True)
    
    print("\n" + "=" * 60)
    print("Available Commands:")
    print("  Hindi: नमस्ते, समय बताओ, तारीख क्या है")
    print("  English: Hello, what time is it, what's the date")
    print("  Mixed: Hey Shadow, aap kaise ho?")
    print("  Say 'exit' or 'बाहर निकलो' to quit")
    print("=" * 60)
    
    while True:
        try:
            print("\n👂 Listening... (Speak now)")
            success, text, lang = engine.recognize_bilingual(timeout=10, phrase_time_limit=10)
            
            if not success:
                print("❌ Didn't catch that. Please try again.")
                continue
            
            print(f"✅ You said ({lang}): {text}")
            
            # Check for exit
            if any(word in text.lower() for word in ['exit', 'quit', 'bye', 'बाहर', 'बंद']):
                if lang == 'hi':
                    goodbye = "अलविदा! फिर मिलेंगे।"
                else:
                    goodbye = "Goodbye! See you again."
                
                print(f"👋 {goodbye}")
                engine.speak(goodbye, language=lang, use_gtts=True)
                break
            
            # Generate response
            response = generate_response(text, lang)
            print(f"🤖 SHADOW: {response}")
            
            # Speak response
            engine.speak(response, language=lang, use_gtts=(lang == 'hi'))
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    print("\n✅ Demo completed!")

def generate_response(text, lang):
    """Generate appropriate response based on input"""
    text_lower = text.lower()
    
    # Greetings
    if any(word in text_lower for word in ['hello', 'hi', 'hey', 'नमस्ते', 'हैलो']):
        if lang == 'hi':
            return "नमस्ते! आप कैसे हैं? मैं आपकी कैसे मदद कर सकता हूँ?"
        else:
            return "Hello! How are you? How can I help you?"
    
    # Time
    if any(word in text_lower for word in ['time', 'समय', 'kitne baje', 'बजे']):
        from datetime import datetime
        now = datetime.now()
        if lang == 'hi':
            return f"अभी समय है {now.strftime('%I:%M %p')} बजे।"
        else:
            return f"The current time is {now.strftime('%I:%M %p')}."
    
    # Date
    if any(word in text_lower for word in ['date', 'today', 'aaj', 'आज', 'tarikh', 'तारीख']):
        from datetime import datetime
        now = datetime.now()
        if lang == 'hi':
            return f"आज की तारीख है {now.strftime('%d %B %Y')}।"
        else:
            return f"Today's date is {now.strftime('%B %d, %Y')}."
    
    # How are you
    if any(word in text_lower for word in ['how are you', 'kaise ho', 'कैसे हो', 'kaisa hai']):
        if lang == 'hi':
            return "मैं बिल्कुल ठीक हूँ, धन्यवाद! आप कैसे हैं?"
        else:
            return "I'm doing great, thank you! How are you?"
    
    # Name
    if any(word in text_lower for word in ['your name', 'naam', 'नाम', 'kaun ho', 'कौन']):
        if lang == 'hi':
            return "मेरा नाम शैडो है। मैं आपका व्यक्तिगत AI सहायक हूँ।"
        else:
            return "My name is SHADOW. I'm your personal AI assistant."
    
    # Default
    if lang == 'hi':
        return f"समझ गया। आपने कहा: {text}। मैं अभी सीख रहा हूँ!"
    else:
        return f"I understood: {text}. I'm still learning!"

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
