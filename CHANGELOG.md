# Changelog

All notable changes to the Zomi NLP library will be documented in this file.

## [0.3.0] - 2026-04-25

### Added
- **ZomiRuleBasedParser** - Complete rule-based Zomi NLP backend
  - 600+ lexicon entries
  - Clitic handling (`ve`, `ta`, `hiam`, etc.)
  - Dependency parsing with CoNLL-U output
  - Constituency tree generation
  - 16-column CoNLL-U export with metadata
- Native backend as primary parser
- `zomi-nlp --doctor` command for diagnostics
- Better error messages for missing dependencies

### Changed
- Auto-backend selection now prefers ZomiRuleBasedParser
- Improved fallback chain: native → stanza → spacy

### Fixed
- ZomiToken parameter naming consistency
- CLI argument parsing for `--doctor` command
- Backend adapter conversion to ZomiDoc

## [0.2.0] - 2026-04-23
### Added
- First stable release on official PyPI
- Complete spaCy backend (tokenization, POS, parsing, NER)
- Complete Stanza backend (tokenization, POS, parsing, NER, lemmatization)
- Shared Stanza pipeline to prevent duplicate downloads
- Comprehensive test suite (11/11 tests passing)
- GitHub Actions CI/CD pipeline
- CLI interface (`zomi-nlp` command)
- Installation helpers and utilities

### Fixed
- Stanza `download()` quiet parameter compatibility
- Proper lemmatization support in Stanza tagger
- Graceful fallback when backends unavailable
- Version management with dynamic reading from pyproject.toml

## v0.1.6-alpha4 - 2026-04-23

- fix: correct release workflow for test upload
- fix: correct release workflow for release
- fix: correct release workflow for TestPyPI uploads


## v0.1.6-alpha3 - 2026-04-23

- fix: correct release workflow for TestPyPI uploads


## v0.1.6-alpha2 - 2026-04-23

- fix: sync pyproject version with latest release


## v0.1.0-alpha1 - 2026-04-23

- style: apply ruff safe fix
- refactor: switch to PEP 621 versioning (Option A)


## v0.1.6-alpha1 - 2026-04-23




## v0.1.6 - 2026-04-23

- ci: replace deprecated readme-renderer check with twine check


## v0.1.5 - 2026-04-23

- style: apply mypy fixes


## v0.1.4 - 2026-04-23

- style: apply ruff safe fixes


## v0.1.3 - 2026-04-23

- fix: resolve mypy errors across adapters and utils, add proper type annotations, unify TypedDicts, and improve optional spaCy/stanza handling


## v0.1.2 - 2026-04-23

- fix: resolve Ruff warnings and clean up stanza/spacy availability checks
- style: apply ruff unsafe fixes


# Changelog

## v0.1.1 - 2026-04-22

- fix(scripts): point VERSION_FILE to zomi_nlp/version.py instead of local path
- chore: update bump_version script
- feat(scripts): add bump_version script under zomi_nlp/scripts
- fix: Update github action workflow
- fix: Resolve pydocstyle conflicts in pyproject.toml
- fix: running linting fix
