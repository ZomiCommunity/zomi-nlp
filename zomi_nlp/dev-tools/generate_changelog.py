#!/usr/bin/env python3
"""Generate CHANGELOG.md from git tags."""

import re
import subprocess


def get_tags() -> list[str]:
    """Get all tags sorted by version."""
    result = subprocess.run(
        ["git", "tag", "-l"],
        capture_output=True,
        text=True
    )
    tags = [t.strip() for t in result.stdout.split("\n") if t.strip()]
    # Sort by version
    tags.sort(key=lambda v: [int(x) for x in v.lstrip('v').split('.')])
    return tags


def get_commits_between(start: str, end: str) -> list[tuple[str, str]]:
    """Get commits between two tags."""
    cmd = ["git", "log", f"{start}..{end}", "--pretty=format:%s|%h"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    commits = []
    for line in result.stdout.split("\n"):
        if "|" in line:
            msg, hash_val = line.rsplit("|", 1)
            commits.append((msg, hash_val))
    return commits


def categorize_commit(msg: str) -> str:
    """Categorize commit message."""
    msg_lower = msg.lower()
    if re.match(r'^(feat|feature|add|new)', msg_lower):
        return "✨ New Features"
    elif re.match(r'^(fix|bug|resolve|correct|repair)', msg_lower):
        return "🐛 Bug Fixes"
    elif re.match(r'^(docs|doc|readme|documentation)', msg_lower):
        return "📚 Documentation"
    elif re.match(r'^(refactor|clean|rename|move|restructure)', msg_lower):
        return "🔧 Refactoring"
    elif re.match(r'^(test|spec)', msg_lower):
        return "✅ Tests"
    elif re.match(r'^(ci|cd|action|workflow)', msg_lower):
        return "⚙️ CI/CD"
    elif re.match(r'^(style|format|lint)', msg_lower):
        return "💄 Code Style"
    elif re.match(r'^(perf|performance|optimize)', msg_lower):
        return "⚡ Performance"
    else:
        return "📦 Other Changes"


def generate_changelog():
    """Generate CHANGELOG.md."""
    tags = get_tags()

    changelog = [
        "# Changelog",
        "",
        "All notable changes to this project will be documented in this file.",
        "",
        "The format is based on [Keep a Changelog](https://keepachangelog.com/).",
        "",
    ]

    # Process tags from newest to oldest
    for i, tag in enumerate(reversed(tags)):
        prev_tag = tags[-i-2] if i + 2 <= len(tags) else None
        version = tag.lstrip('v')

        # Get date from tag
        date_cmd = ["git", "log", "-1", "--format=%ad", "--date=short", tag]
        date = subprocess.run(date_cmd, capture_output=True, text=True).stdout.strip()

        changelog.append(f"## [{version}] — {date}")
        changelog.append("")

        # Get commits since previous tag
        commits = []
        commits = get_commits_between(prev_tag, tag) if prev_tag else get_commits_between("", tag)

        # Group by category
        categories: dict[str, list[str]] = {}
        for msg, hash_val in commits:
            cat = categorize_commit(msg)
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(f"- {msg} [`{hash_val}`]")

        # Write categories
        for cat, items in categories.items():
            changelog.append(f"### {cat}")
            changelog.extend(items)
            changelog.append("")

        changelog.append("---")
        changelog.append("")

    # Write to file
    with open("CHANGELOG.md", "w") as f:
        f.write("\n".join(changelog))

    print("✅ CHANGELOG.md generated!")


if __name__ == "__main__":
    generate_changelog()
