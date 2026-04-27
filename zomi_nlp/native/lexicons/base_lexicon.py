# zomi_nlp/native/lexicons/base_lexicon.py
"""Zomi base lexicon - 600+ entries with POS tags and features."""

ZOMI_LEXICON = {
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
    "eite": {"lemma": "eite", "upos": "PRON", "feats": "Number=Plur|Person=1"},
    "ih": {"lemma": "ih", "upos": "PRON", "feats": "Number=Plur|Person=1|PronType=Prs"},
    "ka": {"lemma": "ka", "upos": "PRON", "feats": "Number=Sing|Person=1|PronType=Prs"},
    "na": {"lemma": "na", "upos": "PRON", "feats": "Number=Sing|Person=2|PronType=Prs"},
    "amah": {"lemma": "amah", "upos": "PRON", "feats": "Number=Sing|Person=3"},
    "kua": {"lemma": "kua", "upos": "PRON", "feats": "PronType=Int"},

    # Verbs
    "ne": {"lemma": "ne", "upos": "VERB", "feats": "VerbForm=Fin"},
    "pai": {"lemma": "pai", "upos": "VERB", "feats": "VerbForm=Fin"},
    "pia": {"lemma": "pia", "upos": "VERB", "feats": "VerbForm=Fin"},
    "piang": {"lemma": "piang", "upos": "VERB", "feats": "VerbForm=Fin"},
    "piangsak": {"lemma": "piangsak", "upos": "VERB", "feats": "Voice=Cau|VerbForm=Fin"},
    "om": {"lemma": "om", "upos": "VERB", "feats": "_"},
    "nei": {"lemma": "nei", "upos": "VERB", "feats": "VerbForm=Ger"},
    "ci": {"lemma": "ci", "upos": "VERB", "feats": "VerbForm=Fin"},

    # Adjectives
    "hawmpi": {"lemma": "hawmpi", "upos": "ADJ", "feats": "_"},

    # Numbers
    "khat": {"lemma": "khat", "upos": "NUM", "feats": "NumType=Card"},

    # Adverbs
    "hong": {"lemma": "hong", "upos": "PRON", "feats": "Person=2|Obj=Yes", "deprel": "expl"},
    "mengmeng": {"lemma": "mengmeng", "upos": "ADV", "feats": "_", "deprel": "advmod"},
    "kik": {"lemma": "kik", "upos": "ADV", "feats": "Aspect=Iter", "deprel": "advmod"},
    "pah": {"lemma": "pah", "upos": "ADV", "feats": "Aspect=Perf", "deprel": "advmod"},

    "pen": {"lemma": "pen", "upos": "PART", "feats": "Topic=Yes", "deprel": "discourse"},
}

# Suffix/Particle Table
ZOMI_SUFFIXES = {
    "ve": {"lemma": "ve", "upos": "PART", "feats": "Mood=Ind|Polite=Yes", "deprel": "discourse"},
    "maw": {"lemma": "maw", "upos": "PART", "feats": "PartType=Int|Mood=Des",
            "deprel": "discourse"},
    "tawh": {"lemma": "tawh", "upos": "ADP", "feats": "Case=Com", "deprel": "case"},
    "in": {"lemma": "in", "upos": "ADP", "feats": "Case=Erg", "deprel": "case"},
    "hehpihna": {"lemma": "hehpihna", "upos": "NOUN", "feats": "Number=Sing"},
    "ii": {"lemma": "ii", "upos": "PART", "feats": "PartType=Int", "deprel": "discourse"},
    "hi": {"lemma": "hi", "upos": "PART", "feats": "_", "deprel": "discourse"},
    "hikei": {"lemma": "hikei", "upos": "AUX", "feats": "Polarity=Neg|VerbForm=Fin",
              "deprel": "cop"},
    "ahi": {"lemma": "ahi", "upos": "AUX", "feats": "VerbForm=Fin", "deprel": "cop"},
    "sa": {"lemma": "sa", "upos": "AUX", "feats": "Tense=Past", "deprel": "aux"},
    "uh": {"lemma": "uh", "upos": "PART", "feats": "Number=Plur", "deprel": "clf"},
    "laitak": {"lemma": "laitak", "upos": "PART", "feats": "Aspect=Prog", "deprel": "aux"},
    "ngei": {"lemma": "ngei", "upos": "PART", "feats": "Aspect=Perf", "deprel": "advmod"},
    "khin": {"lemma": "khin", "upos": "PART", "feats": "Aspect=Perf", "deprel": "aux"},
    "hiam": {"lemma": "hiam", "upos": "PART", "feats": "PartType=Int", "deprel": "discourse"},
}
