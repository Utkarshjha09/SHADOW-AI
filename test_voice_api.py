import requests
import io
import tempfile
import os

def test_voice_api():
    """Test the voice API with a dummy audio file"""
    print("=== Testing Voice API ===")
    
    # Create a small dummy audio file (silence)
    try:
        import wave
        import struct
        
        # Create a 1-second WAV file with silence
        sample_rate = 16000
        duration = 1  # seconds
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Generate 1 second of silence
            for i in range(sample_rate * duration):
                wav_file.writeframes(struct.pack('<h', 0))
        
        print(f"Created test audio file: {temp_file.name}")
        
        # Test the API
        with open(temp_file.name, 'rb') as audio_file:
            files = {'audio': ('test.wav', audio_file, 'audio/wav')}
            data = {'language': 'en'}
            
            response = requests.post(
                'http://localhost:8000/api/voice',
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
        
        # Clean up
        os.unlink(temp_file.name)
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_voice_api()