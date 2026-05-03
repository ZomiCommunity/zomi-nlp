# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.4.1] — 2026-05-03

### 📦 Changes

- docs(readme): Major documentation overhaul
  - Expanded feature list (lemmatization, morphological analysis, CoNLL‑U export)
  - Added Coming Soon section for v0.5.0+ (sense lexicon, WSD, nominalizer detector)
  - Introduced full native pipeline documentation with component table
  - Added CoNLL‑U export example and improved usage demo
  - Added CLI usage section with commands
  - Updated configuration examples to use unified parser_backend
  - Replaced roadmap list with structured version table
  - Added detailed planned features for v0.5.0
  - Added summary of changes section

- docs: Add example scripts (benchmark, quick demo, showcase) and Makefile target
- feat(cli): Add extended 16‑column CoNLL‑U output with metadata
- chore(ner): Remove print statements
- chore(ner): Remove obsolete commented code

### 📝 Summary

This patch release focuses on documentation quality, developer experience, and CLI output improvements. No breaking changes were introduced.


## [0.4.0] — 2026-04-27

### 📦 Changes
- chore(release): bump version to 0.4.0 and prepare release tag
- feat(dev-tools): add changelog generator and update Makefile
- refactor: Centralize morphological data in lexicons
- fix: Remove lemmatizer display from CLI
- feat: Add modular ZomiDependencyParser
- feat: Add Zomi native lemmatizer and rule-based NER
- feat: Add Zomi native POS tagger
- feat: Extract lexicon to separate module - Move base lexicon entries to native/lexicons/ - Move suffix/particle table to lexicons/ - Update parser to import from lexicons module - Prepare for future lexicon expansion
- feat: Add native tokenizer adapter
- docs(makefile): provide tree target for easier project inspection
- refactor: rename scripts to dev-tools
- feat: Add ZomiTokenizer native module
- refactor: Consolidate zomi_native_adapter.py
- refactor: rename zomi_rule_based_parser_backend.py to zomi_adapter.py
- feat(makefile): add version target to display current package version
- release: update CHANGELOG for 0.3.0 for stable release
- release: change version number in pyproject to 0.3.0 for stable release
- Merge pull request #2 from ZomiCommunity/dev

## [0.3.0] — 2026-04-25

### 📦 Changes
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


## [0.2.1] — 2026-04-23

### 📦 Changes
- release: update CHANGELOG for 0.3.0 for stable release
- release: change version number in pyproject to 0.3.0 for stable release
- Merge pull request #2 from ZomiCommunity/dev
- release: Prepare v0.3.0rc1
- chore(release): improve release-test.sh workflow
- docs: update README with installation and doctor instructions
- test: remove commented-out ZomiParser alias test
- feat: Add ZomiRuleBasedParser native backend
- merge: main into dev

## [0.2.0] — 2026-04-23

### 📦 Changes


## [0.1.6-alpha4] — 2026-04-23

### 📦 Changes
- docs: Update PyPI badge to live version v0.2.0
- fix: Correct pre-release detection for v0.2.0
- ci: Switch to PyPI API token authentication
- ci: Simplify release workflow, remove hynek action
- fix: Correct fetch-depth typo and body_path placement
- Merge pull request #1 from ZomiCommunity/dev
- docs: Add complete CHANGELOG with version history
- release: Bump version to 0.2.0 for stable release - Update pyproject.toml version to 0.2.0 - Update CHANGELOG.md with release notes - version.py reads version dynamically
- perf,fix: Share Stanza pipelines to prevent duplicate downloads\n Remove unsupported 'quiet' parameter from stanza.download() \n Add lemma processor to Stanza tagger pipeline - Add singleton manager for shared Stanza resources - All adapters now use shared pipelines - Reduces download/load time by 75% - stanza.download() doesn't accept 'quiet' parameter in v1.10.1 - Use verbose=False in Pipeline constructor instead - Add download tracking to prevent redundant downloads - StanzaTagger now requests 'tokenize,pos,lemma' - Enables proper lemmatization for all processed text - Consistent with Stanza's expected output
- style: Apply linting fixes to stanza_adapter and cli
- ci: Improve workflows with fallback and better error handling
- chore: update gitattributes
- build: add auto-help in makefile
- feat: add CLI entrypoint
- fix: correct type annotations in stanza adapter
- build: add minimal-install-dev target for editable installs and clarify recommended usage scenarios
- build: add quick_test to makefile
- chore: add release preparation and test release scripts
- build: format update for Makefile, space to tab
- build: modify pyproject.toml with updated project settings
- build: add initial Makefile
- doc: enhance README - Added requirements section - Added troubleshooting notes - Improved formatting for readability - Added more badges

## [0.1.6-alpha3] — 2026-04-23

### 📦 Changes
- chore: release v0.1.6-alpha4
- fix: correct release workflow for test upload
- fix: correct release workflow for release
- fix: correct release workflow for TestPyPI uploads

## [0.1.6-alpha2] — 2026-04-23

### 📦 Changes
- chore: release v0.1.6-alpha3
- fix: correct release workflow for TestPyPI uploads

## [0.1.6-alpha1] — 2026-04-23

### 📦 Changes
- chore: release v0.1.6-alpha2
- fix: sync pyproject version with latest release
- chore: release v0.1.0-alpha1
- style: apply ruff safe fix
- refactor: switch to PEP 621 versioning (Option A)

## [0.1.6] — 2026-04-23

### 📦 Changes
- chore: release v0.1.6-alpha1

## [0.1.5] — 2026-04-23

### 📦 Changes
- chore: release v0.1.6
- ci: replace deprecated readme-renderer check with twine check

## [0.1.4] — 2026-04-23

### 📦 Changes
- chore: release v0.1.5
- style: apply mypy fixes

## [0.1.3] — 2026-04-23

### 📦 Changes
- chore: release v0.1.4
- style: apply ruff safe fixes

## [0.1.2] — 2026-04-23

### 📦 Changes
- chore: release v0.1.3
- fix: resolve mypy errors across adapters and utils, add proper type annotations, unify TypedDicts, and improve optional spaCy/stanza handling

## [0.1.1] — 2026-04-22

### 📦 Changes
- chore: release v0.1.2
- fix: resolve Ruff warnings and clean up stanza/spacy availability checks
- style: apply ruff unsafe fixes

## [0.1.0-alpha1] — 2026-04-23

### 📦 Changes


## [0.1.0] — 2026-04-22

### 📦 Changes
- chore: release v0.1.0-alpha1
- style: apply ruff safe fix
- refactor: switch to PEP 621 versioning (Option A)
- chore: release v0.1.6-alpha1
- chore: release v0.1.6
- ci: replace deprecated readme-renderer check with twine check
- chore: release v0.1.5
- style: apply mypy fixes
- chore: release v0.1.4
- style: apply ruff safe fixes
- chore: release v0.1.3
- fix: resolve mypy errors across adapters and utils, add proper type annotations, unify TypedDicts, and improve optional spaCy/stanza handling
- chore: release v0.1.2
- fix: resolve Ruff warnings and clean up stanza/spacy availability checks
- style: apply ruff unsafe fixes
- chore: release v0.1.1
- fix(scripts): point VERSION_FILE to zomi_nlp/version.py instead of local path
- chore: update bump_version script
- feat(scripts): add bump_version script under zomi_nlp/scripts
- fix: Update github action workflow
- fix: Resolve pydocstyle conflicts in pyproject.toml
- fix: running linting fix

## [0.1.0] — 2026-04-22

### 🎉 Initial Release
- Initial project setup

