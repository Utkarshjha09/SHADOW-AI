"""
Ollama AI Backend for SHADOW Voice Assistant
"""
import requests
import json
import os

class OllamaAI:
    def __init__(self, model="phi3:mini", host="http://localhost:11434"):
        """
        Initialize Ollama AI backend
        
        Args:
            model (str): Name of the Ollama model to use
            host (str): Ollama server host URL
        """
        self.model = model
        self.host = host
        self.api_url = f"{host}/api/generate"
        
    def is_available(self):
        """Check if Ollama server is available"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_response(self, query, language='en'):
        """
        Get response from Ollama model
        
        Args:
            query (str): User's query
            language (str): Language code ('en' or 'hi')
            
        Returns:
            str: AI's response
        """
        try:
            print(f"[OLLAMA] Processing query: '{query}' (lang: {language})")
            
            # Prepare the prompt based on language
            if language == 'hi':
                system_prompt = "आप SHADOW हैं, एक व्यक्तिगत AI सहायक। हिंदी में उत्तर दें।"
                prompt = f"{system_prompt}\n\nउपयोगकर्ता: {query}\nSHADOW:"
            else:
                system_prompt = "You are SHADOW, a personal AI assistant. Respond in English."
                prompt = f"{system_prompt}\n\nUser: {query}\nSHADOW:"
            
            print(f"[OLLAMA] Using model: {self.model}")
            
            # Prepare request data
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 150
                }
            }
            
            print(f"[OLLAMA] Making request to: {self.api_url}")
            
            # Make request to Ollama
            response = requests.post(
                self.api_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"[OLLAMA] Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "Sorry, I couldn't generate a response.")
                print(f"[OLLAMA] Generated response: '{ai_response[:100]}...'")
                return ai_response
            else:
                error_msg = f"Error: Ollama server returned status {response.status_code}"
                print(f"[OLLAMA] {error_msg}")
                return error_msg
                
        except requests.RequestException as e:
            error_msg = f"Error connecting to Ollama: {e}"
            print(f"[OLLAMA] {error_msg}")
            return error_msg
        except json.JSONDecodeError:
            error_msg = "Error: Invalid response from Ollama server"
            print(f"[OLLAMA] {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"[OLLAMA] {error_msg}")
            return error_msg
    
    def chat_stream(self, query, language='en'):
        """
        Stream response from Ollama model (for real-time responses)
        
        Args:
            query (str): User's query
            language (str): Language code ('en' or 'hi')
            
        Yields:
            str: Partial responses from the AI
        """
        try:
            # Prepare the prompt based on language
            if language == 'hi':
                system_prompt = "आप SHADOW हैं, एक व्यक्तिगत AI सहायक। हिंदी में उत्तर दें।"
                prompt = f"{system_prompt}\n\nउपयोगकर्ता: {query}\nSHADOW:"
            else:
                system_prompt = "You are SHADOW, a personal AI assistant. Respond in English."
                prompt = f"{system_prompt}\n\nUser: {query}\nSHADOW:"
            
            # Prepare request data for streaming
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 150
                }
            }
            
            # Make streaming request to Ollama
            response = requests.post(
                self.api_url,
                json=data,
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line.decode('utf-8'))
                            if 'response' in json_response:
                                yield json_response['response']
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"Error: Ollama server returned status {response.status_code}"
                
        except requests.RequestException as e:
            yield f"Error connecting to Ollama: {e}"
        except Exception as e:
            yield f"Unexpected error: {e}"
