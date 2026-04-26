# zomi-nlp/zomi_nlp/pipeline/orchestrator.py
"""Main orchestrator for Zomi NLP pipeline with smart fallback."""

import logging
import warnings
from typing import Any, Optional

from zomi_nlp.config import ZomiConfig
from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.interfaces import NERBackend, ParserBackend, TaggerBackend, TokenizerBackend

logger = logging.getLogger(__name__)


class ZomiPipeline:
    """Main pipeline orchestrator for Zomi NLP."""

    def __init__(self, config: Optional[ZomiConfig] = None):
        self.config = config or ZomiConfig()
        self._setup_logging()

        # Backends
        self.tokenizer: Optional[TokenizerBackend] = None
        self.tagger: Optional[TaggerBackend] = None
        self.parser: Optional[ParserBackend] = None
        self.ner: Optional[NERBackend] = None

        # Track what's actually running
        self.active_backends: dict[str, str] = {}
        self.backend_warnings: list[str] = []

        self._initialize_backends()
        self._log_warnings()

    def _setup_logging(self):
        if self.config.verbose:
            logging.basicConfig(level=getattr(logging, self.config.log_level))

    def _initialize_backends(self):
        """Initialize backends with smart fallback."""
        # Tokenizer - prioritize native
        self.tokenizer = self._select_backend_with_fallback(
            task="tokenizer",
            requested=self.config.tokenizer_backend,
            backend_classes={
                "native": ("zomi_nlp.adapters.zomi_native_adapter", "ZomiTokenizer"),
                "spacy": ("zomi_nlp.adapters.spacy_adapter", "SpacyTokenizer"),
                "stanza": ("zomi_nlp.adapters.stanza_adapter", "StanzaTokenizer"),
            },
            fallback_order=["native", "stanza", "spacy"]
        )

        # Tagger - prioritize native
        self.tagger = self._select_backend_with_fallback(
            task="tagger",
            requested=self.config.tagger_backend,
            backend_classes={
                "native": ("zomi_nlp.adapters.zomi_native_adapter", "ZomiTagger"),
                "spacy": ("zomi_nlp.adapters.spacy_adapter", "SpacyTagger"),
                "stanza": ("zomi_nlp.adapters.stanza_adapter", "StanzaTagger"),
            },
            fallback_order=["native", "stanza", "spacy"]
        )

        # Parser - prioritize native
        self.parser = self._select_backend_with_fallback(
            task="parser",
            requested=self.config.parser_backend,
            backend_classes={
                "native": ("zomi_nlp.adapters.zomi_native_adapter", "ZomiParser"),
                "spacy": ("zomi_nlp.adapters.spacy_adapter", "SpacyParser"),
                "stanza": ("zomi_nlp.adapters.stanza_adapter", "StanzaParser"),
            },
            fallback_order=["native", "stanza", "spacy"]
        )

        # NER
        self.ner = self._select_backend_with_fallback(
            task="ner",
            requested=self.config.ner_backend,
            backend_classes={
                "spacy": ("zomi_nlp.adapters.spacy_adapter", "SpacyNER"),
                "stanza": ("zomi_nlp.adapters.stanza_adapter", "StanzaNER"),
            },
            fallback_order=["spacy", "stanza"]
        )

    def _select_backend_with_fallback(
        self,
        task: str,
        requested: str,
        backend_classes: dict[str, tuple],
        fallback_order: list[str]
    ):
        """Select backend with intelligent fallback."""
        # Case 1: User wants a specific backend
        if requested != "auto" and requested != "hybrid":
            backend = self._try_load_backend(task, requested, backend_classes)
            if backend and backend.is_available():
                self.active_backends[task] = requested
                return backend
            else:
                # User requested specific but unavailable
                error_msg = backend.get_error_message() if backend else \
                    f"{requested} backend unavailable"
                warning_msg = (
                    f"⚠️ {task.capitalize()}: Requested backend '{requested}' unavailable. "
                    f"Reason: {error_msg}. "
                    f"Falling back to auto-selection."
                )
                self.backend_warnings.append(warning_msg)
                warnings.warn(warning_msg, UserWarning, stacklevel=2)
                requested = "auto"  # Fall through to auto

        # Case 2: Auto-select (try fallback order)
        if requested == "auto" or requested == "hybrid":
            for backend_name in fallback_order:
                if backend_name in backend_classes:
                    backend = self._try_load_backend(task, backend_name, backend_classes)
                    if backend and backend.is_available():
                        self.active_backends[task] = backend_name
                        if backend_name != fallback_order[0]:
                            # Using fallback, warn user
                            warning_msg = (
                                f"ℹ️ {task.capitalize()}: Using '{backend_name}' as fallback "
                                f"(preferred '{fallback_order[0]}' not available). "
                                f"Install '{fallback_order[0]}' for better performance."
                            )
                            self.backend_warnings.append(warning_msg)
                            warnings.warn(warning_msg, UserWarning, stacklevel=2)
                        return backend

        # Case 3: No backend available
        if backend and not backend.is_available():
            error_msg = backend.get_error_message() \
                if backend else f"{requested} backend unavailable"

            # Check if it's a spaCy model issue specifically
            if requested == "spacy" and "model" in error_msg.lower():
                error_msg += "\n   → Fix: Run 'python -m spacy download en_core_web_sm'"

            warning_msg = (
                f"⚠️ {task.capitalize()}: Requested backend '{requested}' unavailable.\n"
                f"   Reason: {error_msg}\n"
                f"   Falling back to auto-selection.\n"
                f"   📖 See: https://github.com/ZomiCommunity/zomi-nlp#installation"
            )

        # Case 3: No backend available
        warning_msg = (
            f"❌ {task.capitalize()}: No backend available. "
            f"Install spaCy (pip install spacy) or stanza (pip install stanza). "
            f"Using simple fallback tokenizer."
        )
        self.backend_warnings.append(warning_msg)
        warnings.warn(warning_msg, UserWarning, stacklevel=2)
        self.active_backends[task] = "none"
        return None

    def _try_load_backend(self, task: str, backend_name: str, backend_classes: dict[str, tuple]):
        """Try to load a backend, return None if fails."""
        try:
            module_path, class_name = backend_classes[backend_name]

            # Dynamic import
            import importlib
            module = importlib.import_module(module_path)
            backend_class = getattr(module, class_name)

            # Instantiate with appropriate parameters
            if backend_name == "spacy":
                backend = backend_class(model_name="en_core_web_sm")
            elif backend_name == "stanza":
                backend = backend_class(lang="en")
            else:
                backend = backend_class()

            return backend
        except Exception as e:
            logger.debug(f"Failed to load {backend_name} for {task}: {e}")
            return None

    def _log_warnings(self):
        """Log collected warnings."""
        for warning in self.backend_warnings:
            logger.warning(warning)

    def __call__(self, text: str) -> ZomiDoc:
        """Process text through the pipeline."""
        doc = ZomiDoc(text)

        # Tokenization (required)
        if self.tokenizer:
            try:
                tokens = self.tokenizer.tokenize(text)
                if tokens:
                    doc.tokens = tokens
                else:
                    # Tokenizer returned empty - use fallback
                    doc.tokens = self._simple_tokenize(text)
                    if self.tokenizer.get_error_message() \
                          if hasattr(self.tokenizer, 'get_error_message') else False:
                        pass  # Already warned
            except Exception as e:
                logger.error(f"Tokenizer failed: {e}")
                doc.tokens = self._simple_tokenize(text)
        else:
            # No tokenizer available
            doc.tokens = self._simple_tokenize(text)

        # POS Tagging (optional)
        if self.tagger and doc.tokens:
            try:
                if self.tagger.is_available():
                    doc = self.tagger.tag(doc)
                else:
                    # Tagger not available but we have one - skip
                    pass
            except Exception as e:
                logger.debug(f"Tagger failed (non-fatal): {e}")

        # Dependency Parsing (optional)
        if self.parser and doc.tokens:
            try:
                if self.parser.is_available():
                    doc = self.parser.parse(doc)
            except Exception as e:
                logger.debug(f"Parser failed (non-fatal): {e}")

        # NER (optional)
        if self.ner and doc.tokens:
            try:
                if self.ner.is_available():
                    doc = self.ner.recognize(doc)
            except Exception as e:
                logger.debug(f"NER failed (non-fatal): {e}")

        return doc

    def _simple_tokenize(self, text: str) -> list:
        """Simple fallback tokenization that always works."""
        from zomi_nlp.core.token import ZomiToken
        tokens = []
        pos = 0

        for word in text.split():
            # Handle punctuation attached to words
            if word and word[-1] in ".,!?;:()[]{}'\"":
                # Split punctuation
                clean_word = word[:-1]
                punct = word[-1]
                if clean_word:
                    tokens.append(ZomiToken(clean_word, pos, pos + len(clean_word)))
                    pos += len(clean_word)
                tokens.append(ZomiToken(punct, pos, pos + 1))
                pos += 1
            else:
                tokens.append(ZomiToken(word, pos, pos + len(word)))
                pos += len(word) + 1

        return tokens

    def batch_process(self, texts: list[str]) -> list[ZomiDoc]:
        """Process multiple texts in batch."""
        return [self(text) for text in texts]

    def get_status(self) -> dict[str, Any]:
        """Get status of all backends."""
        return {
            "tokenizer": {
                "active": self.active_backends.get("tokenizer", "none"),
                "available": self.tokenizer.is_available() if self.tokenizer else False
            },
            "tagger": {
                "active": self.active_backends.get("tagger", "none"),
                "available": self.tagger.is_available() if self.tagger else False
            },
            "parser": {
                "active": self.active_backends.get("parser", "none"),
                "available": self.parser.is_available() if self.parser else False
            },
            "ner": {
                "active": self.active_backends.get("ner", "none"),
                "available": self.ner.is_available() if self.ner else False
            },
            "warnings": self.backend_warnings
        }

# """Main orchestrator for Zomi NLP pipeline"""

# import logging
# from typing import Optional, List
# from zomi_nlp.config import ZomiConfig, BackendMode
# from zomi_nlp.core.doc import ZomiDoc
# from zomi_nlp.interfaces import TokenizerBackend, TaggerBackend, ParserBackend, NERBackend

# logger = logging.getLogger(__name__)


# class ZomiPipeline:
#     """Main pipeline orchestrator for Zomi NLP"""

#     def __init__(self, config: Optional[ZomiConfig] = None):
#         self.config = config or ZomiConfig()
#         self._setup_logging()

#         # Backends
#         self.tokenizer: Optional[TokenizerBackend] = None
#         self.tagger: Optional[TaggerBackend] = None
#         self.parser: Optional[ParserBackend] = None
#         self.ner: Optional[NERBackend] = None

#         self._initialize_backends()

#     def _setup_logging(self):
#         if self.config.verbose:
#             logging.basicConfig(level=getattr(logging, self.config.log_level))

#     def _initialize_backends(self):
#         """Initialize backends based on configuration"""

#         # Tokenizer
#         if self.config.tokenizer_backend == "spacy":
#             from zomi_nlp.adapters.spacy_adapter import SpacyTokenizer
#             self.tokenizer = SpacyTokenizer()
#         elif self.config.tokenizer_backend == "stanza":
#             from zomi_nlp.adapters.stanza_adapter import StanzaTokenizer
#             self.tokenizer = StanzaTokenizer()
#         else:  # auto or hybrid
#             self.tokenizer = self._select_best_backend("tokenizer")

#         # Tagger
#         if self.config.tagger_backend == "spacy":
#             from zomi_nlp.adapters.spacy_adapter import SpacyTagger
#             self.tagger = SpacyTagger()
#         elif self.config.tagger_backend == "stanza":
#             from zomi_nlp.adapters.stanza_adapter import StanzaTagger
#             self.tagger = StanzaTagger()
#         else:
#             self.tagger = self._select_best_backend("tagger")

#         # Parser
#         if self.config.parser_backend == "spacy":
#             from zomi_nlp.adapters.spacy_adapter import SpacyParser
#             self.parser = SpacyParser()
#         elif self.config.parser_backend == "stanza":
#             from zomi_nlp.adapters.stanza_adapter import StanzaParser
#             self.parser = StanzaParser()
#         else:
#             self.parser = self._select_best_backend("parser")

#         # NER
#         if self.config.ner_backend == "spacy":
#             from zomi_nlp.adapters.spacy_adapter import SpacyNER
#             self.ner = SpacyNER()
#         elif self.config.ner_backend == "stanza":
#             from zomi_nlp.adapters.stanza_adapter import StanzaNER
#             self.ner = StanzaNER()
#         else:
#             self.ner = self._select_best_backend("ner")

#     def _select_best_backend(self, task: str):
#         """Auto-select the best available backend"""
#         backends = []

#         if task == "tokenizer":
#             from zomi_nlp.adapters.spacy_adapter import SpacyTokenizer
#             from zomi_nlp.adapters.stanza_adapter import StanzaTokenizer

#             spacy = SpacyTokenizer()
#             stanza = StanzaTokenizer()

#             if spacy.is_available():
#                 backends.append(("spacy", spacy))
#             if stanza.is_available():
#                 backends.append(("stanza", stanza))

#         # Return first available (priority order)
#         if backends:
#             logger.info(f"Selected {backends[0][0]} for {task}")
#             return backends[0][1]

#         logger.warning(f"No backend available for {task}")
#         return None

#     def __call__(self, text: str) -> ZomiDoc:
#         """Process text through the pipeline"""
#         doc = ZomiDoc(text)

#         # Tokenization
#         if self.tokenizer:
#             try:
#                 doc.tokens = self.tokenizer.tokenize(text)
#             except Exception as e:
#                 logger.error(f"Tokenizer failed: {e}")
#                 if not self.config.fallback_enabled:
#                     raise
#                 # Fallback to simple whitespace tokenization
#                 doc.tokens = self._simple_tokenize(text)

#         # POS Tagging
#         if self.tagger and doc.tokens:
#             try:
#                 doc = self.tagger.tag(doc)
#             except Exception as e:
#                 logger.error(f"Tagger failed: {e}")

#         # Dependency Parsing
#         if self.parser and doc.tokens:
#             try:
#                 doc = self.parser.parse(doc)
#             except Exception as e:
#                 logger.error(f"Parser failed: {e}")

#         # NER
#         if self.ner and doc.tokens:
#             try:
#                 doc = self.ner.recognize(doc)
#             except Exception as e:
#                 logger.error(f"NER failed: {e}")

#         return doc

#     def _simple_tokenize(self, text: str) -> List:
#         """Simple fallback tokenization"""
#         from zomi_nlp.core.token import ZomiToken
#         tokens = []
#         pos = 0

#         for word in text.split():
#             tokens.append(ZomiToken(word, pos, pos + len(word)))
#             pos += len(word) + 1

#         return tokens

#     def batch_process(self, texts: List[str]) -> List[ZomiDoc]:
#         """Process multiple texts in batch"""
#         return [self(text) for text in texts]
