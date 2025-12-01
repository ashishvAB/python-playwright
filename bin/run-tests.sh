#!/bin/bash
#
# Run Playwright tests with pytest and upload results to TestDino
#
# Usage:
#   ./bin/run-tests.sh                    # Run all tests
#   ./bin/run-tests.sh tests/login_test.py   # Run specific test file
#   ./bin/run-tests.sh --headed           # Run in headed mode
#   TESTDINO_TOKEN=xxx ./bin/run-tests.sh # With token
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Default values
RESULTS_DIR="test-results"
TEST_PATH="${1:-tests/}"
EXTRA_ARGS="${@:2}"

# Clean up previous results
rm -rf "$RESULTS_DIR"
mkdir -p "$RESULTS_DIR"

echo "=========================================="
echo "  Running Playwright Tests (headless)    "
echo "=========================================="
echo "Test path: $TEST_PATH"
echo "Output dir: $RESULTS_DIR"
echo "Workers: 10 (parallel)"
echo "Timeout: 30s per test"
echo "Video: on | Tracing: on | Screenshot: on"
echo ""

# Run pytest with playwright-json reporter
pytest "$TEST_PATH" \
    --playwright-json="$RESULTS_DIR/report.json" \
    --playwright-json-test-results-dir="$RESULTS_DIR" \
    -v \
    $EXTRA_ARGS || true

echo ""
echo "=========================================="
echo "  Test Execution Complete                 "
echo "=========================================="

# Check if report was generated
if [ ! -f "$RESULTS_DIR/report.json" ]; then
    echo "ERROR: Report file not generated at $RESULTS_DIR/report.json"
    exit 1
fi

echo "Report generated: $RESULTS_DIR/report.json"

# Extract stats from report
echo ""
echo "Test Results Summary:"
python3 -c "
import json
with open('$RESULTS_DIR/report.json') as f:
    data = json.load(f)
    stats = data.get('stats', {})
    print(f\"  Passed:   {stats.get('expected', 0)}\")
    print(f\"  Failed:   {stats.get('unexpected', 0)}\")
    print(f\"  Skipped:  {stats.get('skipped', 0)}\")
    print(f\"  Flaky:    {stats.get('flaky', 0)}\")
    print(f\"  Duration: {stats.get('duration', 0)/1000:.2f}s\")
"

# Upload to TestDino if token is available
if [ -n "$TESTDINO_TOKEN" ]; then
    echo ""
    echo "=========================================="
    echo "  Uploading to TestDino                   "
    echo "=========================================="

    # Upload JSON report with all attachments
    # Includes: traces (.zip), videos (.webm), screenshots (.png)
    tdpw upload "$RESULTS_DIR" \
        --json-report "$RESULTS_DIR/report.json" \
        --upload-traces \
        --trace-dir "$RESULTS_DIR" \
        -v

    echo ""
    echo "Upload complete!"
else
    echo ""
    echo "=========================================="
    echo "  Skipping Upload (no TESTDINO_TOKEN)     "
    echo "=========================================="
    echo "Set TESTDINO_TOKEN environment variable to upload results."
    echo "Example: TESTDINO_TOKEN=your_token ./bin/run-tests.sh"
fi

echo ""
echo "Done!"
