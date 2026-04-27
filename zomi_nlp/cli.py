# zomi_nlp/cli.py
"""Command-line interface for Zomi NLP."""

import argparse
import sys
from importlib.util import find_spec

from zomi_nlp import __version__
from zomi_nlp.utils import check_installation, check_spacy_model, get_installation_advice


def doctor_command():
    """Diagnose installation issues and suggest fixes."""
    print("\n🔍 Zomi NLP Diagnostic Tool")
    print("="*50)

    issues = []
    fixes = []

    # Check Python version
    py_version = sys.version_info
    if py_version < (3, 9):
        issues.append(f"Python {py_version.major}.{py_version.minor} is too old")
        fixes.append("Install Python 3.9 or higher")

    # Check native parser
    if find_spec("zomi_nlp.native.parser"):
        print("✅ Native parser: Available")
    else:
        print("❌ Native parser: Not available")

    # Check spaCy model
    try:
        import spacy
        try:
            spacy.load("en_core_web_sm")
            print("✅ spaCy: Installed with model")
        except OSError:
            issues.append("spaCy model 'en_core_web_sm' not found")
            fixes.append("python -m spacy download en_core_web_sm")
    except ImportError:
        issues.append("spaCy not installed")
        fixes.append("pip install spacy")

    # Check stanza
    if find_spec("stanza") is not None:
        print("✅ stanza: Installed (models download on first use)")
    else:
        issues.append("stanza not installed (optional, for better accuracy)")
        fixes.append("pip install stanza")

    # Show results
    if issues:
        print("\n⚠️ Issues found:\n")
        for issue in issues:
            print(f"  • {issue}")
        print("\n🔧 Suggested fixes:\n")
        for fix in fixes:
            print(f"  • {fix}")
    else:
        print("\n✅ All systems ready!")

    print("\n" + "="*50)
    print("For more help: https://github.com/ZomiCommunity/zomi-nlp")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Zomi NLP - Natural Language Processing for Zomi Language"
    )

    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"Zomi NLP {__version__}"
    )

    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="Check installation status"
    )

    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Diagnose installation issues and suggest fixes"  # ← Moved BEFORE parse_args
    )

    parser.add_argument(
        "text",
        nargs="?",
        help="Text to process"
    )

    args = parser.parse_args()

    if args.doctor:
        doctor_command()
        return

    if args.check:
        print("\n" + "="*50)
        print("Zomi NLP Installation Status")
        print("="*50)
        check_installation()

        # Check spaCy model specifically
        spacy_status = check_spacy_model()
        if not spacy_status.get("available", False):
            print(f"\n⚠️ spaCy model '{spacy_status.get('model', 'en_core_web_sm')}' missing")
            fix_command = 'python -m spacy download en_core_web_sm'
            print(f"   Run: {spacy_status.get('fix_command', fix_command)}")

        # Show general advice
        print("\n📦 To use all features:\n")
        print(get_installation_advice())
        return

    if args.text:
        from zomi_nlp import ZomiPipeline
        nlp = ZomiPipeline()
        print(f"Tokenizer: {nlp.tokenizer.__class__.__name__}")
        print(f"Tagger: {nlp.tagger.__class__.__name__}")
        print(f"Parser: {nlp.parser.__class__.__name__}")
        print(f"NER: {nlp.ner.__class__.__name__}")

        print("\nProcessing text...\n")
        doc = nlp(args.text)
        print(f"\n{'Token'}\t{'POS'}\t{'Lemma'}\t{'Entity'}\t{'Dep'}\t{'Morph'}\t{'Features'}")
        for token in doc:
            print(f"{token.text}\
                  \t{token.pos_ or 'N/A'}\
                  \t{token.lemma_ or 'N/A'}\
                  \t{token.ent_type_ or 'N/A'}\
                  \t{token.dep_ or 'N/A'}\
                  \t{token.morph or 'N/A'}\
                  \t{token.feats or 'N/A'}")
        return

    # No arguments, show help
    parser.print_help()


if __name__ == "__main__":
    main()
