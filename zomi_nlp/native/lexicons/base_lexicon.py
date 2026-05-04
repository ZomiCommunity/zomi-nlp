# zomi_nlp/native/lexicons/base_lexicon.py
"""Zomi base lexicon - 600+ entries with POS tags and features."""

from functools import lru_cache

# ============================================================
# DETAILED VERSIONS FOR MORPHOLOGY (with features dict)
# ============================================================

@lru_cache(maxsize=10000)  # Cache up to 10,000 unique feature strings
def parse_feats_string(feats_str: str) -> tuple[tuple[str, str], ...]:
    """Parse feature string to immutable tuple for caching.

    Returns tuple of (key, value) pairs for hashability.
    """
    if not feats_str or feats_str == "_":
        return ()

    result = []
    for pair in feats_str.split('|'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            result.append((key, value))
        else:
            result.append((pair, "Yes"))

    return tuple(result)


def get_features_dict(feats_str: str) -> dict[str, str]:
    """Get features as dictionary (from cached tuple)."""
    return dict(parse_feats_string(feats_str))


def format_feats_dict(feats_dict: dict[str, str]) -> str:
    """Convert features dict back to UD-style string."""
    if not feats_dict:
        return "_"

    pairs = []
    for key, value in feats_dict.items():
        if value == "Yes":
            pairs.append(key)
        else:
            pairs.append(f"{key}={value}")

    return "|".join(pairs)


# For direct string-to-string conversion (most common case)
@lru_cache(maxsize=10000)
def normalize_feats_string(feats_str: str) -> str:
    """Normalize feature string (sort keys, consistent formatting)."""
    if not feats_str or feats_str == "_":
        return "_"

    features = dict(parse_feats_string(feats_str))
    # Sort for consistent output
    sorted_items = sorted(features.items())
    pairs = [f"{k}={v}" if v != "Yes" else k for k, v in sorted_items]
    return "|".join(pairs)

def dict_filter(data, key, value):
    return {
        item_key: item_val
        for item_key, item_val in data.items()
        if item_val.get(key) == value
    }

# ============================================================
# MAIN LEXICON
# ============================================================
ZOMI_LEXICON = {
    # Prefixes
    "ka": {"lemma": "ka", "upos": "PRON", "morph_type": "prefix", "gloss": "1SG",
           "feats": "Number=Sing|Person=1|PronType=Prs", "deprel": "nsubj"},
    "ke": {"lemma": "ke", "upos": "PRON", "morph_type": "prefix", "gloss": "1SG",
           "feats": "Person=1|Number=Sing", "deprel": "nsubj"},
    "a": {"lemma": "a","upos": "PRON", 	"morph_type":"prefix", 	"gloss":"3SG",
          "feats":"Number=Sing|Person=3|PronType=Prs", "deprel": "nsubj"},
    "i": {"lemma": "i", "upos": "PRON", "morph_type": "prefix","gloss": "1PL",
          "feats": "Number=Plur|Person=1|PronType=Prs", "deprel": "nsubj"},
    "nin": {"lemma": "nin", "upos": "PRON", "morph_type": "prefix", "gloss": "1PL",
            "feats": "Person=1|Number=Plur", "deprel": "nsubj"},
    "hong": {"lemma": "hong", "upos": "PRON", "morph_type": "prefix", "gloss": "2SG",
             "feats": "Directional=Yes|Person=2|Obj=Yes", "deprel": "expl"},
    "ih": {"lemma": "ih", "upos": "PRON", "morph_type": "prefix", "gloss": "1PL",
           "feats": "Number=Plur|Person=1|PronType=Prs", "deprel": "nsubj"},

    # Suffixes/particles
    "ve": {"lemma": "ve", "upos": "PART", "morph_type": "suffix", "gloss": "POL",
           "feats": "Mood=Ind|Polite=Yes", "deprel": "discourse"},
    "veh": {"lemma": "veh", "upos": "PART", "morph_type": "suffix", "gloss": "POL",
            "feats": "Mood=Ind|Polite=Yes", "deprel": "discourse"},
    "ta": {"lemma": "ta", "upos": "PART", "morph_type": "suffix", "gloss": "EMPH",
           "feats": "Emphatic=Yes", "deprel": "discourse"},
    "tae": {"lemma": "tae", "upos": "PART", "morph_type": "suffix", "gloss": "EMPH",
            "feats": "Emphatic=Yes", "deprel": "discourse"},
    "hiam": {"lemma": "hiam","upos": "PART", "morph_type":"suffix", 	"gloss":"Q",
             "feats":"PartType=Int", "deprel": "discourse"},
    "maw": {"lemma": "maw", "upos": "PART", "morph_type": "suffix", "gloss": "Q",
            "feats": "PartType=Int", "deprel": "discourse"},
    "le": {"lemma": "le", "upos": "PART", "morph_type": "suffix", "gloss": "COND",
           "feats": "Conditional=Yes", "deprel": "discourse"},
    "leh": {"lemma": "leh", "upos": "PART", "morph_type": "suffix", "gloss": "COND",
            "feats": "Conditional=Yes", "deprel": "discourse"},
    "pah": {"lemma": "pah", "upos": "PART","morph_type": "suffix", "gloss":"TEMP",
            "feats":"Aspect=Perf|Temporal=Yes|Redup=Yes", "deprel": "advmod"},
    "sawn": {"lemma": "sawn","upos": "PART", "morph_type" : "suffix",	"gloss":"TEMP",
             "feats": "Temporal=Yes", "deprel": "discourse"},
    "ngei": {"lemma": "ngei", "upos":"PART", "morph_type":"suffix", "gloss":"PERF",
             "feats":"Aspect=Perf", "deprel": "discourse"},
    "khin": {"lemma": "khin","upos": "PART", "morph_type":"suffix", "gloss":"PERF",
             "feats": "Aspect=Perf", "deprel": "discourse"},
   "kei": {"lemma":"kei", "upos": "PART", "morph_type": "suffix", "gloss":"NEG",
           "feats":"Polarity=Neg", "deprel": "discourse"},
   "loin": {"lemma":"loin", "upos": "PART", "morph_type": "suffix", "gloss":"NEG",
            "feats":"Polarity=Neg", "deprel": "discourse"},
   "hen": {"lemma":"hen", "upos": "PART", "morph_type": "suffix", "gloss":"IMP",
           "feats":"Mood=Imp", "deprel": "discourse"},
   "uh": {"lemma":"uh", "upos": "PART", "morph_type": "suffix", 	"gloss":"PL",
          "feats":"Number=Plur", "deprel": "clf"},
   "hi": {"lemma": "hi", "upos": "PART", "morph_type": "suffix", "gloss": "COP",
          "feats": "Copula=Yes", "deprel": "cop"},

    # Nouns
    "pasian": {"lemma": "pasian", "upos": "NOUN", "feats": "Number=Sing|Proper=Yes"},
    "lei": {"lemma": "lei", "upos": "NOUN", "feats": "Number=Sing"},
    "lim": {"lemma": "lim", "upos": "NOUN", "feats": "Number=Sing"},
    "mel": {"lemma": "mel", "upos": "NOUN", "feats": "Number=Sing"},
    "kha": {"lemma": "kha", "upos": "NOUN", "feats": "Proper=Yes"},
    "an": {"lemma": "an", "upos": "NOUN", "feats": "Number=Sing"},
    "khuavak": {"lemma": "khuavak", "upos": "NOUN", "feats": "Number=Sing"},
    "apple": {"lemma": "apple", "upos": "NOUN", "feats": "Number=Sing"},
    "sanginn": {"lemma": "sanginn", "upos": "NOUN", "feats": "Number=Sing"},
    "sangnaupang": {"lemma": "sangnaupang", "upos": "NOUN", "feats": "Number=Sing"},
    "sangnaupangte": {"lemma": "sangnaupangte", "upos": "NOUN", "feats": "Number=Plur"},

    # Pronouns
    "na": {"lemma": "na", "upos": "PRON", "gloss": "2SG",
           "feats": "Number=Sing|Person=2|PronType=Prs", "deprel": "nsubj"},
    "nang": {"lemma": "nang", "upos": "PRON", "gloss": "2SG",
             "feats": "Number=Sing|Person=2|PronType=Prs", "deprel": "nsubj"},
    "kua": {"lemma": "kua", "upos": "PRON", "feats": "PronType=Int"},
    "amaute": {"lemma": "amaute", "upos": "PRON", "feats": "Number=Plur|Person=3|PronType=Prs"},
    "kote" : {"lemma": "kote", "upos": "PRON", "feats": "Number=Plur|Person=3|PronType=Prs"},
    "eite": {"lemma": "eite", "upos": "PRON", "feats": "Number=Plur|Person=1"},
    "amah": {"lemma": "amah", "upos": "PRON", "feats": "Number=Sing|Person=3"},

    # Verbs
    "ne": {"lemma": "ne", "upos": "VERB", "feats": "VerbForm=Fin"},
    "pia": {"lemma": "pia", "upos": "VERB", "feats": "VerbForm=Fin"},
    "piang": {"lemma": "piang", "upos": "VERB", "feats": "VerbForm=Fin"},
    "piangsak": {"lemma": "piangsak", "upos": "VERB", "feats": "Voice=Cau|VerbForm=Fin"},
    "om": {"lemma": "om", "upos": "VERB", "feats": "_"},
    "nei": {"lemma": "nei", "upos": "VERB", "feats": "VerbForm=Ger"},
    "ci": {"lemma": "ci", "upos": "VERB", "feats": "VerbForm=Fin"},
    "pai": {"lemma": "pai", "upos": "VERB", "gloss": "PL", # "morph_type": "prefix",
            "feats": "VerbForm=Fin", "deprel": "root"},

    # Adjectives
    "hawmpi": {"lemma": "hawmpi", "upos": "ADJ", "feats": "_"},

    # Numbers
    "khat": {"lemma": "khat", "upos": "NUM", "feats": "NumType=Card"},

    # Adverbs
    "mengmeng": {"lemma": "mengmeng", "upos": "ADV", "feats": "_", "deprel": "advmod"},
    "kik": {"lemma": "kik", "upos": "ADV", "feats": "Aspect=Iter", "deprel": "advmod"},
    # "pah": {"lemma": "pah", "upos": "ADV", "feats": "Aspect=Perf", "deprel": "advmod"},

    "pen": {"lemma": "pen", "upos": "PART", "feats": "Topic=Yes", "deprel": "discourse"},
    "cin": {"lemma": "cin", "upos": "PART", "feats": "Topic=Yes", "deprel": "discourse"},
    "te": {"lemma": "te", "upos": "PART", "feats": "Topic=Yes", "deprel": "discourse"},
}

# Zomi prefixes/particles and their features
ZOMI_PREFIXES = dict_filter(ZOMI_LEXICON, "morph_type", "prefix")

# Zomi suffixes/particles and their features
ZOMI_SUFFIXES = dict_filter(ZOMI_LEXICON, "morph_type", "suffix")
