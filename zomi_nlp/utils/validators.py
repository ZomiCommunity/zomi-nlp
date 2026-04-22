"""Validation utilities for Zomi NLP"""

from typing import List, Optional
import re


def validate_zomi_text(text: str) -> bool:
    """
    Validate if text contains valid Zomi characters.
    
    Zomi uses Roman alphabet with possible diacritics.
    
    Args:
        text: Text to validate
    
    Returns:
        True if text contains only valid Zomi characters
    """
    # Zomi character set: a-z with diacritics, spaces, punctuation
    pattern = r'^[a-zA-Z\s\.\,\!\?\;\:\'\"\(\)\[\]\{\}àáâãäåèéêëìíîïòóôõöùúûüýÿçñ\-]+$'
    return bool(re.match(pattern, text.strip())) if text.strip() else True


def normalize_zomi_text(text: str, lowercase: bool = True) -> str:
    """
    Normalize Zomi text for processing.
    
    Args:
        text: Input text
        lowercase: Convert to lowercase
    
    Returns:
        Normalized text
    """
    if lowercase:
        text = text.lower()
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace("'", "'").replace("'", "'")
    
    return text


def detect_zomi_dialect(text: str) -> str:
    """
    Detect which Zomi dialect the text uses.
    
    Args:
        text: Zomi text
    
    Returns:
        Dialect name: "tedim", "falam", "zo", or "unknown"
    """
    # This is a simplified placeholder
    # Real implementation would use ML or statistical methods
    
    tedim_markers = ['ve', 'ta', 'hiam', 'maw']
    falam_markers = ['veh', 'tah', 'hiam', 'maw']
    zo_markers = ['ve', 'ta', 'he', 'mo']
    
    text_lower = text.lower()
    
    tedim_count = sum(1 for m in tedim_markers if m in text_lower)
    falam_count = sum(1 for m in falam_markers if m in text_lower)
    zo_count = sum(1 for m in zo_markers if m in text_lower)
    
    scores = {"tedim": tedim_count, "falam": falam_count, "zo": zo_count}
    best = max(scores, key=scores.get)
    
    return best if scores[best] > 0 else "unknown"