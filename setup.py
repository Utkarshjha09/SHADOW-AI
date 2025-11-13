"""
Setup script for SHADOW Personal Voice Assistant
"""
import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Command: {command}")
        print(f"  Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        print(f"  Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        print("✗ requirements.txt not found")
        return False
    
    # Create virtual environment
    venv_command = f"{sys.executable} -m venv venv"
    if not run_command(venv_command, "Creating virtual environment"):
        return False
    
    # Activate virtual environment and install dependencies
    if platform.system() == "Windows":
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
    
    install_command = f"{pip_path} install -r {requirements_file}"
    return run_command(install_command, "Installing Python dependencies")

def setup_web_frontend():
    """Setup React frontend"""
    react_dir = os.path.join(os.path.dirname(__file__), 'src', 'web', 'react-app')
    
    if not os.path.exists(react_dir):
        print("✗ React app directory not found")
        return False
    
    # Check if Node.js is installed
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
        print("✓ Node.js and npm are installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Node.js/npm not found. Please install Node.js first:")
        print("  https://nodejs.org/")
        return False
    
    # Install frontend dependencies
    os.chdir(react_dir)
    return run_command("npm install", "Installing frontend dependencies")

def create_config_file():
    """Create default configuration file"""
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    config_file = os.path.join(config_dir, 'shadow_config.yaml')
    
    if os.path.exists(config_file):
        print("✓ Configuration file already exists")
        return True
    
    os.makedirs(config_dir, exist_ok=True)
    
    default_config = """# SHADOW Voice Assistant Configuration

assistant:
  name: "SHADOW"
  signature_phrase: "SHADOW online."
  persona: "You are SHADOW, a personal AI assistant that can communicate in both Hindi and English."

wake_words:
  - "hey shadow"
  - "hi shadow"
  - "hello shadow"
  - "kya shadow"
  - "suun shadow"
  - "suno shadow"

languages:
  supported: ["en", "hi"]
  default: "en"
  auto_detect: true

ollama:
  host: "http://localhost:11434"
  model: "llama2"
  timeout: 30

voice:
  input_timeout: 5
  recognition_language: "auto"
  tts_engine: "edge"  # Options: edge, gtts, pyttsx3

web:
  port: 8000
  host: "0.0.0.0"
  debug: false

mobile:
  api_base_url: "http://localhost:8000/api"
"""
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(default_config)
        print("✓ Created default configuration file")
        return True
    except Exception as e:
        print(f"✗ Failed to create configuration file: {e}")
        return False

def check_ollama():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Ollama is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠ Ollama not found. Please install it:")
    print("  https://ollama.ai/")
    print("  After installation, run: ollama pull llama2")
    return False

def main():
    print("=" * 60)
    print("SHADOW Personal Voice Assistant - Setup")
    print("Multi-language (Hindi/English) AI Assistant")
    print("=" * 60)
    
    setup_success = True
    
    # Check Python version
    if not check_python_version():
        setup_success = False
    
    # Install Python dependencies
    if not install_python_dependencies():
        setup_success = False
    
    # Setup web frontend
    if not setup_web_frontend():
        setup_success = False
    
    # Create configuration file
    if not create_config_file():
        setup_success = False
    
    # Check Ollama
    check_ollama()
    
    print("\n" + "=" * 60)
    if setup_success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Make sure Ollama is running: 'ollama serve'")
        print("2. Pull a model: 'ollama pull llama2'")
        print("3. Start SHADOW:")
        print("   - Console mode: 'python shadow.py console'")
        print("   - Web mode: 'python shadow.py web'")
        print("   - Development mode: 'python shadow.py dev'")
    else:
        print("✗ Setup encountered errors. Please fix them and run setup again.")
    print("=" * 60)

if __name__ == '__main__':
    main()
