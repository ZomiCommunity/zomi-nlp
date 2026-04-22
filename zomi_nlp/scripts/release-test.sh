#!/usr/bin/env bash
set -e

# Always run from project root
cd "$(dirname "$0")/../.."

# Ensure token exists
if [ -z "$TEST_PYPI_TOKEN" ]; then
    echo "ERROR: TEST_PYPI_TOKEN environment variable is not set."
    exit 1
fi

# Backup pyproject.toml
cp pyproject.toml pyproject.toml.bak

restore_pyproject() {
    echo "Restoring original pyproject.toml"
    mv pyproject.toml.bak pyproject.toml
}
trap restore_pyproject EXIT

# Extract base version
BASE_VERSION=$(python3 - <<'EOF'
import tomllib
with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)
print(data["project"]["version"])
EOF
)

echo "Base version: $BASE_VERSION"

# Generate timestamp version
TIMESTAMP=$(date +"%Y%m%d%H%M")
VERSION="${BASE_VERSION}.dev${TIMESTAMP}"

echo "New TestPyPI version: $VERSION"

# Update pyproject.toml
python3 - <<EOF
import tomllib, tomli_w

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

data["project"]["version"] = "$VERSION"

with open("pyproject.toml", "wb") as f:
    tomli_w.dump(data, f)
EOF

echo "Updated pyproject.toml → version = $VERSION"

# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Upload to TestPyPI
twine upload \
  --repository testpypi \
  --username __token__ \
  --password "$TEST_PYPI_TOKEN" \
  dist/*

# Test installation
pip install \
  --index-url https://test.pypi.org/simple/ \
  --upgrade "zomi-nlp==$VERSION"

echo "Done. Installed zomi-nlp==$VERSION"
