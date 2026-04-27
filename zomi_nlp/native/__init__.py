# zomi_nlp/native/__init__.py
"""Zomi-native NLP components.

This module contains pure Python implementations of Zomi NLP components
with no external dependencies.
"""

from zomi_nlp.native.lemmatizer import (
    ZomiLemmatizer,
    ZomiLemmatizerBackend,
    lemmatize_with_info_zomi,
    lemmatize_zomi,
)
from zomi_nlp.native.ner import ZomiNER, ZomiNERBackend, extract_entities_zomi
from zomi_nlp.native.parser import (
    ZomiParserV362,
    ZomiRuleBasedParser,
)
from zomi_nlp.native.tagger import (
    ZomiPOSTagger,
    ZomiTaggerBackend,
    tag_zomi,
)
from zomi_nlp.native.tokenizer import (
    CliticSplitter,
    CompoundSplitter,
    PunctuationSplitter,
    ReduplicationSplitter,
    ZomiSentenceSplitter,
    ZomiSyllableValidator,
    ZomiTokenizer,
    tokenize_zomi,
)

__all__ = [
    # Parser
    "ZomiParserV362",
    "ZomiParserAdapter",
    "ZomiRuleBasedParser",
    # Tokenizer and related components
    "ZomiSentenceSplitter",
    "ZomiTokenizer",
    "tokenize_zomi",
    "CliticSplitter",
    "CompoundSplitter",
    "PunctuationSplitter",
    "ReduplicationSplitter",
    "ZomiSyllableValidator",
    # Tagger
    "ZomiPOSTagger",
    "ZomiTaggerBackend",
    "tag_zomi",
    # Lemmatizer
    "ZomiLemmatizer",
    "ZomiLemmatizerBackend",
    "lemmatize_zomi",
    "lemmatize_with_info_zomi",
    # Named Entity Recognizer
    "ZomiNER",
    "ZomiNERBackend",
    "extract_entities_zomi",
]
