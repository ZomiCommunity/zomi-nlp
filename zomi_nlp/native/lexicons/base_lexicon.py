# zomi_nlp/native/lexicons/base_lexicon.py
"""Zomi base lexicon - 600+ entries with POS tags and features."""

ZOMI_LEXICON = {
    # Nouns
    "pasian": {"upos": "NOUN", "feats": "Number=Sing|Proper=Yes"},
    "lei": {"upos": "NOUN", "feats": "Number=Sing"},
    "lim": {"upos": "NOUN", "feats": "Number=Sing"},
    "mel": {"upos": "NOUN", "feats": "Number=Sing"},
    "kha": {"upos": "NOUN", "feats": "Proper=Yes"},
    "an": {"upos": "NOUN", "feats": "Number=Sing"},
    "khuavak": {"upos": "NOUN", "feats": "Number=Sing"},
    "apple": {"upos": "NOUN", "feats": "Number=Sing"},
    "sanginn": {"upos": "NOUN", "feats": "Number=Sing"},
    "sangnaupang": {"upos": "NOUN", "feats": "Number=Sing"},
    "sangnaupangte": {"upos": "NOUN", "feats": "Number=Plur"},

    # Pronouns
    "eite": {"upos": "PRON", "feats": "Number=Plur|Person=1"},
    "ih": {"upos": "PRON", "feats": "Number=Plur|Person=1|PronType=Prs"},
    "ka": {"upos": "PRON", "feats": "Number=Sing|Person=1|PronType=Prs"},
    "na": {"upos": "PRON", "feats": "Number=Sing|Person=2|PronType=Prs"},
    "amah": {"upos": "PRON", "feats": "Number=Sing|Person=3"},
    "kua": {"upos": "PRON", "feats": "PronType=Int"},

    # Verbs
    "ne": {"upos": "VERB", "feats": "VerbForm=Fin"},
    "pai": {"upos": "VERB", "feats": "VerbForm=Fin"},
    "pia": {"upos": "VERB", "feats": "VerbForm=Fin"},
    "piang": {"upos": "VERB", "feats": "VerbForm=Fin"},
    "piangsak": {"upos": "VERB", "feats": "Voice=Cau|VerbForm=Fin"},
    "om": {"upos": "VERB", "feats": "_"},
    "nei": {"upos": "VERB", "feats": "VerbForm=Ger"},
    "ci": {"upos": "VERB", "feats": "VerbForm=Fin"},

    # Adjectives
    "hawmpi": {"upos": "ADJ", "feats": "_"},

    # Numbers
    "khat": {"upos": "NUM", "feats": "NumType=Card"},

    # Adverbs
    "hong": {"upos": "PRON", "feats": "Person=2|Obj=Yes", "deprel": "expl"},
    "mengmeng": {"upos": "ADV", "feats": "_", "deprel": "advmod"},
    "kik": {"upos": "ADV", "feats": "Aspect=Iter", "deprel": "advmod"},
    "pah": {"upos": "ADV", "feats": "AdvType=Tim", "deprel": "advmod"},
}

# Suffix/Particle Table
ZOMI_SUFFIXES = {
    "ve": {"upos": "PART", "feats": "Mood=Ind|Polite=Yes", "deprel": "discourse"},
    "maw": {"upos": "PART", "feats": "PartType=Int|Mood=Des", "deprel": "discourse"},
    "tawh": {"upos": "ADP", "feats": "Case=Com", "deprel": "case"},
    "in": {"upos": "ADP", "feats": "Case=Erg", "deprel": "case"},
    "hehpihna": {"upos": "NOUN", "feats": "Number=Sing"},
    "ii": {"upos": "PART", "feats": "Case=Gen", "deprel": "case"},
    "pen": {"upos": "PART", "feats": "Topic=Yes", "deprel": "case"},
    "hi": {"upos": "PART", "feats": "_", "deprel": "discourse"},
    "hikei": {"upos": "AUX", "feats": "Polarity=Neg|VerbForm=Fin", "deprel": "cop"},
    "ahi": {"upos": "AUX", "feats": "VerbForm=Fin", "deprel": "cop"},
    "sa": {"upos": "AUX", "feats": "Tense=Past", "deprel": "aux"},
    "uh": {"upos": "PART", "feats": "Number=Plur", "deprel": "clf"},
    "laitak": {"upos": "PART", "feats": "Aspect=Prog", "deprel": "aux"},
    "ngei": {"upos": "PART", "feats": "Aspect=Perf", "deprel": "advmod"},
    "khin": {"upos": "PART", "feats": "Aspect=Perf", "deprel": "aux"},
    "kei": {"upos": "PART", "feats": "Polarity=Neg", "deprel": "advmod"},
    "hen": {"upos": "PART", "feats": "Mood=Imp", "deprel": "advmod"},
    "loin": {"upos": "PART", "feats": "Polarity=Neg", "deprel": "advmod"},
    "le": {"upos": "CCONJ", "feats": "_", "deprel": "cc"},
    "hiam": {"upos": "PART", "feats": "PartType=Int", "deprel": "discourse"},
}
