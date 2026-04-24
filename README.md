# Zomi NLP

[![PyPI version](https://badge.fury.io/py/zomi-nlp.svg)](https://pypi.org/project/zomi-nlp/)
[![Python Versions](https://img.shields.io/pypi/pyversions/zomi-nlp.svg)](https://pypi.org/project/zomi-nlp/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/ZomiCommunity/zomi-nlp/actions/workflows/ci.yml/badge.svg)](https://github.com/ZomiCommunity/zomi-nlp/actions/workflows/ci.yml)

Natural Language Processing toolkit for the **Zomi language (Zopau)**.

## Features

- 🔤 **Tokenization** - Smart tokenization with Zomi clitic handling
- 🏷️ **POS Tagging** - Part-of-speech tagging
- 🌲 **Dependency Parsing** - Grammatical structure analysis
- 📍 **Named Entity Recognition** - Entity extraction
- 🔌 **Pluggable Backends** - Use spaCy, Stanza, or native implementations
- 🚀 **Production Ready** - CI/CD, type hints, comprehensive testing

## Requirements

- Python 3.9 or higher
- pip (latest version recommended)

## Dependencies

Zomi NLP works with either spaCy or Stanza as backends. If both are installed,
it will prefer Stanza (more accurate) but fall back to spaCy (faster) if needed.

### Installation Options

### Minimal Installation (Basic Tokenization Only)

```bash
pip install zomi-nlp
```

### With spaCy (Recommended for Speed)

```bash
pip install 'zomi-nlp[spacy]'
python -m spacy download en_core_web_sm
```

### With Stanza (Recommended for Accuracy)

```bash
pip install 'zomi-nlp[stanza]'
```

### Full installation (Both Backends)

```bash
pip install 'zomi-nlp[full]'
```

## Quick Start

```python
from zomi_nlp import load

# Load the pipeline (auto-selects best available backend)
nlp = load()

# Process text
text = "An ka ne hi."
doc = nlp(text)

# Access tokens
for token in doc:
    print(f"{token.text}\t{token.pos_}\t{token.lemma_}")

# Output:
# An      NOUN    an
# ka      PRON    ka
# ne      VERB    ne
# hi      PART    hi
# .       PUNCT   .
```

## Configuration

```
from zomi_nlp import ZomiConfig, ZomiPipeline

# Use spaCy for speed
config = ZomiConfig(tokenizer_backend="spacy", tagger_backend="spacy")
nlp = ZomiPipeline(config)

# Use Stanza for accuracy
config = ZomiConfig(tokenizer_backend="stanza", tagger_backend="stanza")
nlp = ZomiPipeline(config)

# Auto-select best available (recommended)
config = ZomiConfig(tokenizer_backend="auto")
nlp = ZomiPipeline(config)
```

## Checking Installation

```python
from zomi_nlp import check_installation

# Check what's installed
check_installation()

# Get status as dict
status = check_installation(verbose=False)
print(status)
```

## Troubleshooting

### "stanza not installed" Warning

If you see warnings about stanza, you have two options:

1. Install stanza (better accuracy):

```python
pip install stanza
```

2. Use spaCy instead (change your config):

```python
config = ZomiConfig(tokenizer_backend="spacy")
```

### "No backend available" Error

Install at least one backend:

```python
pip install 'zomi-nlp[full]'
```

### Getting `None` Values for POS Tags

This happens when no backend is available. The library falls back to a simple
tokenizer. Install spaCy or stanza for full functionality.

## Development

```bash
# Clone repository
git clone https://github.com/ZomiCommunity/zomi-nlp.git
cd zomi-nlp

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
ruff check zomi_nlp/

# Format code
black zomi_nlp/ tests/
```

## Roadmap

- v0.1.0 - Core architecture + spaCy/Stanza adapters
- v0.2.0 - Zomi-native tokenizer
- v0.3.0 - Zomi POS tagger
- v0.4.0 - Zomi dependency parser
- v1.0.0 - Fully native implementation

## Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.

## License

Apache License 2.0

## Citation

```bibtex
@software{zomi_nlp_2026,
  title={Zomi NLP: Natural Language Processing for Zomi Language},
  author={Zomi NLP Community},
  year={2026},
  url={https://github.com/ZomiCommunity/zomi-nlp}
}
```

## Acknowledgments

- Built with ❤️ for the Zomi community
- Uses spaCy and Stanza as backends
- Inspired by universal dependencies framework

### `Makefile`

```makefile
.PHONY: install install-dev test lint format clean build publish help

help:
	@echo "Available commands:"
	@echo "  install     - Install package"
	@echo "  install-dev - Install with dev dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linters"
	@echo "  format      - Format code"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build distribution"
	@echo "  publish     - Publish to PyPI"

install:
	pip install .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=zomi_nlp

lint:
	ruff check zomi_nlp/
	mypy zomi_nlp/ --ignore-missing-imports

format:
	black zomi_nlp/ tests/
	ruff check --fix zomi_nlp/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build
	twine check dist/*

publish: build
	twine upload dist/*

release: lint test build publish
	@echo "Release completed!"
```
