#!/usr/bin/env bash
set -e

# Always run from project root
cd "$(dirname "$0")/../.."

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure token exists
if [ -z "$TEST_PYPI_TOKEN" ]; then
    echo -e "${RED}ERROR: TEST_PYPI_TOKEN environment variable is not set.${NC}"
    echo ""
    echo "Get your token from: https://test.pypi.org/manage/account/token/"
    echo "Then set it: export TEST_PYPI_TOKEN='pypi-xxxxxxxx'"
    exit 1
fi

# Check if required tools are installed
for cmd in python3 twine; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}ERROR: $cmd is not installed.${NC}"
        exit 1
    fi
done

# Backup pyproject.toml
cp pyproject.toml pyproject.toml.bak

restore_pyproject() {
    echo -e "${YELLOW}Restoring original pyproject.toml${NC}"
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

echo -e "${GREEN}Base version: $BASE_VERSION${NC}"

# Generate timestamp version (remove any existing .dev suffix)
CLEAN_VERSION=$(echo "$BASE_VERSION" | sed 's/\.dev.*//')
TIMESTAMP=$(date +"%Y%m%d%H%M")
VERSION="${CLEAN_VERSION}.dev${TIMESTAMP}"

echo -e "${YELLOW}New TestPyPI version: $VERSION${NC}"

# Check if tomli_w is installed, if not, use alternative method
if python3 -c "import tomli_w" 2>/dev/null; then
    # Update pyproject.toml with tomli_w
    python3 - <<EOF
import tomllib, tomli_w

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

data["project"]["version"] = "$VERSION"

with open("pyproject.toml", "wb") as f:
    tomli_w.dump(data, f)
EOF
else
    # Fallback to sed for simplicity
    sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
fi

echo -e "${GREEN}Updated pyproject.toml → version = $VERSION${NC}"

# Clean old builds
echo -e "${YELLOW}Cleaning old builds...${NC}"
rm -rf dist/ build/ *.egg-info

# Build package
echo -e "${YELLOW}Building package...${NC}"
python -m build

# Upload to TestPyPI
echo -e "${YELLOW}Uploading to TestPyPI...${NC}"
twine upload \
  --repository testpypi \
  --username __token__ \
  --password "$TEST_PYPI_TOKEN" \
  dist/*

# Test installation in a clean way
echo -e "${YELLOW}Testing installation...${NC}"

# Create a temporary venv for testing
TEST_ENV=$(mktemp -d)
python3 -m venv "$TEST_ENV"
source "$TEST_ENV/bin/activate"

pip install --upgrade pip --quiet
pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  "zomi-nlp==$VERSION"

# Quick verification
python3 -c "from zomi_nlp import __version__; assert __version__ == '$VERSION'; print('✅ Version OK')"

deactivate
rm -rf "$TEST_ENV"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Done! Installed zomi-nlp==$VERSION${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To test manually:"
echo "  pip install --index-url https://test.pypi.org/simple/ zomi-nlp==$VERSION"
echo ""
echo "To publish to production:"
echo "  make release"
