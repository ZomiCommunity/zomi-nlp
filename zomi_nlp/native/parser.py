# zomi_nlp/native/parser.py

from zomi_nlp.native.dependency_parser import ZomiDependencyParser
from zomi_nlp.native.lemmatizer import ZomiLemmatizer
from zomi_nlp.native.tagger import ZomiPOSTagger  # Note: ZomiPOSTagger, not ZomiPoSTagger
from zomi_nlp.native.tokenizer import ZomiTokenizer


class ZomiRuleBasedParser:
    """Complete pipeline using modular components."""

    def __init__(self) -> None:
        self.dependency_parser = ZomiDependencyParser()
        self.tokenizer = ZomiTokenizer()
        self.tagger = ZomiPOSTagger()  # Fixed typo
        self.lemmatizer = ZomiLemmatizer()
        self._name: str = "zomi_rule_based_parser"
        self._available: bool = True

    def parse(self, sentence: str) -> list[dict]:
        """Run complete pipeline on a sentence.

        Returns:
            List of dictionaries with keys:
            - id: token index
            - form: token text
            - lemma: base form
            - tag: POS tag
            - feats: morphological features
            - head: head token index
            - deprel: dependency relation
        """
        # Step 1: Tokenize
        tokens = self.tokenizer.tokenize(sentence)

        # Step 2: POS Tag
        tagged = self.tagger.tag_with_context(tokens)  # Returns list of (token, tag, feats)
        pos_tags = [tag for _, tag, _ in tagged]
        feats_list = [feats for _, _, feats in tagged]

        # Step 3: Lemmatize
        lemmas = self.lemmatizer.lemmatize(tokens)

        # Step 4: Dependency Parse
        dependencies = self.dependency_parser.parse(tokens, pos_tags, lemmas if lemmas else None)

        # Step 5: Combine into unified format
        return self._combine(tokens, pos_tags, lemmas, feats_list, dependencies)

    def _combine(self, tokens, pos_tags, lemmas, feats_list, dependencies) -> list[dict]:
        """Combine all annotations into a unified list of dictionaries.

        Returns format expected by adapters and CoNLL-U export.
        """
        result: list[dict] = []

        # Create a mapping from token index to dependency info
        dep_map = {}
        for dep in dependencies:
            dep_map[dep["id"]] = dep

        for i, (token, pos, lemma, feats) in enumerate(
            zip(tokens, pos_tags, lemmas, feats_list), 1):
            # Get dependency info for this token
            dep_info = dep_map.get(i, {})

            token_dict = {
                "id": i,
                "form": token,
                "lemma": lemma or token,
                "tag": pos,
                "feats": feats or "_",
                "deprel": dep_info.get("deprel", "_"),
                "head": dep_info.get("head", 0),
            }
            result.append(token_dict)

        return result

    def parse_to_conllu(self, sentence: str) -> str:
        """Parse and return CoNLL-U format string."""
        parsed = self.parse(sentence)
        lines = []
        for token in parsed:
            line = "\t".join([
                str(token["id"]),
                token["form"],
                token["lemma"],
                token["tag"],
                "_",  # XPOS
                token["feats"],
                str(token["head"]),
                token["deprel"],
                "_",  # DEPS
                "_",  # MISC
            ])
            lines.append(line)
        return "\n".join(lines)

    def parse_to_json(self, sentence: str) -> list:
        """Parse and return JSON-serializable list."""
        return self.parse(sentence)

    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return self._available
