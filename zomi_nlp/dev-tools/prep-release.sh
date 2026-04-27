#!/usr/bin/env bash
set -e

# Always run from project root
cd "$(dirname "$0")/../.."

PART="${part:-patch}"

# Extract current version
CURRENT=$(grep '^version' pyproject.toml | sed -E 's/version = "([^"]+)"/\1/')
echo "Current version: $CURRENT"

# Parse version
IFS='.-' read -r MAJOR MINOR PATCH EXTRA <<< "$CURRENT"

case "$PART" in
  patch) PATCH=$((PATCH + 1));;
  minor) MINOR=$((MINOR + 1)); PATCH=0;;
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0;;
  *) echo "Invalid part: $PART"; exit 1;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo "New version: $NEW_VERSION"

# Update pyproject.toml
sed -i.bak -E "s/version = \".+\"/version = \"${NEW_VERSION}\"/" pyproject.toml
rm pyproject.toml.bak

# Generate changelog
if grep -q "## ${NEW_VERSION}" CHANGELOG.md; then
  echo "Changelog already exists for ${NEW_VERSION}"
else
  PREV_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
  if [ -z "$PREV_TAG" ]; then
    LOG=$(git log --pretty=format:"- %s")
  else
    LOG=$(git log "${PREV_TAG}..HEAD" --pretty=format:"- %s")
  fi

  {
    echo "## ${NEW_VERSION} — $(date +%Y-%m-%d)"
    echo ""
    echo "$LOG"
    echo ""
  } >> CHANGELOG.md
fi

# Commit
git add pyproject.toml CHANGELOG.md
git commit -m "Release ${NEW_VERSION}"

# Tag
TAG="v${NEW_VERSION}"
git tag "$TAG"
git push origin "$TAG"

echo "✓ Release ${NEW_VERSION} prepared and tag pushed!"

# chmod +x zomi_nlp/scripts/prep-release.sh
