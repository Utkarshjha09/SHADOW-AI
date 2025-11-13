"""
Lightweight wake word utilities for SHADOW (string-based, no mic dependency)
Supports English and Hindi (Devanagari + Romanized) phrases.
"""
from typing import Iterable, Tuple
from fuzzywuzzy import fuzz


EN_WAKE_WORDS = [
    "hey shadow", "hi shadow", "hello shadow", "listen shadow", "shadow",
    "ok shadow", "hii shadow", "yo shadow", "sup shadow", "wake up shadow"
]

HI_WAKE_WORDS = [
    # Devanagari
    "क्या शैडो", "क्या शैडो?", "सुनो शैडो", "हेलो शैडो", "हाय शैडो",
    "क्या शेडो", "सुन शैडो", "शैडो", "बोल शैडो", "ओके शैडो",
    # Common romanized forms
    "kya shadow", "suno shadow", "sun shadow", "sunn shadow", "hello shadow", 
    "hii shadow", "hi shadow", "bol shadow", "ok shadow"
]

DEFAULT_WAKE_WORDS = [*EN_WAKE_WORDS, *HI_WAKE_WORDS]

# Wake words that are primarily Hindi
HINDI_SPECIFIC = [
    "kya shadow", "suno shadow", "sun shadow", "sunn shadow", "bol shadow",
    "क्या शैडो", "सुनो शैडो", "सुन शैडो", "बोल शैडो"
]


def normalize(s: str) -> str:
    return (s or "").strip().lower()


def is_wake_word(text: str, wake_words: Iterable[str] = None, threshold: int = 78) -> Tuple[bool, str]:
    """
    Fuzzy check whether text contains any wake word.
    Uses partial_ratio so short wake phrases match within longer speech.
    
    Returns:
        Tuple[bool, str]: (is_wake_word_detected, detected_language)
        Language is 'hi' for Hindi, 'en' for English
    """
    if not text:
        return False, 'en'
    text = normalize(text)
    words = [normalize(w) for w in (wake_words or DEFAULT_WAKE_WORDS)]
    
    detected_word = None
    for w in words:
        if w in text:
            detected_word = w
            break
        if fuzz.partial_ratio(w, text) >= threshold:
            detected_word = w
            break
    
    if detected_word:
        # Check if it's a Hindi-specific wake word
        lang = 'hi' if detected_word in [normalize(hw) for hw in HINDI_SPECIFIC] else 'en'
        return True, lang
    
    return False, 'en'


def detect_language(text: str) -> str:
    """
    Detect if the text is primarily Hindi or English.
    
    Args:
        text: Input text to analyze
        
    Returns:
        'hi' for Hindi, 'en' for English
    """
    if not text:
        return 'en'
    
    # Common Hindi words/patterns (romanized and Devanagari)
    hindi_indicators = [
        'kya', 'hai', 'hoon', 'aap', 'mujhe', 'batao', 'karo', 'kaise',
        'kahan', 'kyun', 'kab', 'kaun', 'kitna', 'thik', 'achha', 'nahi',
        'haan', 'tum', 'tumhara', 'mera', 'mere', 'bol', 'bolo', 'suno',
        'sunao', 'dekho', 'karo', 'kar', 'raha', 'rahe', 'रहा', 'है', 'हूं',
        'आप', 'मुझे', 'बताओ', 'करो', 'कैसे', 'कहां', 'क्यों', 'कब'
    ]
    
    # Check for Devanagari script
    has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
    if has_devanagari:
        return 'hi'
    
    # Check for Hindi word indicators
    text_lower = text.lower()
    hindi_word_count = sum(1 for indicator in hindi_indicators if indicator in text_lower)
    
    # If multiple Hindi indicators found, classify as Hindi
    if hindi_word_count >= 2:
        return 'hi'
    
    return 'en'


__all__ = [
    "EN_WAKE_WORDS", "HI_WAKE_WORDS", "DEFAULT_WAKE_WORDS", "HINDI_SPECIFIC",
    "is_wake_word", "detect_language"
]
