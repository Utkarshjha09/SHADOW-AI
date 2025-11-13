"""
Test Hindi Speech Module
Quick test for Hindi speech recognition and synthesis
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from voice.hindi_speech import HindiSpeechEngine

def main():
    print("=" * 60)
    print("🎤 SHADOW Hindi Speech Module Test")
    print("=" * 60)
    
    # Initialize engine
    print("\n📦 Initializing Hindi Speech Engine...")
    engine = HindiSpeechEngine()
    print("✅ Engine initialized successfully!")
    
    # Test 1: Hindi TTS with gTTS
    print("\n" + "=" * 60)
    print("Test 1: Hindi Text-to-Speech (gTTS - High Quality)")
    print("=" * 60)
    test_text_hi = "नमस्ते! मैं शैडो हूँ, आपका हिंदी सहायक।"
    print(f"Speaking: {test_text_hi}")
    engine.speak(test_text_hi, language='hi', use_gtts=True)
    
    # Test 2: English TTS
    print("\n" + "=" * 60)
    print("Test 2: English Text-to-Speech")
    print("=" * 60)
    test_text_en = "Hello! I am SHADOW, your bilingual assistant."
    print(f"Speaking: {test_text_en}")
    engine.speak(test_text_en, language='en')
    
    # Test 3: Auto language detection
    print("\n" + "=" * 60)
    print("Test 3: Auto Language Detection")
    print("=" * 60)
    mixed_text = "नमस्ते, How are you?"
    print(f"Speaking (auto-detect): {mixed_text}")
    engine.speak(mixed_text, language='auto')
    
    # Test 4: Speech Recognition (Interactive)
    print("\n" + "=" * 60)
    print("Test 4: Hindi/English Speech Recognition")
    print("=" * 60)
    print("💬 Say something in Hindi or English...")
    print("Examples:")
    print("  - Hindi: नमस्ते शैडो")
    print("  - English: Hello Shadow")
    print("  - Mixed: Hey Shadow, aap kaise ho?")
    print("\nListening in 3 seconds...")
    
    import time
    time.sleep(3)
    
    success, text, lang = engine.recognize_bilingual(timeout=10)
    
    if success:
        print(f"\n✅ Recognition successful!")
        print(f"   Language: {lang.upper()}")
        print(f"   Text: {text}")
        
        # Respond
        if lang == 'hi':
            response = f"आपने कहा: {text}"
        else:
            response = f"You said: {text}"
        
        print(f"\n🔊 Responding: {response}")
        engine.speak(response, language=lang)
    else:
        print("\n❌ Recognition failed - no speech detected or couldn't understand")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\n📝 Summary:")
    print("  ✓ gTTS (Google) - Best for Hindi quality")
    print("  ✓ pyttsx3 - Offline, works for English")
    print("  ✓ Bilingual recognition - Supports Hindi & English")
    print("  ✓ Auto language detection - From Devanagari script")
    print("\n🎯 Ready to use in SHADOW!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
