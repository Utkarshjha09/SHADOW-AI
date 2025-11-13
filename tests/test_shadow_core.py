# tests/test_shadow_core.py
import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from shadow_core import load_config, ask_shadow

def test_load_config():
    """Test configuration loading."""
    config = load_config()
    
    assert config is not None
    assert "assistant_name" in config
    assert "signature_phrase" in config
    assert "persona" in config
    assert config["assistant_name"] == "SHADOW"

def test_load_config_fallback():
    """Test config fallback when file doesn't exist."""
    # This should not raise an exception
    config = load_config()
    assert config["assistant_name"] == "SHADOW"

def test_ask_shadow_with_mock():
    """Test SHADOW response with mocked config."""
    config = {
        "persona": "You are a test assistant.",
        "assistant_name": "SHADOW"
    }
    
    # Note: This test requires OPENAI_API_KEY to be set
    # In a real test environment, you'd mock the OpenAI client
    if os.getenv("OPENAI_API_KEY"):
        response = ask_shadow("Hello", config)
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    else:
        # Test error handling when API key is missing
        original_key = os.environ.get("OPENAI_API_KEY")
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        response = ask_shadow("Hello", config)
        assert "Error communicating with SHADOW" in response
        
        # Restore original key if it existed
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key

if __name__ == "__main__":
    pytest.main([__file__])
