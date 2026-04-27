# zomi-nlp/zomi_nlp/native/tagger.py
"""Zomi-native POS tagger using lexicon lookup and rule-based heuristics."""

from typing import Optional

from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.native.lexicons import ZOMI_LEXICON, ZOMI_SUFFIXES
from zomi_nlp.native.tokenizer import ZomiTokenizer


class ZomiPOSTagger:
    """POS tagger for Zomi language using lexicon + heuristics.

    Features:
    - Lexicon lookup for known words (600+ entries)
    - Suffix/particle tagging
    - Heuristic fallback based on word patterns
    - Context-aware tagging for ambiguous words
    """

    # Default tag for unknown words
    DEFAULT_TAG = "NOUN"

    # Word pattern heuristics
    PATTERN_RULES: list[tuple[str, str]] = [
        (r'.*ve$', "PART"),      # Words ending in 've' are often particles
        (r'.*ta$', "PART"),      # Words ending in 'ta' are often particles
        (r'.*hiam$', "PART"),    # Question particles
        (r'.*maw$', "PART"),     # Question particles
        (r'.*leh$', "CCONJ"),    # Conditional conjunctions
        (r'^[A-Z][a-z]+$', "PROPN"),  # Capitalized words may be proper nouns
        (r'^[0-9]+$', "NUM"),    # Numbers
    ]

    def __init__(self, tokenizer: Optional[ZomiTokenizer] = None) -> None:
        """Initialize tagger.

        Args:
            tokenizer: Optional tokenizer instance. If not provided, creates new one.
        """
        self.lexicon: dict[str, dict[str, str]] = ZOMI_LEXICON.copy()
        self.suffix_table: dict[str, dict[str, str]] = ZOMI_SUFFIXES.copy()
        self.tokenizer: ZomiTokenizer = tokenizer or ZomiTokenizer()

    def tag(self, tokens: list[str]) -> list[tuple[str, str, Optional[str]]]:
        """Tag a list of tokens.

        Args:
            tokens: List of token strings

        Returns:
            List of (token, pos_tag, features) tuples
        """
        results: list[tuple[str, str, Optional[str]]] = []
        for token in tokens:
            tag, feats = self._tag_single(token)
            results.append((token, tag, feats))
        return results

    def _tag_single(self, token: str) -> tuple[str, Optional[str]]:
        """Tag a single token.

        Returns:
            Tuple of (pos_tag, features)
        """
        token_lower = token.lower()

        # 1. Check lexicon
        if token_lower in self.lexicon:
            entry = self.lexicon[token_lower]
            return entry.get('upos', self.DEFAULT_TAG), entry.get('feats')

        # 2. Check suffix table (particles, auxiliaries)
        if token_lower in self.suffix_table:
            entry = self.suffix_table[token_lower]
            return entry.get('upos', 'PART'), entry.get('feats')

        # 3. Apply pattern heuristics
        for pattern, tag in self.PATTERN_RULES:
            import re
            if re.match(pattern, token):
                return tag, None

        # 4. Check for numbers
        if token.isdigit():
            return "NUM", "NumType=Card"

        # 5. Check for punctuation
        if token in ".,!?;:()[]{}'\"":
            return "PUNCT", None

        # 6. Default fallback
        return self.DEFAULT_TAG, None

    def tag_with_context(self, tokens: list[str]) -> list[tuple[str, str, Optional[str]]]:
        """Tag tokens with context awareness for ambiguous cases.

        Args:
            tokens: List of token strings

        Returns:
            List of (token, pos_tag, features) tuples
        """
        # First, tag individually
        tags: list[tuple[str, Optional[str]]] = [self._tag_single(t) for t in tokens]

        # Apply context rules
        for i, (token, (_tag, _feats)) in enumerate(zip(tokens, tags)):
            # Rule 1: 'ka' before a verb is likely PRON (not NOUN)
            if token.lower() == 'ka' and i + 1 < len(tokens):
                next_tag, _ = tags[i + 1]
                if next_tag == 'VERB':
                    tags[i] = ('PRON', 'Number=Sing|Person=1|PronType=Prs')

            # Rule 2: 'na' before a verb is likely PRON
            elif token.lower() == 'na' and i + 1 < len(tokens):
                next_tag, _ = tags[i + 1]
                if next_tag == 'VERB':
                    tags[i] = ('PRON', 'Number=Sing|Person=2|PronType=Prs')

            # Rule 3: 'pen' as topic marker
            elif token.lower() == 'pen' and i + 1 < len(tokens):
                tags[i] = ('PART', 'Topic=Yes')

            # Rule 4: 'in' as ergative case marker
            elif token.lower() == 'in' and i > 0:
                prev_tag, _ = tags[i - 1]
                if prev_tag in ['NOUN', 'PRON', 'PROPN']:
                    tags[i] = ('ADP', 'Case=Erg')

        # Convert back to list of tuples
        return [(tokens[i], tag, feats) for i, (tag, feats) in enumerate(tags)]


class ZomiTaggerBackend:
    """Adapter for using ZomiPOSTagger as a backend in the pipeline."""

    def __init__(self) -> None:
        self.tagger: ZomiPOSTagger = ZomiPOSTagger()
        self._name: str = "zomi_tagger"
        self._available: bool = True

    def tag(self, doc: ZomiDoc) -> ZomiDoc:
        """Tag tokens in a ZomiDoc."""
        # from zomi_nlp.core.token import ZomiToken

        # Extract token texts
        token_texts = [token.text for token in doc.tokens]

        # Get tags with context
        tagged = self.tagger.tag_with_context(token_texts)

        # Update doc tokens
        for i, (_token_text, tag, feats) in enumerate(tagged):
            if i < len(doc.tokens):
                doc.tokens[i].pos_ = tag
                if feats:
                    # Parse features string into dict
                    if '|' in feats:
                        for feat in feats.split('|'):
                            if '=' in feat:
                                k, v = feat.split('=', 1)
                                doc.tokens[i].morph[k] = v
                    else:
                        doc.tokens[i].morph = {'feats': feats}

        return doc

    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return self._available

    def get_error_message(self) -> Optional[str]:
        return None if self._available else "Zomi tagger not available"


# Convenience function
def tag_zomi(text: str, split_clitics: bool = True) -> list[tuple[str, str, Optional[str]]]:
    """Quick POS tagging for Zomi text.

    Args:
        text: Input Zomi text
        split_clitics: Whether to split clitics before tagging

    Returns:
        List of (token, pos_tag, features) tuples
    """
    tokenizer: ZomiTokenizer = ZomiTokenizer(split_clitics=split_clitics)
    tagger: ZomiPOSTagger = ZomiPOSTagger(tokenizer=tokenizer)

    tokens: list[str] = tokenizer.tokenize(text)
    return tagger.tag_with_context(tokens)
