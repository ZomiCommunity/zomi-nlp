"""Interfaces for Zomi NLP backends"""

from zomi_nlp.interfaces.backends import (
    TokenizerBackend,
    TaggerBackend,
    ParserBackend,
    NERBackend,
)

__all__ = [
    "TokenizerBackend",
    "TaggerBackend",
    "ParserBackend",
    "NERBackend",
]
