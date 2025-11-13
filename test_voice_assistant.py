#!/usr/bin/env python3
"""
Quick test script to verify SHADOW voice assistant is working
Tests wake word detection, language detection, and responses
"""

import requests
import json
import os
import sys

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"✓ Backend health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Backend health failed: {e}")
        return False

def test_wake_words():
    """Test wake word detection"""
    test_phrases = [
        "hey shadow how are you",
        "सुनो shadow क्या हाल है",
        "kya shadow batao",
        "hello there shadow"
    ]
    
    print("\n--- Testing Wake Words ---")
    for phrase in test_phrases:
        try:
            response = requests.post("http://localhost:8000/api/wake-word", 
                                   json={"text": phrase}, 
                                   timeout=5)
            result = response.json()
            wake_detected = result.get('is_wake_word', False)
            print(f"{'✓' if wake_detected else '✗'} '{phrase}' -> Wake: {wake_detected}")
        except Exception as e:
            print(f"✗ Error testing '{phrase}': {e}")

def test_text_chat():
    """Test text chat functionality"""
    test_messages = [
        {"message": "Hello, what's your name?", "language": "en"},
        {"message": "आपका नाम क्या है?", "language": "hi"},
        {"message": "What time is it?", "language": "auto"},
        {"message": "मौसम कैसा है?", "language": "auto"}
    ]
    
    print("\n--- Testing Text Chat ---")
    for msg_data in test_messages:
        try:
            response = requests.post("http://localhost:8000/api/chat", 
                                   json=msg_data, 
                                   timeout=10)
            result = response.json()
            if result.get('success'):
                detected_lang = result.get('detected_language', 'unknown')
                response_text = result.get('response', '')[:100] + "..."
                print(f"✓ '{msg_data['message']}' -> Lang: {detected_lang}")
                print(f"   Response: {response_text}")
            else:
                print(f"✗ Failed: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")

def test_config():
    """Test configuration endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/config", timeout=5)
        result = response.json()
        if result.get('success'):
            wake_words = result.get('config', {}).get('wake_words', [])
            print(f"\n✓ Config loaded, {len(wake_words)} wake words available")
            print(f"   Sample wake words: {wake_words[:3]}")
        else:
            print("✗ Config failed")
    except Exception as e:
        print(f"✗ Config error: {e}")

def main():
    print("SHADOW Voice Assistant - System Test")
    print("=" * 50)
    
    # Check environment
    openai_key = os.environ.get('OPENAI_API_KEY', '')
    if openai_key and not openai_key.startswith('your-'):
        print("✓ OPENAI_API_KEY is set")
    else:
        print("⚠ OPENAI_API_KEY not set - voice transcription will use fallback")
    
    # Run tests
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd c:\\Document\\SHADOW")
        print("   python src\\web\\api_server.py")
        return False
    
    test_config()
    test_wake_words() 
    test_text_chat()
    
    print("\n" + "=" * 50)
    print("🎤 To test voice input:")
    print("   1. Open http://localhost:3000 in browser")
    print("   2. Click microphone button")
    print("   3. Say 'Hey SHADOW' or 'सुनो SHADOW'")
    print("   4. Speak your question")
    print("   5. Wait for response")
    
    return True

if __name__ == "__main__":
    main()