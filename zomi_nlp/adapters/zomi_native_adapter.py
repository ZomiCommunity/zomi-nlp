# zomi_nlp/adapters/zomi_native_adapter.py
"""Adapter for Zomi native backends."""

from typing import Optional

from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.core.token import ZomiToken
from zomi_nlp.interfaces.backends import ParserBackend, TaggerBackend, TokenizerBackend
from zomi_nlp.native import ZomiRuleBasedParser
from zomi_nlp.native.tagger import ZomiTaggerBackend
from zomi_nlp.native.tokenizer import ZomiTokenizer


class ZomiParserAdapter(ParserBackend):
    """Backend adapter for ZomiParser.

    Mapping from parser output to ZomiToken:
    - form      → text
    - lemma     → lemma_
    - tag       → pos_
    - deprel    → dep_
    - head      → head
    """

    def __init__(self):
        self.parser: ZomiRuleBasedParser = ZomiRuleBasedParser() # This parser does tagging too
        self._name: str = self.parser.__class__.__name__.lower()
        self._available: bool = True

    def parse(self, doc: ZomiDoc) -> ZomiDoc:
        """Parse text using ZomiParser."""
        # Annotate parser output
        result = self.parser.parse(doc.text)

        # Convert to ZomiDoc tokens
        for token_data in result:
            token = ZomiToken(
                text=token_data.get('form', ''),
                start_char=0,
                end_char=0,
                idx=len(doc.tokens),
                lemma_=token_data.get('lemma', ''),
                pos_=token_data.get('tag', ''),
                dep_=token_data.get('deprel', ''),
                head=token_data.get('head', 0),
            )
            doc.tokens.append(token)

        return doc

    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return self._available

    def get_error_message(self) -> Optional[str]:
        return None if self._available else "ZomiParser not available"


class ZomiTokenizerAdapter(TokenizerBackend):
    """Tokenizer adapter using native ZomiTokenizer.

    Mapping from tokenizer output to ZomiToken:
    - token text → text
    - start_char → start_char
    - end_char → end_char
    """

    def __init__(self, split_clitics: bool = True, split_punct: bool = True):
        self.tokenizer: ZomiTokenizer = ZomiTokenizer(
            split_clitics=split_clitics,
            split_punct=split_punct
        )
        self._name: str = "zomi_tokenizer"
        self._available: bool = True
        self.split_clitics: bool = split_clitics
        self.split_punct: bool = split_punct

    def tokenize(self, text: str) -> list[ZomiToken]:
        """Tokenize text using native Zomi tokenizer."""
        if not text:
            return []

        # Get tokens with spans
        token_spans = self.tokenizer.tokenize_with_spans(text)

        # Convert to ZomiTokens
        zomi_tokens = []
        for idx, (token_text, start, end) in enumerate(token_spans):
            token = ZomiToken(
                text=token_text,
                start_char=start,
                end_char=end,
                idx=idx,
                # Tokenizer doesn't provide linguistic annotations yet
                pos_=None,
                lemma_=None,
                dep_=None,
                head=-1,
            )

            # Zomi-specific flags
            token.is_clitic = self._is_clitic(token_text)
            token.clitic_type = self._get_clitic_type(token_text) if token.is_clitic else None

            zomi_tokens.append(token)

        return zomi_tokens

    def _is_clitic(self, token: str) -> bool:
        """Check if token is a known Zomi clitic."""
        from zomi_nlp.native.tokenizer import CliticSplitter
        # Clitics are the ones that would be split off
        clitic_splitter = CliticSplitter()
        # If token is in clitic list, it's a clitic
        return token.lower() in clitic_splitter.sorted_clitics

    def _get_clitic_type(self, token: str) -> Optional[str]:
        """Get clitic type."""
        clitic_map = {
            "ve": "polite", "veh": "polite",
            "ta": "emphatic", "tae": "emphatic",
            "hiam": "question", "maw": "question",
            "le": "conditional", "leh": "conditional",
            "pah": "temporal", "sawn": "temporal",
            "ngei": "perfective", "khin": "perfective",
            "kei": "negative", "loin": "negative",
            "hen": "imperative",
            "uh": "plural",
            "hi": "copular",
        }
        return clitic_map.get(token.lower())

    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return self._available

    def get_error_message(self) -> Optional[str]:
        return None if self._available else "Native tokenizer not available"


class ZomiTaggerAdapter(TaggerBackend):
    """Tagger adapter using native ZomiPOSTagger."""

    def __init__(self):
        self.tagger: ZomiTaggerBackend = ZomiTaggerBackend()
        self._name: str = "zomi_tagger"
        self._available: bool = True

    def tag(self, doc: ZomiDoc) -> ZomiDoc:
        """Tag tokens in a ZomiDoc."""
        return self.tagger.tag(doc)

    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return self._available

    def get_error_message(self) -> Optional[str]:
        return None if self._available else "Zomi tagger not available"

# Alias for backward compatibility
# ZomiNativeBackend = ZomiParseradapter
# ZomiTokenizerBackend = ZomiTokenizerAdapter
# ZomiTaggerBackend = ZomiTaggerAdapter
