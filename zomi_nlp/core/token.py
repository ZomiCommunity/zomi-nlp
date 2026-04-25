# zomi_nlp/core/token.py
"""Pure Zomi token implementation - no external dependencies."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ZomiToken:
    """Token representation - independent of any external library."""

    # Core token attributes
    text: str
    start_char: int
    end_char: int
    idx: int = 0
    sent_idx: int = 0

    # CoNLL-U style fields (optional, for direct mapping)
    form: str = ""  # Alias for text
    lemma: Optional[str] = None
    upos: Optional[str] = None  # Universal POS (instead of pos_)
    xpos: Optional[str] = None   # Treebank-specific POS
    feats: Optional[str] = None  # Morphological features
    head: int = -1
    deprel: Optional[str] = None
    deps: Optional[str] = None
    misc: Optional[str] = None

    # Linguistic annotations (will be filled by processors)
    pos_: Optional[str] = None
    tag_: Optional[str] = None
    lemma_: Optional[str] = None
    dep_: Optional[str] = None
    ent_type_: Optional[str] = None
    ent_iob_: Optional[str] = None
    morph: dict[str, str] = field(default_factory=dict)

    # Zomi-specific
    is_clitic: bool = False
    clitic_type: Optional[str] = None  # "ve", "ta", "hiam", etc.

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
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
