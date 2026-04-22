"""Base interfaces for Zomi NLP backends"""

from abc import ABC, abstractmethod
from typing import List

from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.core.token import ZomiToken


class TokenizerBackend(ABC):
    """Base interface for tokenizer backends"""

    @abstractmethod
    def tokenize(self, text: str) -> List[ZomiToken]:
        """Tokenize text into ZomiToken objects"""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of this backend"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available (dependencies installed)"""
        pass


class TaggerBackend(ABC):
    """Base interface for POS tagger backends"""

    @abstractmethod
    def tag(self, doc: ZomiDoc) -> ZomiDoc:
        """Add POS tags to document tokens"""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of this backend"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available (dependencies installed)"""
        pass


class ParserBackend(ABC):
    """Base interface for dependency parser backends"""

    @abstractmethod
    def parse(self, doc: ZomiDoc) -> ZomiDoc:
        """Parse document and add dependency relations"""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of this backend"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available (dependencies installed)"""
        pass


class NERBackend(ABC):
    """Base interface for Named Entity Recognition backends"""

    @abstractmethod
    def recognize(self, doc: ZomiDoc) -> ZomiDoc:
        """Recognize named entities in document"""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of this backend"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available (dependencies installed)"""
        pass
