"""
Quick test script for SHADOW Enhanced Voice Assistant
Run this to test the new wake word and language detection features
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from voice.enhanced_voice_assistant import EnhancedVoiceAssistant

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🌟 SHADOW Enhanced Voice Assistant - Test Mode 🌟         ║
║                                                              ║
║   Features:                                                  ║
║   ✅ Multiple Wake Words (English & Hindi)                  ║
║   ✅ Auto Language Detection                                ║
║   ✅ Wake-up Sound                                          ║
║   ✅ Bilingual Responses                                    ║
║                                                              ║
║   Wake Words:                                                ║
║   English: Hey Shadow, Hi Shadow, Ok Shadow                  ║
║   Hindi: Sunn Shadow, Bol Shadow, Kya Shadow                 ║
║                                                              ║
║   Press Ctrl+C to exit                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Create and start the assistant
        assistant = EnhancedVoiceAssistant()
        assistant.start()
        
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using SHADOW!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
