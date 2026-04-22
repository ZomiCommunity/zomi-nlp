"""spaCy adapter for Zomi NLP with improved error handling."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from spacy.language import Language

from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.core.token import ZomiToken
from zomi_nlp.interfaces import NERBackend, ParserBackend, TaggerBackend, TokenizerBackend


class SpacyTokenizer(TokenizerBackend):
    """Tokenizer using spaCy - graceful failure if not installed."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name: str = model_name
        self._nlp: Optional[Language] = None
        self._name: str = f"spacy_{model_name}"
        self._available: Optional[bool] = None
        self._error_message: Optional[str] = None

    def _check_availability(self) -> bool:
        """Check if spaCy is available and return status."""
        if self._available is not None:
            return self._available

        try:
            import spacy
            # Try to load model
            try:
                self._nlp = spacy.load(self.model_name)
                self._available = True
                self._error_message = None
            except OSError:
                # Model not downloaded
                self._available = False
                self._error_message = (
                    f"spaCy model '{self.model_name}' not found. "
                    f"Run: python -m spacy download {self.model_name}"
                )
        except ImportError:
            self._available = False
            self._error_message = (
                "spaCy not installed. "
                "Run: pip install spacy"
            )

        return self._available

    def _load(self):
        """Lazy load spaCy model with proper error handling."""
        if self._nlp is None and self._check_availability():
            import spacy
            self._nlp = spacy.load(self.model_name)

    def tokenize(self, text: str) -> list[ZomiToken]:
        if not self._check_availability():
            # Return empty list - caller should handle fallback
            return []

        self._load()
        if self._nlp is None:
            raise RuntimeError("Pipeline not initialized")
        spacy_doc = self._nlp(text)
        tokens = []

        for idx, token in enumerate(spacy_doc):
            zomi_token = ZomiToken(
                text=token.text,
                start_char=token.idx,
                end_char=token.idx + len(token.text),
                idx=idx
            )
            # Map spaCy annotations
            zomi_token.pos_ = self._map_pos(token.pos_)
            zomi_token.tag_ = token.tag_
            zomi_token.lemma_ = token.lemma_
            zomi_token.dep_ = token.dep_
            zomi_token.head = token.head.i if token.head else -1

            # Map entity annotations
            if token.ent_type_:
                zomi_token.ent_type_ = token.ent_type_
                zomi_token.ent_iob_ = token.ent_iob_

            tokens.append(zomi_token)

        return tokens

    def _map_pos(self, spacy_pos: str) -> str:
        """Map spaCy POS tags to Universal Dependencies."""
        mapping = {
            "NOUN": "NOUN", "VERB": "VERB", "ADJ": "ADJ", "ADV": "ADV",
            "ADP": "ADP", "CONJ": "CONJ", "DET": "DET", "PRON": "PRON",
            "PUNCT": "PUNCT", "NUM": "NUM", "PART": "PART", "SCONJ": "SCONJ",
            "PROPN": "PROPN", "SYM": "SYM", "INTJ": "INTJ", "X": "X"
        }
        return mapping.get(spacy_pos, "X")

    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return self._check_availability()

    def get_error_message(self) -> Optional[str]:
        """Get error message if backend unavailable."""
        self._check_availability()
        return self._error_message


class SpacyTagger(TaggerBackend):
    """POS Tagger using spaCy - graceful failure."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name: str = model_name
        self._nlp: Optional[Language] = None
        self._available: Optional[bool] = None
        self._error_message: Optional[str] = None

    def _check_availability(self) -> bool:
        if self._available is not None:
            return self._available

        try:
            import spacy
            try:
                self._nlp = spacy.load(self.model_name)
                self._available = True
            except OSError:
                self._available = False
                self._error_message = f"Model '{self.model_name}' not found. \
                Run: python -m spacy download {self.model_name}"
        except ImportError:
            self._available = False
            self._error_message = "spaCy not installed. Run: pip install spacy"

        return self._available

    def _load(self):
        if self._nlp is None and self._check_availability():
            import spacy
            self._nlp = spacy.load(self.model_name)

    def tag(self, doc: ZomiDoc) -> ZomiDoc:
        if not self._check_availability() or not doc.tokens:
            return doc

        self._load()
        assert self._nlp is not None, "Pipeline not initialized"
        spacy_doc = self._nlp(doc.text)

        for idx, token in enumerate(spacy_doc):
            if idx < len(doc.tokens):
                doc.tokens[idx].pos_ = self._map_pos(token.pos_)
                doc.tokens[idx].tag_ = token.tag_
                doc.tokens[idx].lemma_ = token.lemma_

        return doc

    def _map_pos(self, spacy_pos: str) -> str:
        mapping = {
            "NOUN": "NOUN", "VERB": "VERB", "ADJ": "ADJ", "ADV": "ADV",
            "ADP": "ADP", "CONJ": "CONJ", "DET": "DET", "PRON": "PRON",
            "PUNCT": "PUNCT", "NUM": "NUM", "PART": "PART", "SCONJ": "SCONJ",
            "PROPN": "PROPN", "SYM": "SYM", "INTJ": "INTJ", "X": "X"
        }
        return mapping.get(spacy_pos, "X")

    def name(self) -> str:
        return f"spacy_{self.model_name}"

    def is_available(self) -> bool:
        return self._check_availability()

    def get_error_message(self) -> Optional[str]:
        self._check_availability()
        return self._error_message


class SpacyParser(ParserBackend):
    """Dependency Parser using spaCy - graceful failure."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name: str = model_name
        self._nlp: Optional[Language] = None
        self._available: Optional[bool] = None
        self._error_message: Optional[str] = None

    def _check_availability(self) -> bool:
        if self._available is not None:
            return self._available

        try:
            import spacy
            try:
                self._nlp = spacy.load(self.model_name)
                self._available = True
            except OSError:
                self._available = False
                self._error_message = f"Model '{self.model_name}' not found"
        except ImportError:
            self._available = False
            self._error_message = "spaCy not installed"

        return self._available

    def _load(self):
        if self._nlp is None and self._check_availability():
            import spacy
            self._nlp = spacy.load(self.model_name)

    def parse(self, doc: ZomiDoc) -> ZomiDoc:
        if not self._check_availability() or not doc.tokens:
            return doc

        self._load()
        assert self._nlp is not None, "Pipeline not initialized"
        spacy_doc = self._nlp(doc.text)

        for idx, token in enumerate(spacy_doc):
            if idx < len(doc.tokens):
                doc.tokens[idx].dep_ = token.dep_
                doc.tokens[idx].head = token.head.i if token.head else -1

        return doc

    def name(self) -> str:
        return f"spacy_{self.model_name}"

    def is_available(self) -> bool:
        return self._check_availability()

    def get_error_message(self) -> Optional[str]:
        self._check_availability()
        return self._error_message


class SpacyNER(NERBackend):
    """NER using spaCy - graceful failure."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name: str = model_name
        self._nlp: Optional[Language] = None
        self._available: Optional[bool] = None
        self._error_message: Optional[str] = None

    def _check_availability(self) -> bool:
        if self._available is not None:
            return self._available

        try:
            import spacy
            try:
                self._nlp = spacy.load(self.model_name)
                self._available = True
            except OSError:
                self._available = False
                self._error_message = f"Model '{self.model_name}' not found"
        except ImportError:
            self._available = False
            self._error_message = "spaCy not installed"

        return self._available

    def _load(self):
        if self._nlp is None and self._check_availability():
            import spacy
            self._nlp = spacy.load(self.model_name)

    def recognize(self, doc: ZomiDoc) -> ZomiDoc:
        if not self._check_availability() or not doc.tokens:
            return doc

        self._load()
        assert self._nlp is not None, "Pipeline not initialized"
        spacy_doc = self._nlp(doc.text)

        for idx, token in enumerate(spacy_doc):
            if idx < len(doc.tokens) and token.ent_type_:
                doc.tokens[idx].ent_type_ = token.ent_type_
                doc.tokens[idx].ent_iob_ = token.ent_iob_

        return doc

    def name(self) -> str:
        return f"spacy_{self.model_name}"

    def is_available(self) -> bool:
        return self._check_availability()

    def get_error_message(self) -> Optional[str]:
        self._check_availability()
        return self._error_message
