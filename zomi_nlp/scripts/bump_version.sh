#!/usr/bin/env bash
set -e

VERSION_FILE="version.py"
CHANGELOG_FILE="CHANGELOG.md"

# --- SAFETY CHECKS ---------------------------------------------------------

# Ensure working tree is clean
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: Working tree is dirty. Commit or stash changes first."
  exit 1
fi

# Ensure bump type is provided
if [[ -z "$1" ]]; then
  echo "Usage: bump_version.sh [major|minor|patch|prealpha|prebeta|prerc]"
  exit 1
fi

BUMP_TYPE=$1

# --- READ CURRENT VERSION --------------------------------------------------

CURRENT_VERSION=$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+([a-zA-Z0-9\.-]*)?' "$VERSION_FILE")
IFS='.' read -r MAJOR MINOR PATCH <<< "$(echo "$CURRENT_VERSION" | cut -d'-' -f1)"

PRERELEASE=$(echo "$CURRENT_VERSION" | grep -oE '(alpha|beta|rc)[0-9]*' || true)

# --- VERSION BUMP LOGIC ---------------------------------------------------

case "$BUMP_TYPE" in
  major)
    MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0; PRERELEASE="" ;;
  minor)
    MINOR=$((MINOR + 1)); PATCH=0; PRERELEASE="" ;;
  patch)
    PATCH=$((PATCH + 1)); PRERELEASE="" ;;
  prealpha)
    if [[ "$PRERELEASE" =~ alpha ]]; then
      NUM=$(echo "$PRERELEASE" | grep -oE '[0-9]+' || echo 0)
      PRERELEASE="alpha$((NUM + 1))"
    else
      PRERELEASE="alpha1"
    fi
    ;;
  prebeta)
    if [[ "$PRERELEASE" =~ beta ]]; then
      NUM=$(echo "$PRERELEASE" | grep -oE '[0-9]+' || echo 0)
      PRERELEASE="beta$((NUM + 1))"
    else
      PRERELEASE="beta1"
    fi
    ;;
  prerc)
    if [[ "$PRERELEASE" =~ rc ]]; then
      NUM=$(echo "$PRERELEASE" | grep -oE '[0-9]+' || echo 0)
      PRERELEASE="rc$((NUM + 1))"
    else
      PRERELEASE="rc1"
    fi
    ;;
  *)
    echo "Invalid bump type: $BUMP_TYPE"
    exit 1
    ;;
esac

# Construct new version
NEW_VERSION="$MAJOR.$MINOR.$PATCH"
if [[ -n "$PRERELEASE" ]]; then
  NEW_VERSION="$NEW_VERSION-$PRERELEASE"
fi

# --- UPDATE version.py -----------------------------------------------------

sed -i.bak "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" "$VERSION_FILE"
rm "$VERSION_FILE.bak"

echo "Updated version: $CURRENT_VERSION → $NEW_VERSION"

# --- GENERATE CHANGELOG ENTRY ---------------------------------------------

echo "Generating changelog..."

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [[ -n "$LAST_TAG" ]]; then
  LOG_RANGE="$LAST_TAG..HEAD"
else
  LOG_RANGE="HEAD"
fi

NEW_CHANGELOG="## v$NEW_VERSION - $(date +%Y-%m-%d)

$(git log --pretty=format:'- %s' $LOG_RANGE)

"

# Prepend to CHANGELOG.md
if [[ -f "$CHANGELOG_FILE" ]]; then
  echo -e "$NEW_CHANGELOG\n$(cat $CHANGELOG_FILE)" > $CHANGELOG_FILE
else
  echo -e "# Changelog\n\n$NEW_CHANGELOG" > $CHANGELOG_FILE
fi

# --- COMMIT + TAG + PUSH --------------------------------------------------

git add "$VERSION_FILE" "$CHANGELOG_FILE"
git commit -m "chore: release v$NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

git push
git push --tags

echo "Release v$NEW_VERSION created and pushed."
