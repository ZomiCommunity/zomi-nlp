"""Pure Zomi document implementation - no external dependencies."""

from collections.abc import Iterator
from typing import Any

from zomi_nlp.core.token import ZomiToken


class ZomiDoc:
    """Document representation - independent of any external library."""

    def __init__(self, text: str, lang: str = "zom"):
        self.text = text
        self.lang = lang
        self.tokens: list[ZomiToken] = []
        self.sentences: list[list[int]] = []  # List of token index ranges
        self.user_data: dict[str, Any] = {}

    def __len__(self) -> int:
        return len(self.tokens)

    def __getitem__(self, idx: int) -> ZomiToken:
        return self.tokens[idx]

    def __iter__(self) -> Iterator[ZomiToken]:
        return iter(self.tokens)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "text": self.text,
            "lang": self.lang,
            "tokens": [t.to_dict() for t in self.tokens],
            "sentences": self.sentences,
            "user_data": self.user_data
        }

    @property
    def text_with_annotations(self) -> str:
        """Debug view: show text with POS tags."""
        return " ".join([f"{t.text}/{t.pos_}" if t.pos_ else t.text for t in self.tokens])

    def get_sentence(self, sent_idx: int) -> list[ZomiToken]:
        """Get tokens for a specific sentence."""
        if sent_idx >= len(self.sentences):
            raise IndexError(f"Sentence index {sent_idx} out of range")
        start, end = self.sentences[sent_idx]
        return self.tokens[start:end]
