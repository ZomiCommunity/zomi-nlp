# zomi_nlp/native/morphology.py
"""Zomi morphological analyzer - breaks words into morphemes and analyzes features.

Handles:
- Prefixes (ka-, na-, a-, i-, ih-, etc.)
- Suffixes (-ve, -ta, -hiam, -maw, etc.)
- Reduplication (mahmah → mah + mah)
- Compounding (sang-inn → sang + inn)
- Clitic attachment
- Inflectional features
"""

from dataclasses import dataclass, field
from typing import Optional

from zomi_nlp.native.lexicons.base_lexicon import (
    ZOMI_LEXICON,
    ZOMI_PREFIXES,
    ZOMI_SUFFIXES,
    get_features_dict,
)


@dataclass
class Morpheme:
    """A single morpheme with its type and meaning."""
    form: str
    type: str  # "root", "prefix", "suffix", "infix", "clitic", "reduplicant"
    gloss: str = ""
    features: dict[str, str] = field(default_factory=dict)


@dataclass
class MorphAnalysis:
    """Complete morphological analysis of a word."""
    word: str
    morphemes: list[Morpheme]
    root: str
    features: dict[str, str]  # Combined features from all morphemes
    pos: Optional[str] = None
    is_reduplicated: bool = False
    is_compound: bool = False
    has_clitic: bool = False


class ZomiMorphologicalAnalyzer:
    """Morphological analyzer for Zomi language."""

    def __init__(self):
        # Use centralized data from lexicons
        self.PREFIXES = ZOMI_PREFIXES
        self.SUFFIXES = ZOMI_SUFFIXES
        self.LEXICON = ZOMI_LEXICON

        # Pre-sort prefixes and suffixes by length for greedy matching
        self.prefix_list = sorted(self.PREFIXES.keys(), key=len, reverse=True)
        self.suffix_list = sorted(self.SUFFIXES.keys(), key=len, reverse=True)

    def _parse_features(self, feats_str: str) -> dict[str, str]:
        """Parse feature string to dict using cached function."""
        return get_features_dict(feats_str)

    def analyze(self, word: str) -> MorphAnalysis:
        """Analyze a single word morphologically."""
        original = word
        word_lower = word.lower()

        morphemes: list[Morpheme] = []
        all_features: dict[str, str] = {}

        # Track where features come from (for debugging, optional)
        feature_sources: dict[str, str] = {}

        # 1. Check for reduplication
        redup_result = self._check_reduplication(word_lower)
        if redup_result:
            morphemes.extend(redup_result)
            all_features["Reduplication"] = "Yes"
            feature_sources["Reduplication"] = "redup"

        # 2. Split compound words
        compound_parts = self._split_compound(word_lower)
        if len(compound_parts) > 1:
            for part in compound_parts:
                morphemes.append(Morpheme(form=part, type="compound"))
            all_features["Compound"] = "Yes"
            feature_sources["Compound"] = "compound"

        # 3. Strip prefixes and collect features
        remaining = word_lower
        while remaining:
            prefix_found = False
            for prefix in self.prefix_list:
                if remaining.startswith(prefix) and len(remaining) > len(prefix):
                    prefix_info = self.PREFIXES[prefix]
                    prefix_features = self._parse_features(prefix_info.get("feats", ""))
                    morphemes.append(Morpheme(
                        form=prefix,
                        type=prefix_info["type"],
                        gloss=prefix_info["gloss"],
                        features=prefix_features.copy()
                    ))
                    # Add prefix features (Person, Number)
                    for k, v in prefix_features.items():
                        if k not in all_features:
                            all_features[k] = v
                            feature_sources[k] = f"prefix:{prefix}"
                    remaining = remaining[len(prefix):]
                    prefix_found = True
                    break
            if not prefix_found:
                break

        # 4. Find root and add its features
        root = remaining
        root_info = self.LEXICON.get(root, {})
        root_features = self._parse_features(root_info.get("feats", ""))

        # Add all root features (Voice, VerbForm, etc.)
        morphemes.append(Morpheme(
            form=root,
            type="root",
            features=root_features.copy()
        ))
        for k, v in root_features.items():
            if k not in all_features:
                all_features[k] = v
                feature_sources[k] = "root"

        # 5. Strip suffixes and collect features
        remaining_root = root
        suffixes_found: list[Morpheme] = []
        for suffix in self.suffix_list:
            if remaining_root.endswith(suffix) and len(remaining_root) > len(suffix):
                suffix_info = self.SUFFIXES[suffix]
                suffix_features = self._parse_features(suffix_info.get("feats", ""))
                suffixes_found.append(Morpheme(
                    form=suffix,
                    type=suffix_info["type"],
                    gloss=suffix_info["gloss"],
                    features=suffix_features.copy()
                ))
                # Add suffix features (Mood, Polite, etc.)
                for k, v in suffix_features.items():
                    if k not in all_features:
                        all_features[k] = v
                        feature_sources[k] = f"suffix:{suffix}"
                remaining_root = remaining_root[:-len(suffix)]

        # Add suffixes in reverse order (from inner to outer)
        if suffixes_found:
            # Update the root morpheme if suffixes were stripped
            stripped_root_info = self.LEXICON.get(remaining_root, {})
            stripped_root_features = self._parse_features(stripped_root_info.get("feats", ""))

            # Update root morpheme in the list
            for i, m in enumerate(morphemes):
                if m.type == "root":
                    morphemes[i] = Morpheme(
                        form=remaining_root,
                        type="root",
                        features=stripped_root_features.copy()
                    )
                    # Update root features in all_features
                    for k, v in stripped_root_features.items():
                        if k not in all_features:
                            all_features[k] = v
                    break

            # Add suffixes (in correct order: inner to outer)
            morphemes.extend(reversed(suffixes_found))

        # 6. Determine POS from the final root
        final_root = remaining_root if suffixes_found else root
        pos = self.LEXICON.get(final_root, {}).get("upos", "NOUN")

        return MorphAnalysis(
            word=original,
            morphemes=morphemes,
            root=final_root,
            features=all_features,
            pos=pos,
            is_reduplicated=bool(redup_result),
            is_compound=len(compound_parts) > 1,
            has_clitic=bool(suffixes_found)
        )

    def _check_reduplication(self, word: str) -> Optional[list[Morpheme]]:
        """Check if word is reduplicated and return morphemes."""
        if len(word) < 4:
            return None

        # Full reduplication
        half_len = len(word) // 2
        if len(word) % 2 == 0 and word[:half_len] == word[half_len:]:
            return [
                Morpheme(form=word[:half_len], type="reduplicant"),
                Morpheme(form=word[half_len:], type="root")
            ]

        return None

    def _split_compound(self, word: str) -> list[str]:
        """Split compound word by hyphens."""
        if "-" in word:
            return word.split("-")
        return [word]

    def analyze_sentence(self, tokens: list[str]) -> list[MorphAnalysis]:
        """Analyze all tokens in a sentence."""
        return [self.analyze(token) for token in tokens]

    def features_to_string(self, features: dict[str, str]) -> str:
        """Convert features dict to UD-style feature string."""
        if not features:
            return "_"
        return "|".join(f"{k}={v}" for k, v in features.items())


# Convenience function
def analyze_morphology(word: str) -> dict:
    """Quick morphological analysis of a Zomi word."""
    analyzer = ZomiMorphologicalAnalyzer()
    result = analyzer.analyze(word)
    return {
        "word": result.word,
        "root": result.root,
        "pos": result.pos,
        "features": result.features,
        "morphemes": [(m.form, m.type, m.gloss) for m in result.morphemes],
        "is_reduplicated": result.is_reduplicated,
        "is_compound": result.is_compound,
        "has_clitic": result.has_clitic,
    }
