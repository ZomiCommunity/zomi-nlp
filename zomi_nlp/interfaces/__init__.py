"""Interfaces for Zomi NLP backends."""

from zomi_nlp.interfaces.backends import (
    NERBackend,
    ParserBackend,
    TaggerBackend,
    TokenizerBackend,
)

__all__ = [
    "TokenizerBackend",
    "TaggerBackend",
    "ParserBackend",
    "NERBackend",
]
