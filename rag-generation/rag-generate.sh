#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== RAG Generation ==="
echo ""

# ── Prerequisites check ─────────────────────────────────────────────
MISSING=()

check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        MISSING+=("$1")
    fi
}

check_cmd python3
check_cmd pip3
check_cmd git

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "[!] Missing prerequisites:" >&2
    for cmd in "${MISSING[@]}"; do
        echo "    - $cmd" >&2
    done
    echo ""
    echo "Install missing packages and try again." >&2
    echo "  Debian/Ubuntu: sudo apt install python3 python3-pip git"
    echo "  macOS:         brew install python3 git"
    exit 1
fi

echo "[v] All prerequisites found"

# ── Virtual env ─────────────────────────────────────────────────────
VENV_DIR="$PROJECT_ROOT/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment ..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# ── Dependencies ────────────────────────────────────────────────────
echo "[*] Installing dependencies ..."
pip3 install -r "$PROJECT_ROOT/requirements.txt" --quiet

# ── Run ─────────────────────────────────────────────────────────────
echo "[*] Running ingest ..."
python3 "$PROJECT_ROOT/src/ingest.py"

deactivate
echo "[v] RAG Generation Complete!"
