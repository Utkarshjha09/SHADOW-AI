# src/voice_main.py
"""
Voice-enabled version of SHADOW personal assistant
"""
import os
import sys
from shadow_core import ask_shadow, load_config
from voice import SpeechEngine
from memory import ConversationMemory
from tools import SystemTools, plugin_manager

class VoiceShadow:
    def __init__(self):
        self.config = load_config()
        self.memory = ConversationMemory()
        self.speech_engine = None
        self.tools = SystemTools()
        self.voice_mode = False
        
        # Check if OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  Warning: OPENAI_API_KEY environment variable not set!")
            print("   Set it with: set OPENAI_API_KEY=your_api_key_here")
            print("   Voice assistant will still work for system commands.\n")
    
    def initialize_voice(self):
        """Initialize voice recognition and text-to-speech."""
        try:
            print("Initializing voice engine...")
            self.speech_engine = SpeechEngine(self.config)
            self.voice_mode = True
            print("✅ Voice engine initialized successfully!")
            return True
        except ImportError as e:
            print(f"❌ Voice dependencies not installed: {e}")
            print("Install with: pip install speechrecognition pyttsx3 pyaudio")
            return False
        except Exception as e:
            print(f"❌ Voice initialization failed: {e}")
            return False
    
    def process_command(self, user_input: str) -> str:
        """Process user command and return response."""
        user_input_lower = user_input.lower().strip()
        
        # Handle file management commands
        if user_input_lower.startswith("file "):
            return self.handle_file_command(user_input_lower[5:])
        
        # Handle system commands
        elif user_input_lower.startswith("system "):
            return self.handle_system_command(user_input_lower[7:])
        elif "time" in user_input_lower or "date" in user_input_lower:
            time_info = self.tools.get_current_time()
            return f"Current time: {time_info['datetime']}, {time_info['day_of_week']}"
        elif "system info" in user_input_lower:
            sys_info = self.tools.get_system_info()
            return f"System: {sys_info['platform']} {sys_info['architecture']}, Python {sys_info['python_version']}"
        elif "resources" in user_input_lower or "performance" in user_input_lower:
            resources = self.tools.get_system_resources()
            return f"CPU: {resources.get('cpu_usage', 'N/A')}, Memory: {resources.get('memory_usage', 'N/A')}"
        
        # Handle AI queries
        if os.getenv("OPENAI_API_KEY"):
            response = ask_shadow(user_input, self.config)
            return response
        else:
            return "OpenAI API key not configured. I can only handle system and file commands right now."
    
    def handle_file_command(self, command: str) -> str:
        """Handle file management commands."""
        file_plugin = plugin_manager.get_plugin('files')
        
        if command.startswith("create "):
            parts = command[7:].split(" ", 1)
            if len(parts) < 1:
                return "Usage: file create <filepath> [content]"
            filepath = parts[0]
            content = parts[1] if len(parts) > 1 else ""
            result = file_plugin.create_file(filepath, content)
            return result.get('message', result.get('error', 'Unknown error'))
        
        elif command.startswith("read "):
            filepath = command[5:].strip()
            result = file_plugin.read_file(filepath)
            if 'error' in result:
                return result['error']
            return f"File content ({result['size']} bytes):\n{result['content'][:500]}..."
        
        elif command.startswith("info "):
            filepath = command[5:].strip()
            result = file_plugin.get_file_info(filepath)
            if 'error' in result:
                return result['error']
            return f"File: {result['path']}, Size: {result['size_human']}, Modified: {result['modified']}"
        
        elif command.startswith("search "):
            parts = command[7:].split(" ", 1)
            directory = parts[0]
            pattern = parts[1] if len(parts) > 1 else "*"
            result = file_plugin.search_files(directory, pattern)
            if 'error' in result:
                return result['error']
            return f"Found {result['total_found']} files matching '{pattern}'"
        
        else:
            return f"Unknown file command: {command}. Try: create, read, info, search"
    
    def handle_system_command(self, command: str) -> str:
        """Handle system-level commands."""
        if command.startswith("list "):
            path = command[5:].strip() or "."
            result = self.tools.list_directory(path)
            if "error" in result:
                return result["error"]
            return f"Found {result['total_count']} items in {path}"
        elif command.startswith("run "):
            cmd = command[4:].strip()
            result = self.tools.run_command(cmd, safe_mode=True)
            if "error" in result:
                return result["error"]
            return f"Command executed. Output: {result.get('stdout', 'No output')}"
        else:
            return f"Unknown system command: {command}"
    
    def run_text_mode(self):
        """Run SHADOW in text-only mode."""
        print(f"\n🖥️  {self.config['signature_phrase']}")
        print("Text mode active. Type 'voice' to switch to voice mode, 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("SHADOW: Goodbye.")
                    break
                elif user_input.lower() == "voice":
                    if self.initialize_voice():
                        self.run_voice_mode()
                    continue
                elif user_input.lower() == "help":
                    self.show_help()
                    continue
                elif not user_input:
                    continue
                
                response = self.process_command(user_input)
                print(f"SHADOW: {response}")
                
            except KeyboardInterrupt:
                print("\nSHADOW: Goodbye.")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run_voice_mode(self):
        """Run SHADOW in voice mode."""
        print(f"\n🎤 {self.config['signature_phrase']}")
        print("Voice mode active. Say 'text mode' to switch back, 'quit' to exit.")
        print("Listening for commands...\n")
        
        self.speech_engine.speak("Voice mode activated. How can I help you?", priority=True)
        
        while True:
            try:
                # Listen for voice input
                user_input = self.speech_engine.listen_for_speech(timeout=10)
                
                if user_input is None:
                    continue
                
                # Handle exit commands
                if any(word in user_input for word in ["exit", "quit", "goodbye", "stop"]):
                    self.speech_engine.speak("Goodbye!")
                    break
                elif "text mode" in user_input:
                    self.speech_engine.speak("Switching to text mode")
                    self.voice_mode = False
                    return
                elif not user_input.strip():
                    continue
                
                # Process the command
                response = self.process_command(user_input)
                
                # Speak the response
                self.speech_engine.speak(response)
                
            except KeyboardInterrupt:
                self.speech_engine.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Voice mode error: {e}")
                self.speech_engine.speak("Sorry, I encountered an error.")
    
    def show_help(self):
        """Show help information."""
        help_text = """
SHADOW Voice Assistant Commands:

💬 Chat Commands:
  - Ask any question (requires OpenAI API key)
  - "help" - Show this help
  - "quit", "exit", "bye" - Exit the program

🎤 Voice Commands:
  - "voice" - Switch to voice mode
  - "text mode" - Switch to text mode (when in voice mode)

⚙️ System Commands:
  - "time" or "date" - Get current date/time
  - "system info" - Get system information
  - "resources" - Get system resource usage
  - "system list [path]" - List directory contents
  - "system run [command]" - Run safe system commands

🧠 Memory: SHADOW remembers recent conversations for context

Environment Setup:
  - Set OPENAI_API_KEY for AI features
  - Install voice deps: pip install speechrecognition pyttsx3 pyaudio
        """
        print(help_text)
    
    def run(self):
        """Main entry point for SHADOW."""
        print("=" * 50)
        print("    🌑 SHADOW Personal Voice Assistant")
        print("=" * 50)
        
        # Show session info
        session_info = self.memory.get_session_summary()
        print(f"Total conversations: {session_info['total_conversations']}")
        
        # Check if voice is available
        if self.initialize_voice():
            print("Voice mode available!")
            choice = input("\nStart in voice mode? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                self.run_voice_mode()
            else:
                self.run_text_mode()
        else:
            print("Starting in text mode only.")
            self.run_text_mode()

def main():
    shadow = VoiceShadow()
    shadow.run()

if __name__ == "__main__":
    main()
