"""Modular dependency parser for Zomi language.

This parser assumes tokens and POS tags are already provided,
and focuses only on dependency relation assignment.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DependencyToken:
    """Token with dependency information."""
    id: int
    form: str
    lemma: str
    upos: str
    xpos: str
    feats: str
    head: int
    deprel: str
    deps: str = "_"
    misc: str = "_"


class ZomiDependencyParser:
    """Modular dependency parser for Zomi.

    Features:
    - Rule-based head assignment using Zomi grammar rules
    - Support for ergative case marking
    - Topic marker handling
    - Clause chaining detection
    """

    # Zomi-specific dependency relations
    DEPREL_MAPPING = {
        # Core arguments
        "nsubj": "nsubj",      # Nominal subject
        "obj": "obj",          # Object
        "iobj": "iobj",        # Indirect object

        # Non-core dependents
        "obl": "obl",          # Oblique nominal
        "advmod": "advmod",    # Adverbial modifier
        "amod": "amod",        # Adjectival modifier
        "det": "det",          # Determiner
        "nummod": "nummod",    # Numeric modifier
        "case": "case",        # Case marking (in, pan, ah)
        "mark": "mark",        # Marker (pen, cih)

        # Clausal relations
        "root": "root",        # Root of the clause
        "ccomp": "ccomp",      # Clausal complement
        "xcomp": "xcomp",      # Open clausal complement
        "advcl": "advcl",      # Adverbial clause
        "acl": "acl",          # Clausal modifier of noun
        "cc": "cc",            # Coordinating conjunction
        "conj": "conj",        # Conjunct

        # Modifiers
        "discourse": "discourse",  # Discourse particle
        "aux": "aux",          # Auxiliary
        "cop": "cop",          # Copula
        "expl": "expl",        # Expletive

        # Other
        "dep": "dep",          # Unspecified dependency
    }

    # Verbs that typically act as roots
    ROOT_VERBS = {"pai", "zoh", "ne", "ci", "om", "piang", "pia", "piangsak"}

    # Ergative case markers
    ERGATIVE_MARKERS = {"in", "tawh"}

    # Topic markers
    TOPIC_MARKERS = {"pen", "cin", "te", "leh"}

    def __init__(self):
        """Initialize dependency parser."""
        self._reset_state()

    def _reset_state(self) -> None:
        """Reset internal state for new parse."""
        self.tokens: list[dict] = []
        self.heads: list[int] = []
        self.deprels: list[str] = []

    def parse(
        self,
        tokens: list[str],
        pos_tags: list[str],
        lemmas: Optional[list[str]] = None,
        feats: Optional[list[str]] = None
    ) -> list[dict]:
        """Parse dependency relations for given tokens and POS tags.

        Args:
            tokens: List of token strings
            pos_tags: List of POS tags for each token
            lemmas: Optional list of lemmas
            feats: Optional list of morphological features

        Returns:
            List of dictionaries with token information including heads and deprels
        """
        self._reset_state()

        # Build token list
        for i, (form, upos) in enumerate(zip(tokens, pos_tags), 1):
            token = {
                "id": i,
                "form": form,
                "lemma": lemmas[i-1] if lemmas else form,
                "upos": upos,
                "xpos": upos,
                "feats": feats[i-1] if feats else "_",
                "head": 0,
                "deprel": "_",
            }
            self.tokens.append(token)

        # Find root (main verb/aux/predicate)
        root_idx = self._find_root()

        if root_idx:
            self.tokens[root_idx - 1]["head"] = 0
            self.tokens[root_idx - 1]["deprel"] = "root"

        # Assign dependencies
        for i, token in enumerate(self.tokens):
            if token["head"] == 0 and token["deprel"] == "root":
                continue  # Skip root

            # Assign head based on rules
            head = self._assign_head(i + 1, root_idx)
            deprel = self._assign_deprel(i + 1, token, head)

            token["head"] = head
            token["deprel"] = deprel

        return self.tokens

    def _find_root(self) -> int:
        """Find the root token index (the main verb/aux)."""
        # Look for verbs
        for i, token in enumerate(self.tokens, 1):
            if token["upos"] == "VERB" and token["form"] in self.ROOT_VERBS:
                return i

        # Fallback: last verb
        for i, token in enumerate(reversed(self.tokens), 1):
            if token["upos"] == "VERB":
                return len(self.tokens) - i + 1

        # Fallback: last aux
        for i, token in enumerate(reversed(self.tokens), 1):
            if token["upos"] == "AUX":
                return len(self.tokens) - i + 1

        # Default to last token
        return len(self.tokens)

    def _assign_head(self, idx: int, root_idx: int) -> int:
        """Assign head index for a token."""
        token = self.tokens[idx - 1]

        # Particles and aux attach to root or previous word
        if token["upos"] in ["PART", "AUX"]:
            # Attach to root if after root
            if idx > root_idx:
                return root_idx
            # Otherwise attach to previous word
            elif idx > 1:
                return idx - 1

        # Case markers attach to preceding noun
        if token["upos"] == "ADP" and token["form"] in self.ERGATIVE_MARKERS and idx > 1:
            return idx - 1

        # Topic markers attach to preceding noun
        if token["upos"] == "PART" and token["form"] in self.TOPIC_MARKERS and idx > 1:
            return idx - 1

        # Nouns typically attach to the nearest verb to the right (object)
        if token["upos"] in ["NOUN", "PRON", "PROPN"]:
            # Look for verb to the right
            for j in range(idx, len(self.tokens)):
                if self.tokens[j]["upos"] == "VERB":
                    return j + 1
            # Fallback to root
            return root_idx

        # Default: attach to root
        return root_idx

    def _assign_deprel(self, idx: int, token: dict, head_idx: int) -> str:
        """Assign dependency relation for a token."""
        upos = token["upos"]
        form = token["form"]
        head_token = self.tokens[head_idx - 1] if head_idx > 0 else None

        # Root
        if head_idx == 0:
            return "root"

        # Subject (noun before verb)
        if upos in ["NOUN", "PRON", "PROPN"] and idx < head_idx:
            return "nsubj"

        # Object (noun after verb)
        if upos in ["NOUN", "PRON", "PROPN"] and idx > head_idx:
            return "obj"

        # Case markers
        if upos == "ADP" and form in self.ERGATIVE_MARKERS:
            return "case"

        # Topic markers
        if upos == "PART" and form in self.TOPIC_MARKERS:
            if form.lower() == "pen":
                return "discourse"
            return "mark"

        # Discourse particles (sentence final)
        if upos == "PART" and idx > head_idx:
            return "discourse"

        # Auxiliary verbs
        if upos == "AUX":
            return "aux"

        # Copula
        if upos == "AUX" and head_token and head_token["upos"] in ["NOUN", "ADJ"]:
            return "cop"

        # Adverbial modifier
        if upos == "ADV":
            return "advmod"

        # Adjectival modifier
        if upos == "ADJ" and head_token and head_token["upos"] in ["NOUN", "PRON"]:
            return "amod"

        # Punctuation
        if upos == "PUNCT":
            return "punct"

        # Default
        return "dep"

    def to_conllu(self, parsed_data: list[dict]) -> str:
        """Convert parsed data to CoNLL-U format."""
        lines = []
        for token in parsed_data:
            line = "\t".join([
                str(token["id"]),
                token["form"],
                token["lemma"],
                token["upos"],
                token["xpos"],
                token["feats"],
                str(token["head"]),
                token["deprel"],
                token.get("deps", "_"),
                token.get("misc", "_"),
            ])
            lines.append(line)
        return "\n".join(lines)

    def to_json(self, parsed_data: list[dict]) -> list[dict]:
        """Return parsed data as JSON-serializable list."""
        return parsed_data


# Convenience function
def parse_dependencies(
    tokens: list[str],
    pos_tags: list[str],
    lemmas: Optional[list[str]] = None
) -> list[dict]:
    """Quick dependency parsing for Zomi text.

    Args:
        tokens: List of token strings
        pos_tags: List of POS tags
        lemmas: Optional list of lemmas

    Returns:
        List of dictionaries with dependency annotations
    """
    parser = ZomiDependencyParser()
    return parser.parse(tokens, pos_tags, lemmas)
