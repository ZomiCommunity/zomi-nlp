#!/usr/bin/env bash
set -e

VERSION_FILE="pyproject.toml"
CHANGELOG_FILE="CHANGELOG.md"

# --- SAFETY CHECKS ---------------------------------------------------------

if [[ -n "$(git.status --porcelain)" ]]; then
  echo "Error: Working tree is dirty. Commit or stash changes first."
  exit 1
fi

if [[ -z "$1" ]]; then
  echo "Usage: bump_version.sh [major|minor|patch|prealpha|prebeta|prerc]"
  exit 1
fi

BUMP_TYPE=$1

# --- READ CURRENT VERSION --------------------------------------------------

CURRENT_VERSION=$(grep -oE 'version = "[^"]+"' "$VERSION_FILE" | cut -d'"' -f2)
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

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
[[ -n "$PRERELEASE" ]] && NEW_VERSION="$NEW_VERSION-$PRERELEASE"

# --- UPDATE pyproject.toml -------------------------------------------------

sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" "$VERSION_FILE"

echo "Updated version: $CURRENT_VERSION → $NEW_VERSION"

# --- GENERATE CHANGELOG ENTRY ---------------------------------------------

echo "Generating changelog..."

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

LOG_RANGE="${LAST_TAG:+$LAST_TAG..HEAD}"

NEW_CHANGELOG="## v$NEW_VERSION - $(date +%Y-%m-%d)

$(git log --pretty=format:'- %s' $LOG_RANGE)

"

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
