# zomi-nlp/zomi_nlp/native/_reference_parser.py
"""Zomi Rule-Based Parser - Complete NLP using linguistic rules.

This parser implements traditional NLP techniques:
- Lexicon-based word analysis
- Rule-based morphological processing
- Heuristic dependency parsing
- Pattern-based constituency trees

No machine learning, no external dependencies - just pure Zomi linguistics.
"""

import re
from collections import defaultdict

from zomi_nlp.native.lexicons import ZOMI_LEXICON, ZOMI_SUFFIXES


class ZomiReferenceParser:
    """Zomi Reference Parser - Complete NLP using linguistic rules.

    This parser uses:
    - Lexicon lookup (600+ entries)
    - Suffix/particle rules
    - Dependency heuristics
    - Constituency patterns

    No ML, no external dependencies - pure rule-based Zomi NLP.
    """

    def __init__(self):
        # 1. Lexicon: The semantic truth
        self.lexicon = ZOMI_LEXICON
        # 2. Suffix Table: The morphological toolkit
        self.suffix_table = ZOMI_SUFFIXES

    def analyze_morphology(self, token):
        t = token.lower()
        if t in [".", "?", "!", ","]:
            return t, "PUNCT", "_", "punct"
        if t in self.lexicon:
            d = self.lexicon[t]
            return t, d['upos'], d['feats'], d.get('deprel', 'dep')
        if t in self.suffix_table:
            d = self.suffix_table[t]
            print(d)
            return t, d['upos'], d['feats'], d['deprel']

        # Handle 'ci-a' and other complex forms
        if t == "ci-a":
            return "ci", "VERB", "VerbForm=Ger", "advcl"
        if t == "tu-in":
            return "tu-in", "NOUN", "_", "obl:tmod"

        return t, "NOUN", "_", "dep"


    def assign_complex_heads(self, parsed):
        # 1. Clear previous heads to prevent legacy loops
        for t in parsed:
            t['head'] = 0
            t['deprel'] = 'root' if t['tag'] in ['VERB', 'AUX', 'ADJ'] else '_'

        # 2. Identify the Absolute Root (The final predicate)
        root_id = None
        for tok in reversed(parsed):
            if tok['tag'] in ['VERB', 'AUX', 'ADJ']:
                root_id = tok['id']
                tok['head'] = 0
                tok['deprel'] = 'root'
                break

        if not root_id:
            return parsed # Safety for fragments

        # 3. Structural Linkage
        for i, tok in enumerate(parsed):
            if tok['id'] == root_id:
                continue

            # Case A: Grammatical Markers (ADP, PART, DET)
            # These attach to the word BEFORE them
            if tok['tag'] in ['ADP', 'PART', 'DET'] and i > 0:
                tok['head'] = parsed[i-1]['id']
                # UD standard labeling
                form = tok['form'].lower()
                if form in ('in', 'ii'):
                    tok['deprel'] = 'case'
                elif form == 'pen':
                    tok['deprel'] = 'mark'
                else:
                    tok['deprel'] = 'discourse'

            # Case B: Verbal Auxiliaries/Particles following the Root
            elif tok['tag'] in ['AUX', 'PART'] and tok['id'] > root_id:
                tok['head'] = root_id
                tok['deprel'] = 'aux' if tok['tag'] == 'AUX' else 'discourse'

            # Case C: Nouns/Pronouns/Numbers
            # These MUST point to the Root to be included in the Sbar
            elif tok['tag'] in ['NOUN', 'PRON', 'PROPN', 'NUM']:
                tok['head'] = root_id
                tok['deprel'] = 'nsubj' if tok['id'] < root_id else 'obj'

        return parsed


    # Pseudo-logic for your Dependency Parser
    def assign_dependencies(self, tokens):
        # Find the primary anchor (the last AUX or VERB before punctuation)
        anchor_id = None
        for tok in reversed(tokens):
            if tok['tag'] in ['VERB', 'AUX', 'ADJ'] and tok['tag'] != 'PUNCT':
                anchor_id = tok['id']
                tok['head'] = 0
                tok['deprel'] = 'root'
                break

        # Now, ensure nouns and pronouns point to this anchor
        for tok in tokens:
            if tok['id'] == anchor_id:
                continue
            if tok['tag'] in ['NOUN', 'PRON', 'NUM']:
                tok['head'] = anchor_id
                tok['deprel'] = 'nsubj' # or 'obj' / 'attr' based on context



    def generate_constituency_tuple(self, parsed_list):
        punct_tokens = [t for t in parsed_list if t['tag'] == 'PUNCT']
        structural_tokens = [t for t in parsed_list if t['tag'] != 'PUNCT']
        tokens_dict = {t['id']: t for t in structural_tokens}
        children_of = defaultdict(list)
        for t in structural_tokens:
            children_of[t['head']].append(t['id'])


        def build_phrase(head_id, blacklist=None):
            if blacklist is None:
                blacklist = []
            head_tok = tokens_dict[head_id]
            child_ids = [cid for cid in children_of[head_id] if cid not in blacklist]

            form_out = head_tok['form'].lower().replace("ci-a", "ci")

            # 1. LEAF NODE: If no children, return the raw tag/form (No NP wrapping!)
            if not child_ids:
                return (head_tok['tag'], form_out, head_tok['feats'])

            # 2. RECURSIVE STEP: Build the children
            all_ids = sorted(child_ids + [head_id])
            members = [build_phrase(tid, blacklist) if tid != head_id else
                      (head_tok['tag'], form_out, head_tok['feats']) for tid in all_ids]

            # 3. LABELING HEURISTIC
            child_forms = [tokens_dict[cid]['form'].lower() for cid in child_ids]

            # Priority 1: Specific Zomi Phrase Labels
            if any("Topic=Yes" in tokens_dict[cid]['feats'] for cid in child_ids):
                label = "NP-TPC"
            elif 'in' in child_forms:
                label = "NP-nsubj"
            elif 'ii' in child_forms:
                # Check if the head noun is acting as a subject
                label = "NP-SBJ" if head_tok['deprel'] in ['nsubj', 'nsubj:pass'] else "NP-poss"

            # Priority 2: Standard Phrase Labels
            elif head_tok['tag'] in ['VERB', 'AUX', 'ADJ']:
                label = "VP"
            elif head_tok['tag'] in ['NOUN', 'PRON', 'PROPN']:
                label = "NP"

            # Priority 3: Fallback (Prevents 'NP' for isolated particles)
            else:
                label = head_tok['tag']

            return tuple([label] + members)
        # 1. Partition the Root's children
        root_id = next((t['id'] for t in structural_tokens if t['head'] == 0), None)
        root_children = children_of[root_id]

        # promoted = Subjects/Objects; internal = Aux/Particles
        promoted_ids = [cid for cid in root_children if tokens_dict[cid]['tag']
                        not in ['AUX', 'PART']]

        # 2. Build the Sbar Siblings
        top_level_items = []
        for pid in promoted_ids:
            top_level_items.append((pid, build_phrase(pid)))
        # Add the VP (The Root itself + its internal particles)
        top_level_items.append((root_id, build_phrase(root_id, blacklist=promoted_ids)))

        # Sort by ID to maintain correct Zomi SOV order
        top_level_items.sort(key=lambda x: x[0])
        tree = ['Sbar'] + [item[1] for item in top_level_items]

        if punct_tokens:
            tree.append(('Punct', punct_tokens[0]['form'], '_'))

        return tuple(tree)

    def parse(self, sentence):
        tokens = re.findall(r"[\w-]+|[.,!?;]", sentence)
        parsed = []

        # 1. Individual Morphological Analysis
        for i, t in enumerate(tokens):
            lemma, tag, feats, deprel = self.analyze_morphology(t)
            parsed.append({
                'id': i+1, 'form': t, 'lemma': lemma,
                'tag': tag, 'feats': feats, 'deprel': deprel,
                'head': 0  # Default to 0, will be updated below
            })

        # 2. Contextual Overrides (Existing Logic)
        for i in range(len(parsed)-1):
            if parsed[i]['form'].lower() == 'pen' and parsed[i+1]['form'].lower() == 'ii':
                parsed[i]['tag'] = 'DET'
                parsed[i]['feats'] = 'PronType=Art'
                parsed[i]['deprel'] = 'det'

        # 3. Establish the ROOT Anchor (The "Future-Proof" fix)
        # Find the last word that acts as a predicate (VERB, AUX, or ADJ)
        anchor_id = None
        for token in reversed(parsed):
            if token['tag'] in ['VERB', 'AUX', 'ADJ']:
                anchor_id = token['id']
                token['head'] = 0
                token['deprel'] = 'root'
                break

        # 4. Connect Nouns/Pronouns to the Anchor
        # This prevents the "Swallowing" in Tests 11 & 12
        if anchor_id:
            for token in parsed:
                if token['id'] != anchor_id and token['tag'] in ['NOUN', 'PRON', 'PROPN']:
                    token['head'] = anchor_id
                    # Heuristic: if it's before the verb, it's usually a subject/object
                    token['deprel'] = 'nsubj'

        # 5. Final Structure Refinement
        parsed = self.assign_complex_heads(parsed)
        return parsed

    def print_standard_tree(self, sentence):
        parsed_data = self.parse(sentence)
        tree_tuple = self.generate_constituency_tuple(parsed_data)

        def stringify(node, level=0):
            # Leaf Node: (TAG, FORM, FEATS) -> We only display (TAG FORM)
            if isinstance(node, tuple) and len(node) == 3 and isinstance(node[1], str):
                return f"({node[0]} {node[1]})"

            # Phrase Node: (Label, children...)
            label = node[0]
            parts = [stringify(child, level + 1) for child in node[1:]]

            # Determine if we should put children on a new line
            if len(parts) > 1:
                nested_indent = "\n" + "  " * (level + 1)
                return f"({label}{nested_indent}{nested_indent.join(parts)})"
            else:
                return f"({label} {parts[0]})"

        print("\n# Standard Treebank Output")
        print(stringify(tree_tuple))

    def export_to_zomi_conllu(self, parser, test_cases, filename="zomi_corpus.conllu"):
        conllu_lines = []

        # Define the 16 headers
        headers = ["ID", "FORM", "LEMMA", "UPOS", "XPOS", "FEATS", "HEAD", "DEPREL",
                  "DEPS", "MISC", "TEXT", "TEXT_EN", "GENRE", "SOURCE", "ANNOTATOR", "STATUS"]

        for i, (zomi, eng, _) in enumerate(test_cases, 1):
            # 1. Parse the sentence to get the token dictionaries
            parsed_tokens = parser.parse(zomi)

            # 2. Add CoNLL-U Metadata Comments (Standard Practice)
            conllu_lines.append(
                f"# sent_id = ZOM-{'BIBLE' if 'Pasian' in zomi else 'DAILY'}-{i:03d}")
            conllu_lines.append(f"# text = {zomi}")
            conllu_lines.append(f"# text_en = {eng}")

            # 3. Generate the 16-column rows
            for token in parsed_tokens:
                # Map values to the user's specific 16-column layout
                row = [
                    str(token['id']),
                    token['form'],
                    token['lemma'],
                    token['tag'],
                    "_",                        # XPOS
                    token['feats'],
                    str(token['head']),
                    token['deprel'],
                    "_",                        # DEPS
                    "_",                        # MISC
                    # TEXT (only on first row for readability)
                    zomi if token['id'] == 1 else "_",
                    eng if token['id'] == 1 else "_",      # TEXT_EN
                    "Bible" if "Pasian" in zomi else "Edu", # GENRE
                    f"S-{i}",                   # SOURCE
                    "Gemini-3.6-Flash",         # ANNOTATOR
                    "Final"                     # STATUS
                ]
                conllu_lines.append("\t".join(row))

            # Add a newline between sentences
            conllu_lines.append("")

        # Write to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\t".join(headers) + "\n") # Optional header row for CSV/Excel compatibility
            f.write("\n".join(conllu_lines))

        print(f"✅ Success! {len(test_cases)} sentences exported to {filename}")

# Aliases for compatibility
# ZomiParser = ZomiRuleBasedParser
# Original development version if you want to keep the old one unchanged
ZomiReferenceParserV362 = ZomiReferenceParser
