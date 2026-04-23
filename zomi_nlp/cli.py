# zomi_nlp/cli.py
"""Command-line interface for Zomi NLP."""

import argparse

from zomi_nlp import __version__
from zomi_nlp.utils import check_installation


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
        "text",
        nargs="?",
        help="Text to process"
    )

    args = parser.parse_args()

    if args.check:
        check_installation()
        return
    if args.text:
        from zomi_nlp import ZomiPipeline
        nlp = ZomiPipeline()
        doc = nlp(args.text)
        for token in doc:
            print(f"{token.text}\t{token.pos_ or 'N/A'}\t{token.lemma_ or 'N/A'}")
        return
    # No arguments, show help
    parser.print_help()


if __name__ == "__main__":
    main()
