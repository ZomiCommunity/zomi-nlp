# zomi_nlp/native/tokenizer.py

"""Zomi tokenizer and sentence splitter.

Features:
- Multi‑clitic splitting
- Punctuation splitting anywhere in the word
- Reduplication with Zomi syllable validation
- Compound word splitting
- Token spans
- Sentence splitting with abbreviation handling
"""

import re

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
        "ngei", "hiam", "sawn", "khin", "loin", "leh", "veh",
        "pah", "te", "maw", "kei", "hen", "uh", "ta", "ve", "le", "hi"
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
        tokens: list[str] = [word]

        if self.split_punct:
            tokens = self._apply_splitter(tokens, self.punct_splitter)

        if self.split_clitics:
            tokens = self._apply_splitter(tokens, self.clitic_splitter)

        tokens = self._apply_splitter(tokens, self.redup_splitter)
        tokens = self._apply_splitter(tokens, self.compound_splitter)

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

