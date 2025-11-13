"""
Conversation Memory for SHADOW Voice Assistant
"""
from datetime import datetime
from typing import List, Dict, Any

class ConversationMemory:
    def __init__(self, max_messages=100):
        """
        Initialize conversation memory
        
        Args:
            max_messages (int): Maximum number of messages to store
        """
        self.max_messages = max_messages
        self.messages = []
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add a message to conversation memory
        
        Args:
            role (str): Role of the message sender ('user' or 'assistant')
            content (str): Content of the message
            metadata (dict): Optional metadata (language, timestamp, etc.)
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        
        self.messages.append(message)
        
        # Keep only the most recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent messages from memory
        
        Args:
            count (int): Number of recent messages to retrieve
            
        Returns:
            List[Dict]: List of recent messages
        """
        return self.messages[-count:] if count > 0 else self.messages
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """
        Get all messages from memory
        
        Returns:
            List[Dict]: List of all messages
        """
        return self.messages.copy()
    
    def clear(self):
        """Clear all messages from memory"""
        self.messages.clear()
    
    def get_context(self, max_chars: int = 1000) -> str:
        """
        Get conversation context as a string
        
        Args:
            max_chars (int): Maximum characters to return
            
        Returns:
            str: Conversation context
        """
        if not self.messages:
            return ""
        
        context_parts = []
        total_chars = 0
        
        # Build context from recent messages
        for message in reversed(self.messages):
            role = message['role']
            content = message['content']
            
            line = f"{role}: {content}\n"
            
            if total_chars + len(line) > max_chars:
                break
                
            context_parts.insert(0, line)
            total_chars += len(line)
        
        return "".join(context_parts)
    
    def search_messages(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search messages by content
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List[Dict]: Matching messages
        """
        query_lower = query.lower()
        matches = []
        
        for message in self.messages:
            if query_lower in message['content'].lower():
                matches.append(message)
                
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get conversation statistics
        
        Returns:
            Dict: Statistics about the conversation
        """
        if not self.messages:
            return {
                'total_messages': 0,
                'user_messages': 0,
                'assistant_messages': 0,
                'first_message_time': None,
                'last_message_time': None
            }
        
        user_count = sum(1 for msg in self.messages if msg['role'] == 'user')
        assistant_count = sum(1 for msg in self.messages if msg['role'] == 'assistant')
        
        return {
            'total_messages': len(self.messages),
            'user_messages': user_count,
            'assistant_messages': assistant_count,
            'first_message_time': self.messages[0]['timestamp'],
            'last_message_time': self.messages[-1]['timestamp']
        }
