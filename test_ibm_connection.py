"""
Test script for IBM WatsonX services integration
Verifies NLU, TTS, and STT capabilities
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    from services.watsonx_nlu_service import WatsonXNLUService
    from services.watsonx_tts_service import WatsonXTTSService
    from services.watsonx_stt_service import WatsonXSTTService
    from config import settings
except ImportError as e:
    print(f"Error: Missing dependencies or project structure issues: {e}")
    sys.exit(1)

def print_header(title):
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def test_nlu():
    print_header("Testing WatsonX NLU")
    service = WatsonXNLUService()
    
    if not service.nlu:
        print("❌ NLU Service not initialized (check credentials in .env)")
        return False
        
    test_query = "What is the impact of changing auth.py?"
    print(f"Query: '{test_query}'")
    
    try:
        # We use parse_query which internally calls _nlu_parse if self.nlu is set
        result = service.parse_query(test_query)
        print("✅ NLU Response received!")
        print(f"Detected Intent: {result.get('intent')}")
        return True
    except Exception as e:
        print(f"❌ NLU Test failed: {e}")
        return False

def test_tts():
    print_header("Testing WatsonX TTS")
    service = WatsonXTTSService()
    
    if not service.tts:
        print("❌ TTS Service not initialized (check credentials in .env)")
        return False
        
    test_text = "ImpactGuard system is online and ready for analysis."
    print(f"Synthesizing text: '{test_text}'")
    
    try:
        audio_data = service.synthesize_speech(test_text)
        if audio_data:
            print(f"✅ TTS Success! Received {len(audio_data)} bytes of audio data.")
            return True
        else:
            print("❌ TTS failed: No audio data returned.")
            return False
    except Exception as e:
        print(f"❌ TTS Test failed: {e}")
        return False

def test_stt():
    print_header("Testing WatsonX STT")
    service = WatsonXSTTService()
    
    if not service.stt:
        print("❌ STT Service not initialized (check credentials in .env)")
        return False
    
    print("ℹ️ STT requires an audio file to test transcription.")
    print("Checking for available models instead to verify connection...")
    
    try:
        models = service.get_available_models()
        if models:
            print(f"✅ STT Success! Found {len(models)} available models.")
            print(f"Sample model: {models[0]}")
            return True
        else:
            print("❌ STT failed: No models found.")
            return False
    except Exception as e:
        print(f"❌ STT Test failed: {e}")
        return False

def main():
    print("ImpactGuard IBM WatsonX Connection Test")
    print(f"Using .env file: {os.path.exists('.env')}")
    
    results = {
        "NLU": test_nlu(),
        "TTS": test_tts(),
        "STT": test_stt()
    }
    
    print_header("Final Results Summary")
    for service, status in results.items():
        print(f"{service:4}: {'✅ WORKING' if status else '❌ FAILED/NOT CONFIGURED'}")

if __name__ == "__main__":
    main()
