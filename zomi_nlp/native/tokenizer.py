# zomi_nlp/native/tokenizer.py
"""Zomi tokenizer and sentence splitter.

Features:
- Multi‑clitic splitting
- Punctuation splitting anywhere in the word
- Reduplication with Zomi syllable validation
- Compound word splitting
- Plural suffix splitting for nouns
- Token spans
- Sentence splitting with abbreviation handling
"""

import logging
import re

logger = logging.getLogger(__name__)

# -----------------------------
# Zomi syllable validator
# -----------------------------

class ZomiSyllableValidator:
    """Validates whether a string is a plausible Zomi syllable.

    Used to improve reduplication accuracy.
    """

    ONSETS = [
        "kh", "ch", "ph", "th", "ng", "ny",
        "k", "g", "c", "j", "t", "d", "p", "b",
        "m", "n", "l", "r", "s", "h", "v", "z", "w"
    ]

    VOWELS = [
        "aw", "ei", "ai", "ui", "oa", "ia", "ua",
        "a", "e", "i", "o", "u"
    ]

    CODAS = [
        "ng", "m", "n", "k", "t", "p", "h", "l", "r"
    ]

    def __init__(self):
        onset = f"(?:{'|'.join(self.ONSETS)})?"
        vowel = f"(?:{'|'.join(self.VOWELS)})"
        coda = f"(?:{'|'.join(self.CODAS)})?"
        self.pattern = re.compile(f"^{onset}{vowel}{coda}$", re.IGNORECASE)

    def is_syllable(self, text: str) -> bool:
        return bool(self.pattern.match(text))


# -----------------------------
# Splitter components
# -----------------------------

class CliticSplitter:
    """Split Zomi clitics, including multi‑clitic chains."""

    CLITICS = [
        "in", "ngei", "hiam", "sawn", "khin", "loin", "leh", "veh",
        "pah", "maw", "kei", "hen", "uh", "ta", "ve", "le", "hi"
    ]

    def __init__(self):
        self.sorted_clitics = sorted(self.CLITICS, key=len, reverse=True)

    def split(self, word: str) -> list[str]:
        tokens = []
        w = word

        while True:
            w_lower = w.lower()
            matched = False

            for clitic in self.sorted_clitics:
                if w_lower.endswith(clitic) and len(w_lower) > len(clitic):
                    tokens.append(w[-len(clitic):])
                    w = w[:-len(clitic)]
                    matched = True
                    break

            if not matched:
                break

        return [w] + tokens[::-1]


class PunctuationSplitter:
    """Split punctuation anywhere in a word."""

    PUNCT = set('.,!?;:()[]{}"\'“”‘’—–…')

    def split(self, word: str) -> list[str]:
        tokens = []
        current = ""

        for ch in word:
            if ch in self.PUNCT:
                if current:
                    tokens.append(current)
                    current = ""
                tokens.append(ch)
            else:
                current += ch

        if current:
            tokens.append(current)

        return tokens


class ReduplicationSplitter:
    """Split reduplicated words using Zomi syllable validation."""

    REDUP_PATTERN = re.compile(r'^([A-Za-z]{3,})\1$', re.IGNORECASE)

    def __init__(self):
        self.validator = ZomiSyllableValidator()

    def split(self, word: str) -> list[str]:
        match = self.REDUP_PATTERN.match(word)
        if not match:
            return [word]

        stem = match.group(1)

        if self.validator.is_syllable(stem):
            return [stem, stem]

        return [word]


class CompoundSplitter:
    """Split hyphenated compounds, preserving '-' as tokens."""

    def split(self, word: str) -> list[str]:
        if "-" not in word:
            return [word]

        parts = word.split("-")
        tokens = []
        for i, part in enumerate(parts):
            tokens.append(part)
            if i < len(parts) - 1:
                tokens.append("-")
        return tokens


class PluralSuffixSplitter:
    """Split Zomi plural suffix -te from nouns ONLY.

    Rules:
    - Split -te from nouns: sangnaupangte → sangnaupang + te
    - NEVER split pronouns: amaute, eite, kote, note, etc.

    Examples:
    - sangnaupangte → sangnaupang + te (noun plural)
    - mite → mi + te (people)
    - naute → nau + te (children)
    - amaute → amaute (pronoun, no split)
    - eite → eite (pronoun, no split)
    - kote → kote (pronoun, no split)
    """

    # Pronouns that should NEVER be split (already plural or emphatic)
    INDIVISIBLE_PRONOUNS = {
        # Personal pronouns
        "ka", "kei", "na", "nang", "a", "amah", "amau", "amaute",
        "ei", "eite", "ih", "nin", "pai",
        # Interrogative pronouns
        "ko", "kote", "note", "nodan", "bang", "kuate",
        "kua", "kuamah",
    }

    # Nouns that CAN take plural -te suffix
    SPLITTABLE_NOUNS = {
        "sangnaupang",  # student → students
        "mi",           # person → people
        "nau",          # child → children
        "tapa",         # son → sons
        "tanu",         # daughter → daughters
        "lawm",         # friend → friends
        "galkap",       # soldier → soldiers
    }

    PLURAL_SUFFIX = "te"

    def split(self, word: str) -> list[str]:
        """Split plural suffix -te from nouns only."""
        word_lower = word.lower()
        logger.debug(f"PluralSplitter: checking '{word}'")

        # NEVER split pronouns
        if word_lower in self.INDIVISIBLE_PRONOUNS:
            logger.debug(f"PluralSplitter: '{word}' is an indivisible pronoun")
            return [word]

        # Check if word ends with 'te' and is long enough
        if word_lower.endswith(self.PLURAL_SUFFIX) and len(word_lower) > len(self.PLURAL_SUFFIX):
            base = word_lower[:-len(self.PLURAL_SUFFIX)]

            # Split only if base is a noun that takes plural
            if base in self.SPLITTABLE_NOUNS:
                logger.debug(f"PluralSplitter: splitting '{word}' → '{base}' + 'te'")
                # Preserve original case
                original_base = word[:-len(self.PLURAL_SUFFIX)]
                return [original_base, self.PLURAL_SUFFIX]

        logger.debug(f"PluralSplitter: no split for '{word}'") 
        return [word]


# -----------------------------
# Tokenizer
# -----------------------------

class ZomiTokenizer:
    """Pipeline-based Zomi tokenizer."""

    def __init__(self, split_clitics: bool = True, split_punct: bool = True):
        self.split_clitics = split_clitics
        self.split_punct = split_punct

        self.clitic_splitter = CliticSplitter()
        self.punct_splitter = PunctuationSplitter()
        self.redup_splitter = ReduplicationSplitter()
        self.compound_splitter = CompoundSplitter()
        self.plural_splitter = PluralSuffixSplitter()  # ← ADD THIS

    def tokenize(self, text: str) -> list[str]:
        if not text:
            return []

        text = " ".join(text.split())
        words = text.split()

        tokens: list[str] = []
        for word in words:
            tokens.extend(self._process_word(word))

        return tokens

    def _process_word(self, word: str) -> list[str]:
        logger.debug(f"Tokenizer: processing word '{word}'")
        tokens: list[str] = [word]

        # Apply splitters in order (priority: punctuation first)
        if self.split_punct:
            tokens = self._apply_splitter(tokens, self.punct_splitter)
            logger.debug(f"After punctuation: {tokens}")

        # Split plural suffix before clitics
        tokens = self._apply_splitter(tokens, self.plural_splitter)
        logger.debug(f"After plural splitting: {tokens}")

        if self.split_clitics:
            tokens = self._apply_splitter(tokens, self.clitic_splitter)
            logger.debug(f"After clitic splitting: {tokens}")

        # Apply remaining splitters
        tokens = self._apply_splitter(tokens, self.redup_splitter)
        logger.debug(f"After reduplication: {tokens}")

        tokens = self._apply_splitter(tokens, self.compound_splitter)
        logger.debug(f"After compound splitting: {tokens}")

        return tokens

    def _apply_splitter(self, tokens: list[str], splitter) -> list[str]:
        out: list[str] = []
        for t in tokens:
            out.extend(splitter.split(t))
        return out

    def tokenize_with_spans(self, text: str) -> list[tuple[str, int, int]]:
        tokens = self.tokenize(text)
        spans: list[tuple[str, int, int]] = []

        pos = 0
        lower = text.lower()

        for token in tokens:
            token_lower = token.lower()
            start = lower.find(token_lower, pos)
            if start == -1:
                start = pos
            end = start + len(token)
            spans.append((token, start, end))
            pos = end

        return spans


def tokenize_zomi(text: str, split_clitics: bool = True) -> list[str]:
    """Convenience function."""
    return ZomiTokenizer(split_clitics=split_clitics).tokenize(text)


# -----------------------------
# Sentence splitter
# -----------------------------


class ZomiSentenceSplitter:
    """Improved sentence splitter for Zomi and English‑influenced text.

    Avoids look‑behind (Python limitation).
    """

    ABBREVIATIONS = {
        "mr", "mrs", "ms", "dr", "prof", "rev", "hon",
        "vs", "etc", "e.g", "i.e", "cf", "al",
        "p.n", "a.d",
    }

    # Split on punctuation followed by space/newline/end
    BASE_SPLIT = re.compile(r'([.!?]+["\')\]]*\s+)')

    @classmethod
    def split(cls, text: str) -> list[str]:
        if not text:
            return []

        parts = cls.BASE_SPLIT.split(text)

        # Recombine into sentences
        sentences = []
        current = ""

        for part in parts:
            current += part

            # Check if this part ends with sentence punctuation
            stripped = current.strip()
            if not stripped:
                continue

            last_word = stripped.rstrip().split()[-1].lower().rstrip('."\'”’)]')

            if last_word in cls.ABBREVIATIONS:
                # Don't split here
                continue

            # If ends with punctuation, finalize sentence
            if stripped[-1] in ".!?":
                sentences.append(stripped)
                current = ""

        # Add any remaining text
        if current.strip():
            sentences.append(current.strip())

        return sentences
