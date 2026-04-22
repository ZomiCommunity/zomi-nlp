"""Pure Zomi token implementation - no external dependencies"""

from typing import Dict, Any, Optional


class ZomiToken:
    """Token representation - independent of any external library"""
    
    def __init__(
        self,
        text: str,
        start_char: int,
        end_char: int,
        idx: int = 0,
        sent_idx: int = 0
    ):
        self.text = text
        self.start_char = start_char
        self.end_char = end_char
        self.idx = idx
        self.sent_idx = sent_idx
        
        # Linguistic annotations (will be filled by processors)
        self.pos_: Optional[str] = None
        self.tag_: Optional[str] = None
        self.lemma_: Optional[str] = None
        self.dep_: Optional[str] = None
        self.head: int = -1
        self.ent_type_: Optional[str] = None
        self.ent_iob_: Optional[str] = None
        self.morph: Dict[str, str] = {}
        
        # Zomi-specific
        self.is_clitic: bool = False
        self.clitic_type: Optional[str] = None  # "ve", "ta", "hiam", etc.
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return {
            "text": self.text,
            "start": self.start_char,
            "end": self.end_char,
            "idx": self.idx,
            "pos": self.pos_,
            "tag": self.tag_,
            "lemma": self.lemma_,
            "dep": self.dep_,
            "head": self.head,
            "ent_type": self.ent_type_,
            "ent_iob": self.ent_iob_,
            "morph": self.morph,
            "is_clitic": self.is_clitic,
            "clitic_type": self.clitic_type
        }
    
    def __repr__(self) -> str:
        return f"ZomiToken('{self.text}', pos={self.pos_}, lemma={self.lemma_})"
    
    @property
    def is_space(self) -> bool:
        return self.text.isspace()
    
    @property
    def is_punct(self) -> bool:
        return self.text in ".,!?;:()[]{}'\""