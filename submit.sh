#!/usr/bin/env bash
# Batch pixelation runner.
#
# Iterates over every immediate subdirectory of INPUT_ROOT and runs process.py
# on each one, writing results to OUTPUT_ROOT/<subdir_name>/. Useful for
# processing a collection of per-user or per-session screenshot folders overnight.
#
# Usage:
#   ./submit.sh <input_root> <output_root> [extra process.py flags...]
#
# Examples:
#   ./submit.sh ./data/screenshots ./data/out
#   ./submit.sh ./data/screenshots ./data/out --elements profile_pic
#   ./submit.sh ./data/screenshots ./data/out --pixel-mode B
#
# Input spec:  INPUT_ROOT contains subdirs, each holding .png/.jpg/.jpeg files.
# Output spec: OUTPUT_ROOT/<subdir>/ gets *_pixelated.png for each input image.
#              A per-job log is written to OUTPUT_ROOT/logs/<subdir>.log.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <input_root> <output_root> [extra process.py flags...]" >&2
    exit 1
fi

INPUT_ROOT="$1"
OUTPUT_ROOT="$2"
shift 2
EXTRA_FLAGS=("$@")

if [[ ! -d "$INPUT_ROOT" ]]; then
    echo "Error: input_root not found: $INPUT_ROOT" >&2
    exit 1
fi

if [[ -z "${OPENROUTER_API_KEY:-}" ]] && [[ -f "$SCRIPT_DIR/.env" ]]; then
    # Load only KEY=VALUE lines, ignoring comments and non-assignment lines
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue
        export "$key=${value//\"/}"
    done < <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' "$SCRIPT_DIR/.env")
fi

LOG_DIR="$OUTPUT_ROOT/logs"
mkdir -p "$LOG_DIR"

TOTAL=0
SUCCESS=0
FAILED=0

for JOB_DIR in "$INPUT_ROOT"/*/; do
    [[ -d "$JOB_DIR" ]] || continue
    JOB_NAME="$(basename "$JOB_DIR")"
    JOB_OUT="$OUTPUT_ROOT/$JOB_NAME"
    JOB_LOG="$LOG_DIR/$JOB_NAME.log"

    mkdir -p "$JOB_OUT"
    echo ">>> [$JOB_NAME] $JOB_DIR -> $JOB_OUT"

    TOTAL=$((TOTAL + 1))
    if python3 "$SCRIPT_DIR/process.py" "$JOB_DIR" "$JOB_OUT" "${EXTRA_FLAGS[@]}" \
            >"$JOB_LOG" 2>&1; then
        SUCCESS=$((SUCCESS + 1))
        echo "    OK  (log: $JOB_LOG)"
    else
        FAILED=$((FAILED + 1))
        echo "    FAILED  (log: $JOB_LOG)" >&2
    fi
done

echo ""
echo "=== Batch summary: $TOTAL jobs, $SUCCESS OK, $FAILED failed ==="
if [[ $FAILED -gt 0 ]]; then
    exit 1
fi
