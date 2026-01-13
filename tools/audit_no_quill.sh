#!/usr/bin/env bash
# Fail if Quill remnants exist.
# Usage: bash tools/audit_no_quill.sh

set -euo pipefail

patterns=("quill" "ql-" "dangerouslyPasteHTML")
exclude_dirs=(".git" "__pycache__" "node_modules" "venv" "planQuoteGenV4.7" "agentsQuoteGenV4.7" "tools")

echo "Audit: scanning repo for prohibited Quill remnants..."

# Build grep exclude args
exclude_args=()
for d in "${exclude_dirs[@]}"; do
  exclude_args+=( "--exclude-dir=$d" )
done

found=0
for p in "${patterns[@]}"; do
  if grep -RIn "${exclude_args[@]}" -- "$p" . >/dev/null 2>&1; then
    echo "FAILED: Found matches for pattern: $p"
    grep -RIn "${exclude_args[@]}" -- "$p" . || true
    found=1
  fi
done

if [ "$found" -ne 0 ]; then
  exit 1
fi

echo "PASSED: No Quill remnants found."
