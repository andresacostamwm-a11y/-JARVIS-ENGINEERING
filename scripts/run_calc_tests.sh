#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/services/api:${PYTHONPATH:-}"
cd "$ROOT"
python -m pip install -q pytest numpy 2>/dev/null || true
python -m pytest tests/calculations -v --tb=short
