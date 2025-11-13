"""
Language detection and utilities for SHADOW Voice Assistant
"""
import re

def detect_language(text):
    """
    Detect language of the input text
    
    Args:
        text (str): Input text to analyze
        
    Returns:
        str: Language code ('hi' for Hindi, 'en' for English)
    """
    if not text:
        return 'en'
    
    # Check for Devanagari script (Hindi)
    devanagari_pattern = r'[\u0900-\u097F]'
    if re.search(devanagari_pattern, text):
        return 'hi'
    
    # Check for common Hindi words in Roman script
    hindi_words = [
        'kya', 'hai', 'hain', 'main', 'mein', 'aap', 'tum', 'yeh', 'woh',
        'kaise', 'kahan', 'kab', 'kyun', 'accha', 'theek', 'namaste',
        'dhanyawad', 'shukriya', 'batao', 'bolo', 'suno', 'suun'
    ]
    
    text_lower = text.lower()
    for word in hindi_words:
        if word in text_lower:
            return 'hi'
    
    # Default to English
    return 'en'

def get_greeting(language='en'):
    """
    Get appropriate greeting based on language
    
    Args:
        language (str): Language code
        
    Returns:
        str: Greeting message
    """
    greetings = {
        'en': "Hello! I'm SHADOW, your personal assistant. How can I help you?",
        'hi': "नमस्ते! मैं SHADOW हूँ, आपका व्यक्तिगत सहायक। मैं आपकी कैसे मदद कर सकता हूँ?"
    }
    return greetings.get(language, greetings['en'])

def get_goodbye(language='en'):
    """
    Get appropriate goodbye based on language
    
    Args:
        language (str): Language code
        
    Returns:
        str: Goodbye message
    """
    goodbyes = {
        'en': "Goodbye! Have a great day!",
        'hi': "अलविदा! आपका दिन शुभ हो!"
    }
    return goodbyes.get(language, goodbyes['en'])

def get_error_message(language='en'):
    """
    Get appropriate error message based on language
    
    Args:
        language (str): Language code
        
    Returns:
        str: Error message
    """
    error_messages = {
        'en': "I'm sorry, I didn't understand that. Could you please repeat?",
        'hi': "क्षमा करें, मैं यह समझ नहीं पाया। कृपया दोबारा कहें?"
    }
    return error_messages.get(language, error_messages['en'])

def translate_wake_words():
    """
    Get wake words in both languages
    
    Returns:
        list: List of wake words in English and Hindi
    """
    return [
        # English variations
        "hey shadow", "hi shadow", "hello shadow", "shadow",
        "hey ashadow", "hi ashadow", "hello ashadow", "ashadow",
        
        # Hindi variations (Roman script)
        "kya shadow", "suun shadow", "suno shadow", "shadow suno",
        "shadow kya", "shadow bolo", "shadow batao",
        
        # Hindi variations (Devanagari script)
        "क्या shadow", "सुनो shadow", "shadow सुनो",
        "shadow क्या", "shadow बोलो", "shadow बताओ"
    ]
