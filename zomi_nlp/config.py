"""Configuration management for Zomi NLP"""

from dataclasses import dataclass, field
from typing import Optional, Literal

BackendMode = Literal["auto", "spacy", "stanza", "hybrid", "none"]


@dataclass
class ZomiConfig:
    """Configuration for Zomi NLP pipeline"""
    
    # Model settings
    model_name: str = "auto"
    
    # Backend selection - default to auto for smooth experience
    tokenizer_backend: BackendMode = "auto"
    tagger_backend: BackendMode = "auto"
    parser_backend: BackendMode = "auto"
    ner_backend: BackendMode = "auto"
    
    # Fallback settings
    fallback_enabled: bool = True
    fallback_chain: list = field(default_factory=lambda: ["stanza", "spacy", "native"])
    strict_mode: bool = False  # If True, raise errors instead of falling back
    
    # Performance
    batch_size: int = 100
    use_gpu: bool = False
    
    # Logging
    verbose: bool = True  # Show warnings by default
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.model_name == "auto":
            self.model_name = "zomi_sm"
        
        # In strict mode, disable fallback
        if self.strict_mode:
            self.fallback_enabled = False