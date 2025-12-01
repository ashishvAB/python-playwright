#!/bin/bash
#
# Playwright Test Runner with TestDino Integration
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON="$PROJECT_DIR/.venv/bin/python3"

# Load .env file if it exists
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

# Default values
RESULTS_DIR="test-results"
TEST_PATH="tests/"
UPLOAD=false
SETUP=false
HEADED=false
WORKERS=10
TIMEOUT=30

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_help() {
    echo "Playwright Test Runner with TestDino Integration"
    echo ""
    echo "Usage: ./bin/run-tests.sh [OPTIONS] [TEST_PATH]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -s, --setup         Setup environment (create venv, install deps)"
    echo "  -u, --upload        Upload results to TestDino after tests"
    echo "  --headed            Run tests in headed mode (visible browser)"
    echo "  -w, --workers NUM   Number of parallel workers (default: 10)"
    echo "  -t, --timeout SEC   Test timeout in seconds (default: 30)"
    echo ""
    echo "Examples:"
    echo "  ./bin/run-tests.sh                     # Run all tests"
    echo "  ./bin/run-tests.sh --setup             # Setup env and run tests"
    echo "  ./bin/run-tests.sh --upload            # Run tests and upload to TestDino"
    echo "  ./bin/run-tests.sh --setup --upload    # Full setup, run, and upload"
    echo "  ./bin/run-tests.sh tests/test_login.py # Run specific test file"
    echo "  ./bin/run-tests.sh --headed            # Run with visible browser"
    echo "  ./bin/run-tests.sh -w 5 -t 60          # 5 workers, 60s timeout"
    echo ""
    echo "Environment Variables:"
    echo "  TESTDINO_TOKEN      API token for TestDino uploads (required for --upload)"
    echo ""
    echo "Configuration:"
    echo "  Create a .env file in the project root with:"
    echo "    TESTDINO_TOKEN=your_token_here"
    echo ""
}

setup_environment() {
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}  Setting up environment                  ${NC}"
    echo -e "${GREEN}==========================================${NC}"

    cd "$PROJECT_DIR"

    # Create venv if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi

    # Install/upgrade pip
    echo "Upgrading pip..."
    $PYTHON -m pip install --upgrade pip --quiet

    # Install dependencies
    echo "Installing project dependencies..."
    $PYTHON -m pip install -e . --quiet

    # Install playwright browsers
    echo "Installing Playwright browsers..."
    $PYTHON -m playwright install chromium

    # Install pytest-playwright-json and tdpw from local packages or PyPI
    echo "Installing pytest-playwright-json and tdpw..."
    if [ -d "$PROJECT_DIR/packages" ] && ls "$PROJECT_DIR/packages"/*.whl 1> /dev/null 2>&1; then
        # Install from local wheel files (CI/CD mode)
        $PYTHON -m pip install "$PROJECT_DIR/packages"/*.whl --quiet --force-reinstall
    else
        # Install from PyPI (production mode)
        $PYTHON -m pip install pytest-playwright-json tdpw --quiet
    fi

    echo ""
    echo -e "${GREEN}Environment ready!${NC}"
    echo ""
}

run_tests() {
    cd "$PROJECT_DIR"

    # Clean up previous results
    rm -rf "$RESULTS_DIR"
    mkdir -p "$RESULTS_DIR"

    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}  Running Playwright Tests                ${NC}"
    echo -e "${GREEN}==========================================${NC}"
    echo "Test path: $TEST_PATH"
    echo "Output dir: $RESULTS_DIR"
    echo "Workers: $WORKERS (parallel)"
    echo "Timeout: ${TIMEOUT}s per test"
    echo "Mode: $([ "$HEADED" = true ] && echo "headed" || echo "headless")"
    echo ""

    # Build pytest args
    PYTEST_ARGS=(
        "$TEST_PATH"
        "--playwright-json=$RESULTS_DIR/report.json"
        "--html=$RESULTS_DIR/index.html"
        "--self-contained-html"
        "-n=$WORKERS"
        "--timeout=$TIMEOUT"
        "-v"
    )

    if [ "$HEADED" = true ]; then
        PYTEST_ARGS+=("--headed")
    fi

    # Run pytest
    $PYTHON -m pytest "${PYTEST_ARGS[@]}" || true

    echo ""
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}  Test Execution Complete                 ${NC}"
    echo -e "${GREEN}==========================================${NC}"

    # Check if report was generated
    if [ ! -f "$RESULTS_DIR/report.json" ]; then
        echo -e "${RED}ERROR: Report file not generated at $RESULTS_DIR/report.json${NC}"
        exit 1
    fi

    echo "Report generated: $RESULTS_DIR/report.json"
    echo "HTML report: $RESULTS_DIR/index.html"

    # Extract stats from report
    echo ""
    echo "Test Results Summary:"
    $PYTHON -c "
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
}

upload_results() {
    if [ -z "$TESTDINO_TOKEN" ]; then
        echo ""
        echo -e "${YELLOW}==========================================${NC}"
        echo -e "${YELLOW}  Skipping Upload (no TESTDINO_TOKEN)     ${NC}"
        echo -e "${YELLOW}==========================================${NC}"
        echo "Set TESTDINO_TOKEN environment variable to upload results."
        echo "Example: TESTDINO_TOKEN=your_token ./bin/run-tests.sh --upload"
        return
    fi

    cd "$PROJECT_DIR"

    echo ""
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}  Uploading to TestDino                   ${NC}"
    echo -e "${GREEN}==========================================${NC}"

    # Build upload args
    UPLOAD_ARGS=(
        "$RESULTS_DIR"
        "--json-report" "$RESULTS_DIR/report.json"
        "--upload-traces"
        "--trace-dir" "$RESULTS_DIR"
        "-v"
    )

    # Add HTML upload if index.html exists in results dir
    if [ -f "$RESULTS_DIR/index.html" ]; then
        UPLOAD_ARGS+=("--upload-html" "--html-report" "$RESULTS_DIR")
    else
        echo "⚠️  HTML report not found, skipping HTML upload"
    fi

    # Upload JSON report with all attachments
    $PYTHON -m testdino_cli.cli.index upload "${UPLOAD_ARGS[@]}"

    echo ""
    echo -e "${GREEN}Upload complete!${NC}"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--setup)
            SETUP=true
            shift
            ;;
        -u|--upload)
            UPLOAD=true
            shift
            ;;
        --headed)
            HEADED=true
            shift
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# Main execution
cd "$PROJECT_DIR"

if [ "$SETUP" = true ]; then
    setup_environment
fi

run_tests

if [ "$UPLOAD" = true ]; then
    upload_results
fi

echo ""
echo "Done!"
