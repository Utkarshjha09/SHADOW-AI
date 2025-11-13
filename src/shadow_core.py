# src/shadow_core.py
from openai import OpenAI
import os
import sys
import yaml

# Add src directory to path for memory import
sys.path.insert(0, os.path.dirname(__file__))
from memory import ConversationMemory

# Initialize OpenAI client only if API key is available
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# Initialize memory system
memory = ConversationMemory()

def load_config():
    """Load configuration from the YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'shadow_config.yaml')
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Config file not found at {config_path}")
        return {
            "assistant_name": "SHADOW",
            "signature_phrase": "SHADOW online.",
            "persona": "You are SHADOW, a personal AI assistant."
        }

def ask_shadow(user_input: str, config=None) -> str:
    """Send a prompt to SHADOW and get a response with memory context."""
    if config is None:
        config = load_config()
    
    if not client:
        return "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
    
    # Get context from memory (last 5 interactions)
    context = memory.get_recent_context(5)
    
    # Build messages with context
    messages = [
        {"role": "system", "content": config.get("persona", "You are SHADOW, a personal AI assistant.")},
    ]
    
    # Add conversation context if available
    if context:
        messages.append({"role": "system", "content": f"Recent conversation context:\n{context}"})
    
    messages.append({"role": "user", "content": user_input})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        reply = response.choices[0].message.content
        
        # Store the interaction in memory
        memory.add_interaction(user_input, reply)
        
        return reply
    except Exception as e:
        error_msg = f"Error communicating with SHADOW: {str(e)}"
        # Still store failed interactions for debugging
        memory.add_interaction(user_input, error_msg)
        return error_msg
