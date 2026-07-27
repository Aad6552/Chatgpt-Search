#!/usr/bin/env bash
# Tag and publish a release of the Ulauncher ChatGPT extension.
#
# The VERSION file is the source of truth for the current version.
#
# Usage:
#   ./release.sh              # bump patch version (default)
#   ./release.sh patch|minor|major
#   ./release.sh 1.2.3        # set an explicit version
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f VERSION ]]; then
  echo "Error: VERSION file not found" >&2
  exit 1
fi

CURRENT="$(<VERSION)"
CURRENT="${CURRENT//[$'\t\r\n ']/}"
if [[ ! "$CURRENT" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: VERSION file does not contain a valid semver (got '$CURRENT')" >&2
  exit 1
fi

BUMP="${1:-patch}"
BUMP="${BUMP#v}"
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP" in
  patch)
    PATCH=$((PATCH + 1))
    VERSION="$MAJOR.$MINOR.$PATCH"
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    VERSION="$MAJOR.$MINOR.$PATCH"
    ;;
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    VERSION="$MAJOR.$MINOR.$PATCH"
    ;;
  [0-9]*.[0-9]*.[0-9]*)
    VERSION="$BUMP"
    ;;
  *)
    echo "Usage: $0 [patch|minor|major|<explicit-version>]" >&2
    exit 1
    ;;
esac

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: version must be semver, e.g. 1.0.0 (got '$VERSION')" >&2
  exit 1
fi
TAG="v$VERSION"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not a git repository" >&2
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" != "master" ]]; then
  echo "Error: must be on 'master' branch (currently on '$BRANCH')" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: working tree is not clean. Commit or stash changes first." >&2
  git status --short
  exit 1
fi

if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Error: tag '$TAG' already exists" >&2
  exit 1
fi

echo "==> Running sanity checks"
python3 -m py_compile main.py
python3 -c "import json; json.load(open('manifest.json'))"
python3 -c "import json; json.load(open('versions.json'))"
if [[ ! -s images/icon.png ]]; then
  echo "Error: images/icon.png is missing or empty" >&2
  exit 1
fi

echo "==> Bumping version: $CURRENT -> $VERSION"
printf '%s\n' "$VERSION" > VERSION

echo "==> Setting manifest.json version to $VERSION"
python3 - "$VERSION" <<'PY'
import json
import sys

version = sys.argv[1]
path = "manifest.json"
with open(path) as f:
    manifest = json.load(f)
manifest["version"] = version
with open(path, "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")
PY

echo "==> Pointing versions.json at $TAG"
python3 - "$TAG" <<'PY'
import json
import sys

tag = sys.argv[1]
path = "versions.json"
with open(path) as f:
    versions = json.load(f)
for entry in versions:
    entry["commit"] = tag
with open(path, "w") as f:
    json.dump(versions, f, indent=2)
    f.write("\n")
PY

git add VERSION manifest.json versions.json
git commit -m "Release $TAG"

echo "==> Tagging $TAG"
git tag -a "$TAG" -m "Release $TAG"

echo "==> Pushing master and $TAG"
git push origin master
git push origin "$TAG"

if command -v gh >/dev/null 2>&1; then
  echo "==> Creating GitHub release"
  gh release create "$TAG" --title "$TAG" --generate-notes
else
  echo "==> gh CLI not found; skipping GitHub release creation."
  echo "    Create one manually at: https://github.com/Aad6552/Chatgpt-Search/releases/new?tag=$TAG"
fi

echo "==> Done: $TAG released"
