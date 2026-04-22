"""Stanza adapter for Zomi NLP."""


import importlib

from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.core.token import ZomiToken
from zomi_nlp.interfaces import NERBackend, ParserBackend, TaggerBackend, TokenizerBackend


class StanzaTokenizer(TokenizerBackend):
    """Tokenizer using Stanza."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._nlp = None
        self._name = f"stanza_{lang}"

    def _load(self):
        if self._nlp is None:
            try:
                import stanza
                stanza.download(self.lang, quiet=True)
                self._nlp = stanza.Pipeline(self.lang, processors="tokenize", use_gpu=False)
            except ImportError as e:
                raise ImportError("stanza not installed.  Run: pip install stanza") from e

    def tokenize(self, text: str) -> list[ZomiToken]:
        self._load()
        stanza_doc = self._nlp(text)
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
        return importlib.util.find_spec("stanza") is not None


class StanzaTagger(TaggerBackend):
    """POS Tagger using Stanza."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._nlp = None

    def _load(self):
        if self._nlp is None:
            try:
                import stanza
                stanza.download(self.lang, quiet=True)
                self._nlp = stanza.Pipeline(self.lang, processors="tokenize,pos", use_gpu=False)
            except ImportError as e:
                raise ImportError("stanza not installed.  Run: pip install stanza") from e

    def tag(self, doc: ZomiDoc) -> ZomiDoc:
        self._load()
        stanza_doc = self._nlp(doc.text)
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
        return importlib.util.find_spec("stanza") is not None


class StanzaParser(ParserBackend):
    """Dependency Parser using Stanza."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._nlp = None

    def _load(self):
        if self._nlp is None:
            try:
                import stanza
                stanza.download(self.lang, quiet=True)
                self._nlp = stanza.Pipeline(
                    self.lang, processors="tokenize,pos,depparse", use_gpu=False)
            except ImportError as e:
                raise ImportError("stanza not installed.  Run: pip install stanza") from e

    def parse(self, doc: ZomiDoc) -> ZomiDoc:
        self._load()
        stanza_doc = self._nlp(doc.text)
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
        return importlib.util.find_spec("stanza") is not None

class StanzaNER(NERBackend):
    """NER using Stanza."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._nlp = None

    def _load(self):
        if self._nlp is None:
            try:
                import stanza
                stanza.download(self.lang, quiet=True)
                self._nlp = stanza.Pipeline(self.lang, processors="tokenize,ner", use_gpu=False)
            except ImportError as e:
                raise ImportError("stanza not installed.  Run: pip install stanza") from e

    def recognize(self, doc: ZomiDoc) -> ZomiDoc:
        self._load()
        stanza_doc = self._nlp(doc.text)

        for sentence in stanza_doc.sentences:
            for ent in sentence.ents:
                # Mark tokens in this entity
                for _i in range(ent.start_char, ent.end_char):
                    # Simplified - would need proper alignment
                    pass

        return doc

    def name(self) -> str:
        return f"stanza_{self.lang}"

    def is_available(self) -> bool:
        return importlib.util.find_spec("stanza") is not None
