
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

help:
	@echo ""
	@echo "$(BLUE)Available commands:$(NC)"
	@echo "  $(GREEN)install$(NC)      - Install package"
	@echo "  $(GREEN)install-dev$(NC)  - Install with dev dependencies"
	@echo "  $(GREEN)test$(NC)         - Run tests"
	@echo "  $(GREEN)test-all$(NC)     - Run tests on all Python versions (tox)"
	@echo "  $(GREEN)lint$(NC)         - Run linters"
	@echo "  $(GREEN)format$(NC)       - Format code"
	@echo "  $(GREEN)check$(NC)        - Run all checks (lint + test)"
	@echo "  $(GREEN)pre-commit$(NC)   - Run pre-commit hooks"
	@echo "  $(GREEN)clean$(NC)        - Clean build artifacts"
	@echo "  $(GREEN)clean-all$(NC)    - Deep clean (including venv)"
	@echo "  $(GREEN)build$(NC)        - Build package distribution (wheel + sdist)"
	@echo "  $(GREEN)publish$(NC)      - Publish to PyPI"
	@echo "  $(GREEN)bump-version$(NC) - Bump package version"
	@echo "  $(GREEN)test-release$(NC) - Build and upload a timestamped dev version to TestPyPI"
	@echo "  $(GREEN)release$(NC)      - Full release (lint + test + build + publish)"
	@echo "  $(GREEN)tag$(NC)          - Create and push a git tag"
	@echo "  $(GREEN)change-log$(NC)      - Generate CHANGELOG.md from git history"
	@echo "  $(GREEN)prep-release$(NC)    - Run release prep script (bump version, update changelog, tag)"
	@echo ""

# -----------------------------
# Development commands
# -----------------------------

install:
	@echo "$(GREEN)Installing package...$(NC)"
	pip install .

install-dev:
	@echo "$(GREEN)Installing with dev dependencies...$(NC)"
	pip install -e ".[dev]"

test:
	@echo "$(GREEN)Running tests...$(NC)"
	pytest tests/ -v --cov=zomi_nlp --cov-report=term --cov-report=html
	@echo "$(GREEN)Tests complete! Coverage report: htmlcov/index.html$(NC)"

test-all:
	@echo "$(GREEN)Running tests on all Python versions...$(NC)"
	tox

lint:
	@echo "$(YELLOW)Linting code...$(NC)"
	ruff check zomi_nlp/
	mypy zomi_nlp/ --ignore-missing-imports
	@echo "$(GREEN)Linting complete!$(NC)"

format:
	@echo "$(YELLOW)Formatting code...$(NC)"
	black zomi_nlp/ tests/
	ruff check --fix zomi_nlp/
	@echo "$(GREEN)Formatting complete!$(NC)"

check: lint test
	@echo "$(GREEN)✓ All checks passed!$(NC)"

pre-commit:
	@echo "$(YELLOW)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)Pre-commit complete!$(NC)"

# -----------------------------
# Build commands
# -----------------------------

clean:
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

clean-all: clean
	@echo "$(YELLOW)Deep cleaning...$(NC)"
	rm -rf .venv/
	rm -rf .tox/
	rm -rf .pytest_cache/
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Deep clean complete!$(NC)"

build: clean
	@echo "$(GREEN)Building package distribution...$(NC)"
	python -m build
	twine check dist/*
	@echo "$(GREEN)Build complete!$(NC)"

publish: build
	@echo "$(GREEN)Publishing to PyPI...$(NC)"
	twine upload dist/*
	@echo "$(GREEN)Published successfully!$(NC)"

# -----------------------------
# Version bumping
# -----------------------------
# Usage: make bump-version part=patch|minor|major
bump-version:
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

test-release:
    @echo "$(GREEN)Running TestPyPI release...$(NC)"
    ./zomi_nlp/scripts/release-test.sh

# -----------------------------
# Full PyPI Release
# -----------------------------

release:
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

tag:
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

changelog:
    @echo "$(BLUE)Generating changelog entry...$(NC)"
    @version=$$(grep '^version' pyproject.toml | sed -E 's/version = "([^"]+)"/\1/'); \
    if grep -q "## $$version" CHANGELOG.md; then \
        echo "$(YELLOW)Changelog for version $$version already exists.$(NC)"; \
        exit 1; \
    fi; \
    echo "Creating changelog for version $$version"; \
    previous_tag=$$(git describe --tags --abbrev=0 2>/dev/null || echo ""); \
    if [ -z "$$previous_tag" ]; then \
        echo "$(YELLOW)No previous tag found — using full commit history.$(NC)"; \
        git_log=$$(git log --pretty=format:"- %s"); \
    else \
        echo "Comparing commits since $$previous_tag"; \
        git_log=$$(git log $$previous_tag..HEAD --pretty=format:"- %s"); \
    fi; \
    { \
        echo "## $$version — $$(date +%Y-%m-%d)"; \
        echo ""; \
        echo "$$git_log"; \
        echo ""; \
    } >> CHANGELOG.md; \
    echo "$(GREEN)✓ Changelog updated for version $$version$(NC)"


# Usage: make prep-release part=patch|minor|major
prep-release:
    ./zomi_nlp/scripts/prep-release.sh part=$(part)


