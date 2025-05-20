#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# generate_bin.sh – build standalone binary of dataset_tools.py using PyInstaller
# -----------------------------------------------------------------------------
# This script ensures a **local virtual environment (.venv)** exists, installs
# PyInstaller inside it, and then compiles `dataset_tools.py` into a self-
# contained executable placed under ./bin/.
#
# It is fully self-contained: you don’t need to activate .venv manually – the
# script does everything. However, if you *already* have an activated venv, it
# will reuse it.
#
# Usage examples
# --------------
#   ./generate_bin.sh                # default: python3, onefile
#   PYTHON=python3.11 ./generate_bin.sh --noconsole  # forward flags to PyInstaller
#
# Environment variables
# ---------------------
#   PYTHON     – interpreter to create venv (default: python3)
#   VENV_DIR   – directory for the virtual env (default: .venv)
#   OUTPUT_DIR – where the binary goes (default: ./bin)
# -----------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"  # ensure repo root

PYTHON="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
OUTPUT_DIR="${OUTPUT_DIR:-bin}"
NAME="inredd_stats"
EXTRA_FLAGS=("${@}")  # forward any CLI args to PyInstaller

# -----------------------------------------------------------------------------
# Create/ensure virtual environment
# -----------------------------------------------------------------------------

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  # Not inside any venv – ensure local .venv exists
  if [[ ! -d "$VENV_DIR" ]]; then
    echo "[+] Creating virtual environment at $VENV_DIR (using $PYTHON)"
    "$PYTHON" -m venv "$VENV_DIR"
  fi
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
else
  echo "[i] Using already-activated venv: $VIRTUAL_ENV"
fi

# -----------------------------------------------------------------------------
# Install PyInstaller if missing
# -----------------------------------------------------------------------------
if ! python -m pip show pyinstaller &>/dev/null; then
  echo "[+] Installing PyInstaller into venv…"
  python -m pip install --upgrade pyinstaller
fi

# -----------------------------------------------------------------------------
# Build binary
# -----------------------------------------------------------------------------
mkdir -p "$OUTPUT_DIR"

echo "[+] Running PyInstaller…"
pyinstaller dataset_tools.py \
  --name "$NAME" \
  --onefile \
  --distpath "$OUTPUT_DIR" \
  --specpath .pyi_build \
  --clean \
  "${EXTRA_FLAGS[@]}"

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------
echo "[✓] Binary created at $OUTPUT_DIR/$NAME"