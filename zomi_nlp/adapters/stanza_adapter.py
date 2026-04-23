"""Stanza adapter for Zomi NLP."""

from importlib.util import find_spec
from typing import Optional

from zomi_nlp.adapters.stanza_shared import _stanza_shared
from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.core.token import ZomiToken
from zomi_nlp.interfaces import NERBackend, ParserBackend, TaggerBackend, TokenizerBackend


class StanzaTokenizer(TokenizerBackend):
    """Tokenizer using Stanza."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._name = f"stanza_{lang}"
        self._available: Optional[bool] = None
        self._error_message: Optional[str] = None

    def _check_availability(self) -> bool:
        """Check if stanza is available and return status."""
        if self._available is not None:
            return self._available

        if find_spec("stanza") is not None:
            self._available = True
            self._error_message = None
        else:
            self._available = False
            self._error_message = "stanza not installed. Run: pip install stanza"

        return self._available

    def tokenize(self, text: str) -> list[ZomiToken]:
        if not self._check_availability():
            return []

        nlp = _stanza_shared.get_pipeline(self.lang, processors="tokenize")

        stanza_doc = nlp(text)
        tokens = []
        idx = 0

        for sentence in stanza_doc.sentences:
            for word in sentence.words:
                zomi_token = ZomiToken(
                    text=word.text,
                    start_char=word.start_char or 0,
                    end_char=word.end_char or (word.start_char or 0) + len(word.text),
                    idx=idx
                )
                # Map Stanza annotations
                if hasattr(word, 'upos'):
                    zomi_token.pos_ = word.upos
                if hasattr(word, 'xpos'):
                    zomi_token.tag_ = word.xpos
                if hasattr(word, 'lemma'):
                    zomi_token.lemma_ = word.lemma
                if hasattr(word, 'deprel'):
                    zomi_token.dep_ = word.deprel
                if hasattr(word, 'head'):
                    zomi_token.head = word.head - 1 if word.head else -1

                tokens.append(zomi_token)
                idx += 1

        return tokens

    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return self._check_availability()

    def get_error_message(self) -> Optional[str]:
        """Get error message if backend unavailable."""
        self._check_availability()
        return self._error_message


class StanzaTagger(TaggerBackend):
    """POS Tagger using Stanza."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._available: Optional[bool] = None
        self._error_message: Optional[str] = None

    def _check_availability(self) -> bool:
        if self._available is not None:
            return self._available

        if find_spec("stanza") is not None:
            self._available = True
            self._error_message = None
        else:
            self._available = False
            self._error_message = "stanza not installed. Run: pip install stanza"

        return self._available

    def tag(self, doc: ZomiDoc) -> ZomiDoc:
        if not self._check_availability():
            return doc

        nlp = _stanza_shared.get_pipeline(self.lang, processors="tokenize,pos,lemma")
        stanza_doc = nlp(doc.text)
        idx = 0

        for sentence in stanza_doc.sentences:
            for word in sentence.words:
                if idx < len(doc.tokens):
                    if hasattr(word, 'upos'):
                        doc.tokens[idx].pos_ = word.upos
                    if hasattr(word, 'xpos'):
                        doc.tokens[idx].tag_ = word.xpos
                    if hasattr(word, 'lemma'):
                        doc.tokens[idx].lemma_ = word.lemma
                idx += 1

        return doc

    def name(self) -> str:
        return f"stanza_{self.lang}"

    def is_available(self) -> bool:
        return self._check_availability()

    def get_error_message(self) -> Optional[str]:
        """Get error message if backend unavailable."""
        self._check_availability()
        return self._error_message


class StanzaParser(ParserBackend):
    """Dependency Parser using Stanza."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._available: Optional[bool] = None
        self._error_message: Optional[str] = None

    def _check_availability(self) -> bool:
        if self._available is not None:
            return self._available

        if find_spec("stanza") is not None:
            self._available = True
            self._error_message = None
        else:
            self._available = False
            self._error_message = "stanza not installed. Run: pip install stanza"

        return self._available

    def parse(self, doc: ZomiDoc) -> ZomiDoc:
        if not self._check_availability():
            return doc

        nlp = _stanza_shared.get_pipeline(self.lang, processors="tokenize,pos,lemma,depparse")
        stanza_doc = nlp(doc.text)
        idx = 0

        for sentence in stanza_doc.sentences:
            for word in sentence.words:
                if idx < len(doc.tokens):
                    if hasattr(word, 'deprel'):
                        doc.tokens[idx].dep_ = word.deprel
                    if hasattr(word, 'head'):
                        doc.tokens[idx].head = word.head - 1 if word.head else -1
                idx += 1

        return doc

    def name(self) -> str:
        return f"stanza_{self.lang}"

    def is_available(self) -> bool:
        return self._check_availability()

    def get_error_message(self) -> Optional[str]:
        """Get error message if backend unavailable."""
        self._check_availability()
        return self._error_message


class StanzaNER(NERBackend):
    """NER using Stanza."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._available: Optional[bool] = None
        self._error_message: Optional[str] = None

    def _check_availability(self) -> bool:
        if self._available is not None:
            return self._available

        if find_spec("stanza") is not None:
            self._available = True
            self._error_message = None
        else:
            self._available = False
            self._error_message = "stanza not installed. Run: pip install stanza"

        return self._available

    def recognize(self, doc: ZomiDoc) -> ZomiDoc:
        if not self._check_availability():
            return doc

        # Use shared pipeline with ner processor
        nlp = _stanza_shared.get_pipeline(self.lang, processors="tokenize,ner")
        stanza_doc = nlp(doc.text)

        for sentence in stanza_doc.sentences:
            for ent in sentence.ents:
                # Mark tokens in this entity range
                for token in doc.tokens:
                    if token.start_char >= ent.start_char and token.end_char <= ent.end_char:
                        token.ent_type_ = ent.type
                        token.ent_iob_ = "B" if token.start_char == ent.start_char else "I"

        return doc

    def name(self) -> str:
        return f"stanza_{self.lang}"

    def is_available(self) -> bool:
        return self._check_availability()

    def get_error_message(self) -> Optional[str]:
        """Get error message if backend unavailable."""
        self._check_availability()
        return self._error_message
