#!/usr/bin/env python3
"""Complete showcase of Zomi NLP capabilities.

Run: python examples/showcase_zomi_nlp.py
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path if running directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from zomi_nlp import ZomiConfig, ZomiPipeline, __version__
from zomi_nlp.native import (
    ZomiDependencyParser,
    ZomiLemmatizer,
    ZomiNER,
    ZomiPOSTagger,
    ZomiTokenizer,
    analyze_morphology,
)
from zomi_nlp.utils import check_installation


def print_header(title: str, char: str = "="):
    """Print a formatted header."""
    print(f"\n{char * 60}")
    print(f"  {title}")
    print(f"{char * 60}\n")


def showcase_basic_usage():
    """Show basic pipeline usage."""
    print_header("1. BASIC PIPELINE USAGE", "=")

    nlp = ZomiPipeline()

    texts = [
        "Ka pai ve.",
        "Na pai hi?",
        "Tuni ka pai ve.",
        "Pasian in leitung a piangsak hi.",
    ]

    for text in texts:
        doc = nlp(text)
        print(f"📝 Input: {text}")
        print(f"   Tokens: {[t.text for t in doc]}")
        print(f"   Tags:   {[t.pos_ for t in doc]}")
        print(f"   Lemmas: {[t.lemma_ for t in doc]}")
        print()


def showcase_tokenizer():
    """Show tokenizer capabilities."""
    print_header("2. TOKENIZER CAPABILITIES", "=")

    tokenizer = ZomiTokenizer()

    examples = [
        ("Basic tokens", "Ka pai ve."),
        ("Clitic splitting", "Ka zohve hi."),
        ("Reduplication", "mahmah"),
        ("Compound words", "sang-inn"),
        ("Multiple clitics", "kapiangsakve"),
        ("Question particles", "Na pai na hiam?"),
    ]

    for name, text in examples:
        tokens = tokenizer.tokenize(text)
        print(f"🔤 {name}:")
        print(f"   Input:  {text}")
        print(f"   Output: {tokens}\n")


def showcase_pos_tagger():
    """Show POS tagging capabilities."""
    print_header("3. POS TAGGING CAPABILITIES", "=")

    tagger = ZomiPOSTagger()
    tokenizer = ZomiTokenizer()

    sentences = [
        "Ka pai ve.",
        "Na pai hi?",
        "Amah piang hi.",
        "Sangnaupang khat ka hi hi.",
        "Eite pen sanginn pen ii sangnaupangte ih hikei uh hi.",
    ]

    for sentence in sentences:
        tokens = tokenizer.tokenize(sentence)
        tagged = tagger.tag_with_context(tokens)

        print(f"📝 Sentence: {sentence}")
        print(f"   {'Token':<15} {'POS':<12} {'Features'}")
        print(f"   {'-'*40}")
        for token, pos, feats in tagged:
            feats_display = feats if feats else "_"
            print(f"   {token:<15} {pos:<12} {feats_display}")
        print()


def showcase_lemmatizer():
    """Show lemmatization capabilities."""
    print_header("4. LEMMATIZER CAPABILITIES", "=")

    lemmatizer = ZomiLemmatizer()
    # tokenizer = ZomiTokenizer()

    examples = [
        ("zohve", "Verb with clitic"),
        ("kapiangsakve", "Full word with prefix+suffix"),
        ("sangnaupangte", "Plural noun"),
        ("hikei", "Negative copula"),
        ("mahmah", "Reduplicated"),
    ]

    print(f"{'Word':<20} {'Lemma':<15} {'Method':<12}")
    print("-" * 50)
    for word, _ in examples:
        # tokens = tokenizer.tokenize(word)
        # lemmas = lemmatizer.lemmatize(tokens)
        lemma, method = lemmatizer._get_lemma_with_method(word)
        print(f"{word:<20} {lemma:<15} {method:<12}")
    print()


def showcase_morphological_analyzer():
    """Show morphological analysis capabilities."""
    print_header("5. MORPHOLOGICAL ANALYZER", "=")

    words = [
        "kapiangsakve",
        "upna",
        "piakna",
        "sangnaupangte",
        "mahmah",
        "pasian",
    ]

    for word in words:
        result = analyze_morphology(word)
        print(f"🔬 Word: {result['word']}")
        print(f"   Root: {result['root']}")
        print(f"   POS:  {result['pos']}")
        print(f"   Features: {result['features']}")
        print(f"   Morphemes: {result['morphemes']}")
        if result['is_compound']:
            print("   ⚡ Compound: Yes")
        if result['is_reduplicated']:
            print("   🔄 Reduplicated: Yes")
        if result['has_clitic']:
            print("   🔗 Has clitic: Yes")
        print()


def show_ner():
    """Show Named Entity Recognition capabilities."""
    print_header("6. NAMED ENTITY RECOGNITION", "=")

    ner = ZomiNER()

    texts = [
        ("Pasian", "Person name"),
        ("Jerusalem", "Location"),
        ("Tedim", "GPE - Geo-political entity"),
        ("Tuni", "Date"),
        ("khat", "Number"),
    ]

    for text, desc in texts:
        entities = ner.extract(text)
        print(f"📍 {desc}: '{text}'")
        if entities:
            for ent in entities:
                print(f"   → Entity: {ent.text} (Type: {ent.type}, \
                      Confidence: {ent.confidence:.2f})")
        else:
            print("   → No entities found")
    print()


def show_dependency_parser():
    """Show dependency parsing capabilities."""
    print_header("7. DEPENDENCY PARSING", "=")

    parser = ZomiDependencyParser()
    tokenizer = ZomiTokenizer()
    tagger = ZomiPOSTagger()

    sentences = [
        "Ka pai ve.",
        "Pasian in leitung a piangsak hi.",
    ]

    for sentence in sentences:
        tokens = tokenizer.tokenize(sentence)
        pos_tags = [tag for _, tag, _ in tagger.tag_with_context(tokens)]

        dep_result = parser.parse(tokens, pos_tags)

        print(f"📝 Sentence: {sentence}")
        print(f"   {'ID':<4} {'Form':<15} {'POS':<8} {'Head':<6} {'Deprel'}")
        print(f"   {'-'*50}")
        for token in dep_result:
            print(f"   {token['id']:<4} {token['form']:<15} {token['upos']:<8} \
                  {token['head']:<6} {token['deprel']}")
        print()


def showcase_conllu_export():
    """Show CoNLL-U export capabilities."""
    print_header("8. CONLL-U EXPORT", "=")

    nlp = ZomiPipeline()

    sentences = [
        "Ka pai ve.",
        "Pasian in leitung a piangsak hi.",
        "Eite pen sanginn pen ii sangnaupangte ih hikei uh hi.",
    ]

    print("📋 CoNLL-U Format (10-column Universal Dependencies standard):")
    print("   COLs: ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC\n")

    for sentence in sentences:
        doc = nlp(sentence)

        print(f"# text = {sentence}")

        for i, token in enumerate(doc.tokens, 1):
            # Format: ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC
            conllu_line = "\t".join([
                str(i),                           # ID
                token.text,                       # FORM
                token.lemma_ or "_",              # LEMMA
                token.pos_ or "_",                # UPOS
                token.tag_ or "_",                # XPOS
                token.morph_to_string() if hasattr(token, 'morph_to_string') else "_",  # FEATS
                str(token.head) if token.head >= 0 else "0",  # HEAD
                token.dep_ or "_",                # DEPREL
                "_",                              # DEPS
                "_",                              # MISC
            ])
            print(conllu_line)

        print()  # Empty line between sentences

    # Also show how to export to file
    print_header("8a. EXPORT TO CONLL-U FILE", "-")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.conllu', delete=False) as f:
        for sentence in sentences:
            doc = nlp(sentence)
            f.write(f"# text = {sentence}\n")
            for i, token in enumerate(doc.tokens, 1):
                conllu_line = "\t".join([
                    str(i), token.text, token.lemma_ or "_",
                    token.pos_ or "_", "_",
                    token.morph_to_string() if hasattr(token, 'morph_to_string') else "_",
                    str(token.head) if token.head >= 0 else "0",
                    token.dep_ or "_", "_", "_"
                ])
                f.write(conllu_line + "\n")
            f.write("\n")

        print(f"💾 CoNLL-U file exported to: {f.name}")
        print(f"   File size: {Path(f.name).stat().st_size} bytes")
        print("\n   Sample content:")
        with open(f.name) as sample:
            lines = sample.readlines()[:10]
            for line in lines:
                print(f"   {line.rstrip()}")

    print()


def showcase_16_column_export():
    """Show 16-column CoNLL-U export (extended format)."""
    print_header("9. 16-COLUMN EXTENDED EXPORT", "=")

    nlp = ZomiPipeline()

    sentence = "Eite pen sanginn pen ii sangnaupangte ih hikei uh hi."
    doc = nlp(sentence)

    print("📊 Extended CoNLL-U Format (16 columns with metadata):")
    print("   COLs: ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC | \
          TEXT | TEXT_EN | GENRE | SOURCE | ANNOTATOR | STATUS\n")

    # Mock metadata for demonstration
    metadata = {
        "text_en": "We are not the students of the school.",
        "genre": "Bible",
        "source": "ZOM-BIBLE-001",
        "annotator": "ZomiNLP-v0.4.0",
        "status": "Final"
    }

    print(f"# text = {sentence}")
    print(f"# text_en = {metadata['text_en']}")
    print(f"# genre = {metadata['genre']}")
    print(f"# source = {metadata['source']}")
    print(f"# annotator = {metadata['annotator']}")
    print(f"# status = {metadata['status']}")

    for i, token in enumerate(doc.tokens, 1):
        # 16-column format
        conllu_line = "\t".join([
            str(i),                           # 1: ID
            token.text,                       # 2: FORM
            token.lemma_ or "_",              # 3: LEMMA
            token.pos_ or "_",                # 4: UPOS
            "_",                              # 5: XPOS
            token.morph_to_string() if hasattr(token, 'morph_to_string') else "_",  # 6: FEATS
            str(token.head) if token.head >= 0 else "0",  # 7: HEAD
            token.dep_ or "_",                # 8: DEPREL
            "_",                              # 9: DEPS
            "_",                              # 10: MISC
            sentence if i == 1 else "_",      # 11: TEXT (on first row)
            metadata['text_en'] if i == 1 else "_",  # 12: TEXT_EN
            metadata['genre'],                # 13: GENRE
            metadata['source'],               # 14: SOURCE
            metadata['annotator'],            # 15: ANNOTATOR
            metadata['status'],               # 16: STATUS
        ])
        print(conllu_line)

    print()


def show_cli_commands():
    """Show CLI commands."""
    print_header("10. CLI COMMANDS", "=")

    commands = [
        ("zomi-nlp --version", "Show version"),
        ("zomi-nlp --check", "Check installation status"),
        ("zomi-nlp --doctor", "Diagnose installation issues"),
        ("zomi-nlp 'Ka pai ve.'", "Process text directly"),
    ]

    print("💻 Available CLI commands:")
    for cmd, desc in commands:
        print(f"   {cmd:<35} # {desc}")
    print()


def show_backend_comparison():
    """Compare different backends."""
    print_header("11. BACKEND COMPARISON", "=")

    text = "Ka pai ve."

    backends = ["native", "spacy", "stanza"]

    for backend in backends:
        try:
            config = ZomiConfig(parser_backend=backend)
            nlp = ZomiPipeline(config)
            doc = nlp(text)
            print(f"🔧 Backend: {backend}")
            print(f"   Output: {' '.join([f'{t.text}({t.pos_})' for t in doc])}")
        except Exception as e:
            print(f"⚠️ Backend {backend} not available: {e}")
    print()


def show_nominalization_rules():
    """Show -na nominalization rules."""
    print_header("12. NOMINALIZATION RULES (-NA SUFFIX)", "=")

    examples = [
        ("it", "love (verb)", "itna", "love (noun)"),
        ("pia", "give (verb)", "piakna", "giving (noun)"),
        ("um", "believe (verb)", "upna", "belief (noun)"),
        ("zoh", "watch (verb)", "zohna", "watching (noun)"),
    ]

    print("🔍 Zomi -na Nominalization Pattern:")
    print(f"   {'Verb':<12} {'Meaning':<18} {'Noun':<12} {'Meaning'}")
    print(f"   {'-'*50}")
    for verb, verb_meaning, noun, noun_meaning in examples:
        print(f"   {verb:<12} {verb_meaning:<18} {noun:<12} {noun_meaning}")
    print()

    print("🧠 Stem alternation rules detected automatically!")
    print("   - pia → piak + na (insert 'k')")
    print("   - um → up + na (m → p)")
    print("   - it → it + na (no change)\n")


def show_particle_system():
    """Show particle system capabilities."""
    print_header("13. PARTICLE SYSTEM", "=")

    particles = {
        "ve": "Polite/Indicative",
        "ta": "Emphatic",
        "hiam": "Question particle",
        "maw": "Question (alternative)",
        "leh": "Conditional",
        "le": "Connective",
        "uh": "Plural marker",
        "hi": "Copular/Existence",
        "kei": "Negative",
        "loin": "Negative (alternative)",
        "hen": "Imperative",
        "ngei": "Perfective aspect",
        "khin": "Completed aspect",
    }

    print("📌 Zomi Particles and Their Functions:")
    print(f"   {'Particle':<10} {'Function'}")
    print(f"   {'-'*40}")
    for particle, func in particles.items():
        print(f"   {particle:<10} {func}")
    print()


def show_sentence_examples():
    """Show complete sentence examples with all annotations."""
    print_header("14. COMPLETE SENTENCE EXAMPLES", "=")

    nlp = ZomiPipeline()

    examples = [
        ("Simple statement", "Ka pai ve."),
        ("Question", "Na pai na hiam?"),
        ("Negative", "Ka pai kei hi."),
        ("With topic marker", "Eite pen ka pai ve."),
        ("Complex", "Pasian in vantung leh leitung a piangsak hi."),
    ]

    for name, sentence in examples:
        doc = nlp(sentence)
        print(f"📖 {name}: {sentence}")
        print()
        print(f"   {'Token':<15} {'POS':<10} {'Lemma':<12} {'Head':<6} {'Deprel':<12} {'Entity'}")
        print(f"   {'-'*70}")
        for token in doc:
            ent = token.ent_type_ or "N/A"
            dep = token.dep_ or "N/A"
            head = token.head if token.head >= 0 else "0"
            print(f"   {token.text:<15} {token.pos_ or 'N/A':<10} {token.lemma_ or 'N/A':<12} \
                  {head:<6} {dep:<12} {ent}")
        print()


def main():
    """Run the complete showcase."""
    print("\n" + "🎯" * 30)
    print("         ZOMI NLP - COMPLETE CAPABILITIES SHOWCASE")
    print("         Version: " + __version__)
    print("🎯" * 30)

    # Check installation first
    check_installation(verbose=False)

    # Run all showcases
    showcase_basic_usage()
    showcase_tokenizer()
    showcase_pos_tagger()
    showcase_lemmatizer()
    showcase_morphological_analyzer()
    show_ner()
    show_dependency_parser()
    showcase_conllu_export()      # NEW: CoNLL-U export
    showcase_16_column_export()   # NEW: 16-column extended format
    show_cli_commands()
    show_backend_comparison()
    show_nominalization_rules()
    show_particle_system()
    show_sentence_examples()

    print("\n" + "✅" * 30)
    print("         SHOWCASE COMPLETE!")
    print("         Zomi NLP is ready for production!")
    print("✅" * 30)
    print("\n📚 For more information:")
    print("   - GitHub: https://github.com/ZomiCommunity/zomi-nlp")
    print("   - PyPI: https://pypi.org/project/zomi-nlp/")
    print("   - Documentation: https://github.com/ZomiCommunity/zomi-nlp#readme")
    print("\n📊 Export Formats Supported:")
    print("   - CoNLL-U (10-column Universal Dependencies)")
    print("   - Extended CoNLL-U (16-column with metadata)")
    print("   - JSON")
    print("   - Plain text with annotations")
    print()


if __name__ == "__main__":
    main()
