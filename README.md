# Zomi NLP

[![PyPI version](https://badge.fury.io/py/zomi-nlp.svg)](https://pypi.org/project/zomi-nlp/)
[![Python Versions](https://img.shields.io/pypi/pyversions/zomi-nlp.svg)](https://pypi.org/project/zomi-nlp/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/ZomiCommunity/zomi-nlp/actions/workflows/ci.yml/badge.svg)](https://github.com/ZomiCommunity/zomi-nlp/actions/workflows/ci.yml)

Natural Language Processing toolkit for the **Zomi language (Zopau)**.

## Features

- 🔤 **Tokenization** - Smart tokenization with clitic splitting, reduplication handling, and compound word support
- 🏷️ **POS Tagging** - Rule-based part-of-speech tagging with 600+ lexicon entries
- 📖 **Lemmatization** - Morphological lemmatization with clitic removal and affix stripping
- 🌲 **Dependency Parsing** - Grammatical structure analysis with Zomi-specific rules
- 📍 **Named Entity Recognition** - Entity extraction for PERSON, LOCATION, GPE, DATE, NUMERIC
- 🔬 **Morphological Analysis** - Morpheme segmentation and feature extraction
- 🔌 **Pluggable Backends** - Use native Zomi, spaCy, or Stanza backends
- 📊 **CoNLL-U Export** - Standard 10-column and extended 16-column formats
- 🚀 **Production Ready** - CI/CD, type hints, comprehensive testing

### Coming Soon (v0.5.0+)

- 🔤 **Word Sense Disambiguation** - Context-aware meaning disambiguation
- 📚 **Sense Lexicon** - Word sense inventory with examples
- 📈 **Statistical Disambiguation** - Frequency-based sense prediction
- 🏷️ **Sense Tagger** - Automatic sense annotation
- 🔧 **Nominalizer Detector** - Rule-based `-na` suffix detection with stem alternation handling

## Requirements

- Python 3.9 or higher
- pip (latest version recommended)

## Dependencies

Zomi NLP works with either spaCy or Stanza as backends. If both are installed,
it will prefer Stanza (more accurate) but fall back to spaCy (faster) if needed.

### Installation Options

### Minimal Installation (Native Only)

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
text = "Tuni an ka ne hi."
doc = nlp(text)

# Access tokens
for token in doc:
    print(f"{token.text}\t{token.pos_}\t{token.lemma_}\t{token.ent_type_ or 'N/A'}")

# Output:
# Tuni    DATE    tuni    DATE
# an      NOUN    an      N/A  
# ka      PRON    ka      N/A
# ne      VERB    ne      N/A
# hi      PART    hi      N/A
# .       PUNCT   .       N/A
```

## Native Pipeline Components

Zomi NLP v0.4.0 introduces a complete native pipeline with no external dependencies:
| Component                 | Description                                           |
|---------------------------|-------------------------------------------------------|
| ZomiTokenizer             | Clitic splitting, reduplication, compound words, punctuation |
| ZomiPOSTagger             | Rule-based POS tagging with 600+ lexicon entries     |
| ZomiLemmatizer            | Morphological lemmatization with irregular form handling |
| ZomiDependencyParser      | Zomi-specific dependency relations (nsubj, obj, case, etc.) |
| ZomiNER                   | Named entity recognition for 6+ entity types         |
| ZomiMorphologicalAnalyzer | Morpheme segmentation and feature extraction         |

## CoNLL-U Export

```python
from zomi_nlp import load

nlp = load()
doc = nlp("Ka pai ve.")

# Export to standard CoNLL-U format
for token in doc:
    print(f"{token.text}\t{token.lemma_}\t{token.pos_}\t{token.head}\t{token.dep_}")

# Output format: ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC
```

## Configuration

```
from zomi_nlp import ZomiConfig, ZomiPipeline

# Use native Zomi pipeline (default, no dependencies)
config = ZomiConfig(parser_backend="native")
nlp = ZomiPipeline(config)

# Use spaCy for speed
config = ZomiConfig(parser_backend="spacy")
nlp = ZomiPipeline(config)

# Use Stanza for accuracy
config = ZomiConfig(parser_backend="stanza")
nlp = ZomiPipeline(config)

# Auto-select best available
config = ZomiConfig(parser_backend="auto")
nlp = ZomiPipeline(config)
```

## CLI Usage

```bash
# Check installation status
zomi-nlp --check

# Diagnose issues
zomi-nlp --doctor

# Process text directly
zomi-nlp "Tuni ka pai ve."

# Output:
# Tuni     DATE     tuni
# ka       PRON     ka
# pai      VERB     pai
# hi       PART     hi
# .        PUNCT    .
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

| Version | Features                                   | Status      |
|---------|---------------------------------------------|-------------|
| v0.1.0  | Core architecture + spaCy/Stanza adapters   | ✅ Released |
| v0.2.0  | spaCy/Stanza backends                       | ✅ Released |
| v0.3.0  | ZomiRuleBasedParser                         | ✅ Released |
| v0.4.0  | Complete native pipeline                    | ✅ Current  |
| v0.5.0  | Word embeddings, sense disambiguation       | 🔜 Planned  |
| v0.6.0  | ML-based components                         | 🔜 Planned  |
| v1.0.0  | Production ready                            | 🔜 Planned  |

## Planned Features for v0.5.0

- ZomiWordSenseDisambiguator - Context-aware meaning disambiguation
- ZOMI_SENSE_LEXICON - Word sense inventory with examples
- StatisticalDisambiguator - Frequency-based sense prediction
- ZomiSenseTagger - Automatic sense annotation
- ZomiNominalizerDetector - Rule-based -na suffix detection with stem alternation handling (e.g., pia → piakna, um → upna)

## Contributing

Contributions welcome! See [CONTRIBUTING](CONTRIBUTING.md) for guidelines.

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


## 📝 Summary of Changes

| Section | Change |
|---------|--------|
| **Features** | Added lemmatization, morphological analysis, CoNLL-U export |
| **Coming Soon** | New section listing planned features (disambiguator, sense lexicon, etc.) |
| **Native Pipeline** | New section documenting all native components |
| **CoNLL-U Export** | New section with example |
| **CLI Usage** | New section with command examples |
| **Roadmap** | Converted to table format, marked v0.4.0 as current |
| **Planned Features** | Detailed list of v0.5.0 features including those you asked about |

The planned features section clearly indicates that **ZomiWordSenseDisambiguator**, **ZOMI_SENSE_LEXICON**, **StatisticalDisambiguator**, **ZomiSenseTagger**, and **ZomiNominalizerDetector** are coming in v0.5.0, not yet available in v0.4.0. 🚀