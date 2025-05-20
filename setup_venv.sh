#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# setup_venv.sh – quick virtual‑environment bootstrapper for the InReDD project
# -----------------------------------------------------------------------------
# Usage:
#   ./setup_venv.sh            # creates .venv and installs requirements
#   PYTHON=python3.11 ./setup_venv.sh   # choose a specific interpreter
#
# After running, activate with:
#   source .venv/bin/activate
# -----------------------------------------------------------------------------
set -euo pipefail

# cd to the directory containing this script so the venv sits in repo root
cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON="${PYTHON:-python3}"
VENV_DIR=".venv"

if ! command -v "$PYTHON" &>/dev/null; then
  echo "[ERROR] $PYTHON not found in PATH. Set PYTHON=/path/to/python3" >&2
  exit 1
fi

printf "\n[+] Creating virtual environment in '%s'...\n" "$VENV_DIR"
"$PYTHON" -m venv "$VENV_DIR"

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

printf "[+] Upgrading core packaging tools...\n"
pip install --upgrade --quiet pip setuptools wheel

echo "[+] Installing project requirements..."
if [[ -f requirements.txt ]]; then
  pip install --upgrade -r requirements.txt
else
  echo "  (requirements.txt not found – installing minimal extras)"
  pip install --upgrade tqdm
fi

echo "\n[✓] Setup complete. Activate anytime with: source $VENV_DIR/bin/activate"
