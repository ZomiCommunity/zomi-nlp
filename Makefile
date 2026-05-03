
# -----------------------------
# Zomi NLP Project Makefile
# -----------------------------

# Default target
.DEFAULT_GOAL := help

# Colors for pretty output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help install install-dev test test-all lint format clean clean-all build publish release check pre-commit

# -----------------------------
# High-level commands
# -----------------------------

help: ## Show this help message
	@echo "Auto‑generated help:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "%-25s %s\n", $$1, $$2}'

# 	@echo ""
# 	@echo "$(BLUE)Available commands:$(NC)"
# 	@echo "  $(GREEN)install$(NC)      - Install package"
# 	@echo "  $(GREEN)install-dev$(NC)  - Install with dev dependencies"
# 	@echo "  $(GREEN)minimal-install-dev$(NC)  - Install with minimal dev dependencies"
# 	@echo "  $(GREEN)quick-test$(NC)   - Run quick tests"
# 	@echo "  $(GREEN)test$(NC)         - Run tests"
# 	@echo "  $(GREEN)test-all$(NC)     - Run tests on all Python versions (tox)"
# 	@echo "  $(GREEN)lint$(NC)         - Run linters"
# 	@echo "  $(GREEN)format$(NC)       - Format code"
# 	@echo "  $(GREEN)check$(NC)        - Run all checks (lint + test)"
# 	@echo "  $(GREEN)pre-commit$(NC)   - Run pre-commit hooks"
# 	@echo "  $(GREEN)clean$(NC)        - Clean build artifacts"
# 	@echo "  $(GREEN)clean-all$(NC)    - Deep clean (including venv)"
# 	@echo "  $(GREEN)build$(NC)        - Build package distribution (wheel + sdist)"
# 	@echo "  $(GREEN)publish$(NC)      - Publish to PyPI"
# 	@echo "  $(GREEN)bump-version$(NC) - Bump package version"
# 	@echo "  $(GREEN)test-release$(NC) - Build and upload a timestamped dev version to TestPyPI"
# 	@echo "  $(GREEN)release$(NC)      - Full release (lint + test + build + publish)"
# 	@echo "  $(GREEN)tag$(NC)          - Create and push a git tag"
# 	@echo "  $(GREEN)change-log$(NC)      - Generate CHANGELOG.md from git history"
# 	@echo "  $(GREEN)prep-release$(NC)    - Run release prep script (bump version, update changelog, tag)"
# 	@echo "  $(GREEN)sanity-check-commit$(NC) - Check commit before pushing (git status + diff)"
# 	@echo ""

# -----------------------------
# Development commands
# -----------------------------


install: ## Install package
	@echo "$(GREEN)Installing package...$(NC)"
	pip install .

install-dev: ## Install with dev dependencies
	@echo "$(GREEN)Installing with dev dependencies...$(NC)"
	pip install -e ".[dev]"

###############################################################################
# This target is for users who want to contribute but don't need all the heavy dependencies for testing, linting, etc. It installs only the core dev dependencies needed for development and quick testing.
# ✅ YES - Run this: pip install -e .
# - Create NEW Python file | Package metadata needs update
# - Add new optional dependency (e.g. stanza) | Update install-dev and minimal-install-dev
# - Delete a Python file | Package structure changed
# - Refactor code | Package structure changed
# - Move/rename a file | Package structure changed
# - Edit pyproject.toml | Package metadata needs update, Dependencies or config changed
# - Edit README.md | Package metadata needs update
# - Add new dependency | Need to install new package
# - Change entry points/scripts | CLI commands need update
# - Add new data files | Package data needs inclusion, Package structure changed, Need to include new files in distribution
# touch zomi_nlp/new_file.py                    # New file created
# rm zomi_nlp/old_file.py                       # File deleted
# mv zomi_nlp/file.py zomi_nlp/moved.py         # File moved
# nano pyproject.toml                           # Changed config
# pip install numpy                             # Added to dependencies

# # ❌ NO - Don't need to run:
# nano zomi_nlp/existing_file.py                # Edit existing file
# python test_local.py                          # Run tests
# git commit                                    # Git operations
# pytest                                        # Run test suite
###############################################################################
minimal-install-dev: ## Install minimal editable dev environment
	@echo "$(GREEN)Installing with dev minimal...$(NC)"
	pip install -e .

quick-test: ## Run quick tests (smoke test, basic functionality)
	@echo "$(GREEN)Running quick tests...$(NC)"
	python3 temp/quick_test.py
	@echo "$(GREEN)Quick tests complete!$(NC)"

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	pytest tests/ -v --cov=zomi_nlp --cov-report=term --cov-report=html
	@echo "$(GREEN)Tests complete! Coverage report: htmlcov/index.html$(NC)"

test-all: ## Run tests on all Python versions
	@echo "$(GREEN)Running tests on all Python versions...$(NC)"
	tox

lint: ## Lint code
	@echo "$(YELLOW)Linting code...$(NC)"
	ruff check .
	mypy zomi_nlp/ --ignore-missing-imports
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code
	@echo "$(YELLOW)Formatting code...$(NC)"
	black zomi_nlp/ tests/
	ruff check --fix zomi_nlp/
	@echo "$(GREEN)Formatting complete!$(NC)"

check: lint test ## Run all checks (lint + test)
	@echo "$(GREEN)✓ All checks passed!$(NC)"

pre-commit: ## Run pre-commit hooks
	@echo "$(YELLOW)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)Pre-commit complete!$(NC)"

# -----------------------------
# Build commands
# -----------------------------

clean: ## Clean build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)Clean complete!$(NC)"

clean-all: clean ## Deep clean (includes virtual environment)
	@echo "$(YELLOW)Deep cleaning...$(NC)"
	rm -rf .venv/
	rm -rf .tox/
	rm -rf .pytest_cache/
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Deep clean complete!$(NC)"

build: clean ## Build package distribution (wheel + sdist)
	@echo "$(GREEN)Building package distribution...$(NC)"
	python -m build
	twine check dist/*
	@echo "$(GREEN)Build complete!$(NC)"

publish: build ## Publish to PyPI
	@echo "$(GREEN)Publishing to PyPI...$(NC)"
	twine upload dist/*
	@echo "$(GREEN)Published successfully!$(NC)"

# -----------------------------
# Version bumping
# -----------------------------
# Usage: make bump-version part=patch|minor|major
bump-version: ## Bump package version (patch, minor, major)
	@echo "$(BLUE)Bumping version...$(NC)"
	@if [ -z "$(part)" ]; then part=patch; else part=$(part); fi; \
	current=$$(grep '^version' pyproject.toml | sed -E 's/version = "([^"]+)"/\1/'); \
	echo "Current version: $$current"; \
	IFS='.-' read -r major minor patch extra <<< "$$current"; \
	case "$$part" in \
		patch) patch=$$((patch + 1));; \
		minor) minor=$$((minor + 1)); patch=0;; \
		major) major=$$((major + 1)); minor=0; patch=0;; \
		*) echo "$(RED)Invalid part: $(part). Use patch|minor|major$(NC)"; exit 1;; \
	esac; \
	new_version="$$major.$$minor.$$patch"; \
	echo "New version: $$new_version"; \
	sed -i.bak -E "s/version = \".+\"/version = \"$$new_version\"/" pyproject.toml; \
	rm pyproject.toml.bak; \
	echo "$(GREEN)Version bumped to $$new_version$(NC)"


# -----------------------------
# Release commands
# -----------------------------

test-release: ## Build and upload a timestamped dev version to TestPyPI
	@echo "$(GREEN)Running TestPyPI release...$(NC)"
	./zomi_nlp/scripts/release-test.sh

# -----------------------------
# Full PyPI Release
# -----------------------------

release: ## Usage: make release
	@echo "$(BLUE)Preparing full PyPI release...$(NC)"
	@version=$$(grep '^version' pyproject.toml | sed -E 's/version = "([^"]+)"/\1/'); \
	if echo "$$version" | grep -Eq 'dev|alpha|beta|rc'; then \
		echo "$(RED)Refusing to release pre-release version ($$version) to PyPI.$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)Releasing version $$version to PyPI$(NC)"
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) build
	$(MAKE) publish
	@echo "$(GREEN)🎉 Release $$version completed successfully! 🎉$(NC)"


# -----------------------------
# Git Tagging
# -----------------------------

tag: ## Create and push a git tag based on the current version in pyproject.toml
	@echo "$(BLUE)Creating git tag...$(NC)"
	@version=$$(grep '^version' pyproject.toml | sed -E 's/version = "([^"]+)"/\1/'); \
	if echo "$$version" | grep -Eq 'dev|alpha|beta|rc'; then \
		echo "$(RED)Refusing to tag pre-release version ($$version).$(NC)"; \
		exit 1; \
	fi; \
	tag="v$$version"; \
	if git rev-parse "$$tag" >/dev/null 2>&1; then \
		echo "$(RED)Tag $$tag already exists.$(NC)"; \
		exit 1; \
	fi; \
	echo "Tagging $$tag"; \
	git tag "$$tag"; \
	git push origin "$$tag"; \
	echo "$(GREEN)✓ Tag $$tag created and pushed!$(NC)"

# -----------------------------
# Auto-generate CHANGELOG
# -----------------------------

# In Makefile, replace your changelog target with:

.PHONY: changelog
changelog: ## Generate CHANGELOG.md entry from git history since last tag
	@echo "$(BLUE)Generating changelog entry...$(NC)"
	@# Get the latest tag
	@latest_tag=$$(git describe --tags --abbrev=0 2>/dev/null || echo ""); \
	previous_tag=$$(git describe --tags --abbrev=0 $$latest_tag^ 2>/dev/null || echo ""); \
	version=$$(echo $$latest_tag | sed 's/^v//'); \
	\
	if grep -q "## \[$$version\]" CHANGELOG.md; then \
		echo "$(YELLOW)Changelog for version $$version already exists.$(NC)"; \
		exit 1; \
	fi; \
	\
	echo "Creating changelog for version $$version (since $$previous_tag)"; \
	\
	# Categorize commits
	feats=$$(git log $$previous_tag..$$latest_tag --pretty=format:"- %s" | grep -E '^(feat|feature|add|new)' || echo ""); \
	fixes=$$(git log $$previous_tag..$$latest_tag --pretty=format:"- %s" | grep -E '^(fix|bug|resolve|correct)' || echo ""); \
	docs=$$(git log $$previous_tag..$$latest_tag --pretty=format:"- %s" | grep -E '^(docs|doc|readme)' || echo ""); \
	refactor=$$(git log $$previous_tag..$$latest_tag --pretty=format:"- %s" | grep -E '^(refactor|clean|rename|move)' || echo ""); \
	tests=$$(git log $$previous_tag..$$latest_tag --pretty=format:"- %s" | grep -E '^(test|spec)' || echo ""); \
	ci=$$(git log $$previous_tag..$$latest_tag --pretty=format:"- %s" | grep -E '^(ci|cd|action|workflow)' || echo ""); \
	\
	# Insert at top of CHANGELOG.md
	{ \
		echo "## [$$version] — $$(date +%Y-%m-%d)"; \
		echo ""; \
		if [ -n "$$feats" ]; then \
			echo "### ✨ New Features"; \
			echo "$$feats"; \
			echo ""; \
		fi; \
		if [ -n "$$fixes" ]; then \
			echo "### 🐛 Bug Fixes"; \
			echo "$$fixes"; \
			echo ""; \
		fi; \
		if [ -n "$$docs" ]; then \
			echo "### 📚 Documentation"; \
			echo "$$docs"; \
			echo ""; \
		fi; \
		if [ -n "$$refactor" ]; then \
			echo "### 🔧 Refactoring"; \
			echo "$$refactor"; \
			echo ""; \
		fi; \
		if [ -n "$$tests" ]; then \
			echo "### ✅ Tests"; \
			echo "$$tests"; \
			echo ""; \
		fi; \
		if [ -n "$$ci" ]; then \
			echo "### ⚙️ CI/CD"; \
			echo "$$ci"; \
			echo ""; \
		fi; \
		if [ -z "$$feats$$fixes$$docs$$refactor$$tests$$ci" ]; then \
			echo "### 📦 Other Changes"; \
			git log $$previous_tag..$$latest_tag --pretty=format:"- %s" || echo ""; \
			echo ""; \
		fi; \
		echo "---"; \
		echo ""; \
		cat CHANGELOG.md; \
	} > CHANGELOG.new && mv CHANGELOG.new CHANGELOG.md; \
	echo "$(GREEN)✓ Changelog updated for version $$version$(NC)"

.PHONY: changelog-full
changelog-full: ## Generate full changelog from all tags
	@echo "$(BLUE)Generating full changelog from all tags...$(NC)"
	@> CHANGELOG.md
	@echo "# Changelog" > CHANGELOG.md
	@echo "" >> CHANGELOG.md
	@echo "All notable changes to this project will be documented in this file." >> CHANGELOG.md
	@echo "" >> CHANGELOG.md
	@echo "The format is based on [Keep a Changelog](https://keepachangelog.com/)." >> CHANGELOG.md
	@echo "" >> CHANGELOG.md
	@tags=$$(git tag -l | sort -V -r); \
	prev=""; \
	for tag in $$tags; do \
		if [ -n "$$prev" ]; then \
			version=$$(echo $$tag | sed 's/^v//'); \
			echo "## [$$version] — $$(git log -1 --format=%ad --date=short $$tag)" >> CHANGELOG.md; \
			echo "" >> CHANGELOG.md; \
			echo "### 📦 Changes" >> CHANGELOG.md; \
			git log $$tag..$$prev --pretty=format:"- %s" >> CHANGELOG.md; \
			echo "" >> CHANGELOG.md; \
			echo "" >> CHANGELOG.md; \
		fi; \
		prev=$$tag; \
	done; \
	# First release \
	if [ -n "$$prev" ]; then \
		version=$$(echo $$prev | sed 's/^v//'); \
		echo "## [$$version] — $$(git log -1 --format=%ad --date=short $$prev)" >> CHANGELOG.md; \
		echo "" >> CHANGELOG.md; \
		echo "### 🎉 Initial Release" >> CHANGELOG.md; \
		echo "- Initial project setup" >> CHANGELOG.md; \
		echo "" >> CHANGELOG.md; \
	fi; \
	echo "$(GREEN)✓ Full changelog generated$(NC)"


# Usage: make prep-release part=patch|minor|major
prep-release: ## Run release prep script (bump version, update changelog, tag)
	@echo "$(BLUE)Running release prep...$(NC)"
	./zomi_nlp/scripts/prep-release.sh part=$(part)

sanity-check-commit: ## Show git status, unstaged diff, and staged diff
	@echo "=== Git Status ==="
	@git status
	@echo ""
	@echo "=== Unstaged Changes (git diff) ==="
	@git diff
	@echo ""
	@echo "=== Staged Changes (git diff --cached) ==="
	@git diff --cached

version: ## Print current package version
	python -c "from zomi_nlp import __version__; print(__version__)"

tree: ## Print project directory tree
	tree -I "venv|.venv|__pycache__|*.egg-info|build|dist|.tox|.pytest_cache|.mypy_cache|.ruff_cache|htmlcov" -L 4

.PHONY: showcase
showcase: ## Run full capability showcase
	@echo "$(BLUE)Running Zomi NLP showcase...$(NC)"
	@python examples/showcase_zomi_nlp.py

.PHONY: demo
demo: ## Run interactive demo
	@python examples/quick_demo.py

.PHONY: benchmark
benchmark: ## Run performance benchmark
	@python examples/benchmark.py
