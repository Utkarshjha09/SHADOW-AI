#!/usr/bin/env python3
"""
SHADOW Enhanced Voice Mode - Launcher
Runs the enhanced voice assistant with multi-language wake words
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Launch enhanced voice assistant"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🎙️ SHADOW Enhanced Voice Assistant 🎙️               ║
║                                                              ║
║  Multi-Language Wake Words | Auto Language Detection        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Try to import AI backend
        try:
            from ai_backends.ollama_backend import OllamaBackend
            print("✅ Loading AI backend (Ollama)...")
            ai_backend = OllamaBackend()
            print("✅ AI backend loaded successfully!")
        except Exception as e:
            print(f"⚠️  AI backend not available: {e}")
            print("ℹ️  Running in demo mode with basic responses")
            ai_backend = None
        
        # Import and start enhanced voice assistant
        from voice.enhanced_voice_assistant import EnhancedVoiceAssistant
        
        assistant = EnhancedVoiceAssistant(ai_backend=ai_backend)
        
        print("\n📝 Wake Words:")
        print("   English: Hey Shadow, Hi Shadow, Ok Shadow")
        print("   Hindi:   Sunn Shadow, Bol Shadow, Kya Shadow")
        print("\n💡 Tip: Ask in English → Get English reply")
        print("        Ask in Hindi → Get Hindi reply")
        print("\n⌨️  Press Ctrl+C to exit\n")
        
        assistant.start()
        
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using SHADOW Enhanced Voice Assistant!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
