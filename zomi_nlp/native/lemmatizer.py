# zomi_nlp/native/lemmatizer.py
"""Zomi-native lemmatizer using lexicon lookup and rule-based stemming."""

import re
from dataclasses import dataclass
from typing import Optional

from zomi_nlp.core.doc import ZomiDoc
from zomi_nlp.native.lexicons import ZOMI_LEXICON
from zomi_nlp.native.tokenizer import CliticSplitter, ZomiTokenizer


@dataclass
class LemmaRule:
    """Rule for lemmatization."""
    pattern: str          # Regex pattern
    replacement: str      # Replacement string
    priority: int = 0     # Higher priority runs first


class ZomiLemmatizer:
    """Lemmatizer for Zomi language using lexicon + rules.

    Features:
    - Lexicon lookup for known words
    - Clitic removal (ve, ta, hiam, etc.)
    - Reduplication handling
    - Affix stripping (prefixes, suffixes)
    - Rule-based fallback with priority ordering
    """

    # Common Zomi suffixes to remove
    SUFFIX_PATTERNS: list[tuple[str, str]] = [
        (r've$', ''),      # Polite/indicative
        (r'veh$', ''),     # Polite variant
        (r'ta$', ''),      # Emphatic
        (r'tae$', ''),     # Emphatic variant
        (r'hiam$', ''),    # Question
        (r'maw$', ''),     # Question
        (r'leh$', ''),     # Conditional
        (r'le$', ''),      # Conditional
        (r'pah$', ''),     # Temporal
        (r'sawn$', ''),    # Temporal
        (r'ngei$', ''),    # Perfective
        (r'khin$', ''),    # Perfective
        (r'kei$', ''),     # Negative
        (r'lo$', ''),    # Negative
        (r'loin$', ''),    # Negative
        (r'hen$', ''),     # Imperative
        (r'uh$', 'u'),     # Plural (u is stem form)
        (r'te$', ''),      # Plural variant
        (r'na$', ''),      # Nominalizer
        (r'na', ''),       # Nominalizer (mid-word)
    ]

    # Common Zomi prefixes to remove
    PREFIX_PATTERNS: list[tuple[str, str]] = [
        (r'^ka', ''),      # 1st person singular
        (r'^na', ''),      # 2nd person singular
        (r'^a', ''),       # 3rd person
        (r'^i', ''),       # 1st person plural
        (r'^nin', ''),     # 1st person plural
        (r'^nang', ''),    # 2nd person singular
        (r'^amah', ''),    # 3rd person singular
        (r'^amau', ''),    # 3rd person plural
        (r'^hong', ''),    # Directional
        (r'^pai', ''),     # 1st person plural
        (r'^sang', ''),    # Comparative
    ]

    # Reduplication patterns
    REDUP_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r'^(.{2,}?)\1$'), r'\1'),  # Full reduplication
        (re.compile(r'^(..).*\1$'), r'\1'),    # Partial reduplication
    ]

    # Special case mapping (irregular forms)
    IRREGULAR_LEMMAS: dict[str, str] = {
        # Verbs
        "pai": "pai",
        "paive": "pai",
        "paiveh": "pai",
        "zoh": "zoh",
        "zohve": "zoh",
        "zohveh": "zoh",
        "ne": "ne",
        "neh": "ne",
        "neve": "ne",
        "cii": "ci",
        "ci-a": "ci",
        "om": "om",
        "omve": "om",
        "nei": "nei",
        "neive": "nei",

        # Pronouns (lemmatize to base form)
        "ka": "ka",
        "ke": "ka",
        "keimah": "keimah",
        "na": "na",
        "nang": "nang",
        "amah": "amah",
        "amau": "amau",
        "eite": "eite",
        "ih": "ih",

        # Nouns
        "sangnaupang": "sangnaupang",
        "sangnaupangte": "sangnaupang",

        # Particles
        "hi": "hi",
        "hikei": "hi",
        "ahi": "hi",

        # Question words
        "kua": "kua",
        "kuai": "kua",
        "kuamah": "kua",
    }

    def __init__(self, tokenizer: Optional[ZomiTokenizer] = None):
        """Initialize lemmatizer.

        Args:
            tokenizer: Optional tokenizer for pre-processing.
        """
        self.tokenizer = tokenizer or ZomiTokenizer()
        self.lexicon = ZOMI_LEXICON.copy()
        self.clitic_splitter = CliticSplitter()

        # Compile regex patterns for efficiency
        self._compiled_rules: list[tuple[re.Pattern, str]] = []
        self._compile_rules()

    def _compile_rules(self) -> None:
        """Pre-compile regex patterns for performance."""
        # Compile suffix patterns
        for pattern, replacement in self.SUFFIX_PATTERNS:
            self._compiled_rules.append((re.compile(pattern, re.IGNORECASE), replacement))

        # Compile prefix patterns
        for pattern, replacement in self.PREFIX_PATTERNS:
            self._compiled_rules.append((re.compile(pattern, re.IGNORECASE), replacement))

    def lemmatize(self, tokens: list[str]) -> list[str]:
        """Get lemmas for a list of tokens.

        Args:
            tokens: List of token strings

        Returns:
            List of lemma strings
        """
        return [self._get_lemma(token) for token in tokens]

    def lemmatize_with_info(self, tokens: list[str]) -> list[tuple[str, str, str]]:
        """Get lemmas with processing info.

        Returns:
            List of (original, lemma, method) tuples where method indicates
            how the lemma was derived (lexicon, clitic, rule, etc.)
        """
        results = []
        for token in tokens:
            lemma, method = self._get_lemma_with_method(token)
            results.append((token, lemma, method))
        return results

    def _get_lemma(self, word: str) -> str:
        """Get lemma for a single word."""
        lemma, _ = self._get_lemma_with_method(word)
        return lemma

    def _get_lemma_with_method(self, word: str) -> tuple[str, str]:
        """Get lemma with method description.

        Returns:
            Tuple of (lemma, method) where method is a string indicating
            how the lemma was derived.
        """
        word_lower = word.lower()

        # 1. Check irregular forms
        if word_lower in self.IRREGULAR_LEMMAS:
            return self.IRREGULAR_LEMMAS[word_lower], "irregular"

        # 2. Check lexicon
        if word_lower in self.lexicon:
            entry = self.lexicon[word_lower]
            if 'lemma' in entry:
                return entry['lemma'], "lexicon"
            # Use word itself as lemma if not specified
            return word, "lexicon"

        # 3. Split clitics and check stem
        clitic_split = self.clitic_splitter.split(word_lower)
        if len(clitic_split) > 1:
            stem = clitic_split[0]
            # Check if stem is in lexicon
            if stem in self.lexicon:
                return stem, "clitic"
            # Check if stem is irregular
            if stem in self.IRREGULAR_LEMMAS:
                return self.IRREGULAR_LEMMAS[stem], "clitic"

        # 4. Apply suffix rules (shortest first, but with priority)
        for pattern, replacement in self._compiled_rules:
            candidate = pattern.sub(replacement, word_lower)

            if (
                pattern.search(word_lower)
                and candidate
                and len(candidate) >= 2
                and self._is_plausible_stem(candidate)
            ):
                return candidate, "rule"

        # 5. Handle reduplication
        for pattern, _replacement in self.REDUP_PATTERNS:
            match = re.match(pattern, word_lower)
            if match:
                stem = match.group(1)
                if self._is_plausible_stem(stem):
                    return stem, "redup"

        # 6. Default: return word itself
        return word, "default"

    def _is_plausible_stem(self, candidate: str) -> bool:
        """Check if a candidate stem is linguistically plausible."""
        # Minimum length check
        if len(candidate) < 2:
            return False

        # Must contain at least one vowel
        if not any(c in 'aeiou' for c in candidate):
            return False

        # No weird character sequences
        return not re.search(r'[bcdfghjklmnpqrstvwxyz]{5,}', candidate)


class ZomiLemmatizerBackend:
    """Adapter for using ZomiLemmatizer in the pipeline."""

    def __init__(self) -> None:
        self.lemmatizer: ZomiLemmatizer = ZomiLemmatizer()
        self._name: str = "zomi_lemmatizer"
        self._available: bool = True

    def lemmatize(self, doc: ZomiDoc) -> ZomiDoc:
        """Add lemmas to tokens in a ZomiDoc."""
        # Extract token texts
        token_texts = [token.text for token in doc.tokens]

        # Get lemmas
        lemmas = self.lemmatizer.lemmatize(token_texts)

        # Update doc tokens
        for i, lemma in enumerate(lemmas):
            if i < len(doc.tokens):
                doc.tokens[i].lemma_ = lemma

        return doc

    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return self._available

    def get_error_message(self) -> Optional[str]:
        return None if self._available else "Zomi lemmatizer not available"


# Convenience function
def lemmatize_zomi(text: str, split_clitics: bool = True) -> list[str]:
    """Quick lemmatization for Zomi text.

    Args:
        text: Input Zomi text
        split_clitics: Whether to split clitics before lemmatization

    Returns:
        List of lemma strings
    """
    tokenizer = ZomiTokenizer(split_clitics=split_clitics)
    lemmatizer = ZomiLemmatizer(tokenizer=tokenizer)

    tokens = tokenizer.tokenize(text)
    return lemmatizer.lemmatize(tokens)


def lemmatize_with_info_zomi(text: str) -> list[tuple[str, str, str]]:
    """Quick lemmatization with processing info.

    Returns:
        List of (original, lemma, method) tuples
    """
    tokenizer = ZomiTokenizer()
    lemmatizer = ZomiLemmatizer(tokenizer=tokenizer)

    tokens = tokenizer.tokenize(text)
    return lemmatizer.lemmatize_with_info(tokens)
