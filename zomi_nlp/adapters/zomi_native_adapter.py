# zomi_nlp/adapters/zomi_native_adapter.py
"""Adapter for ZomiRuleBasedParser native backend."""

from typing import Optional

from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.core.token import ZomiToken
from zomi_nlp.interfaces.backends import ParserBackend
from zomi_nlp.native import ZomiRuleBasedParser


class ZomiParser(ParserBackend):
    """Backend adapter for ZomiParser.

    Mapping from parser output to ZomiToken:
    - form      → text
    - lemma     → lemma_
    - tag       → pos_
    - deprel    → dep_
    - head      → head
    """

    def __init__(self):
        self.parser = ZomiRuleBasedParser()
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
