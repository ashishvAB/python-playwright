# Playwright Python Test Runner

Run automated browser tests and upload results to TestDino.
this is fake commit
## Quick Start

### 1. Setup (First Time Only)

```bash
./bin/run-tests.sh --setup
```

This installs everything you need automatically.

### 2. Run Tests

```bash
./bin/run-tests.sh
```

### 3. Run Tests & Upload to TestDino

```bash
./bin/run-tests.sh --upload
```

## Configuration

### TestDino Token

Create a `.env` file in the project root:

```
TESTDINO_TOKEN=your_token_here
```

Or pass it directly:

```bash
TESTDINO_TOKEN=your_token ./bin/run-tests.sh --upload
```

## Commands

| Command | Description |
|---------|-------------|
| `./bin/run-tests.sh` | Run all tests |
| `./bin/run-tests.sh --setup` | Setup environment + run tests |
| `./bin/run-tests.sh --upload` | Run tests + upload to TestDino |
| `./bin/run-tests.sh --setup --upload` | Full setup, run, and upload |
| `./bin/run-tests.sh --headed` | Run with visible browser |
| `./bin/run-tests.sh --help` | Show all options |

## Options

| Option | Description |
|--------|-------------|
| `-s, --setup` | Install dependencies and browsers |
| `-u, --upload` | Upload results to TestDino |
| `--headed` | Show browser window during tests |
| `-w, --workers N` | Number of parallel tests (default: 10) |
| `-t, --timeout N` | Test timeout in seconds (default: 30) |

## Test Results

After running tests, find results in `test-results/`:

```
test-results/
├── report.json     # Test data (JSON)
├── index.html      # Visual report (open in browser)
└── tests-.../      # Screenshots, videos, traces (for failed tests)
```

### View HTML Report

Open `test-results/index.html` in your browser to see a visual test report.

## Running Specific Tests

```bash
# Run a specific test file
./bin/run-tests.sh tests/test_reporter.py

# Run with visible browser
./bin/run-tests.sh --headed tests/test_reporter.py
```

## Troubleshooting

### "command not found" errors

Run setup first:
```bash
./bin/run-tests.sh --setup
```

### Tests timeout

Increase timeout:
```bash
./bin/run-tests.sh -t 60
```

### Browser not installed

Setup installs browsers automatically. If issues persist:
```bash
.venv/bin/python -m playwright install chromium
```

### Upload fails

1. Check your `TESTDINO_TOKEN` is set correctly
2. Ensure you have internet connection
3. Run with verbose mode for details:
   ```bash
   ./bin/run-tests.sh --upload -v
   ```

## Project Structure

```
python-playwright/
├── .env                 # Your TestDino token (create this)
├── bin/
│   └── run-tests.sh     # Main script
├── tests/
│   └── test_reporter.py # Your test files
├── test-results/        # Generated after running tests
└── pyproject.toml       # Project configuration
```

## Writing Tests

Tests are in `tests/` folder. Example:

```python
from playwright.sync_api import Page, expect

def test_example(page: Page):
    page.goto("https://example.com")
    expect(page).to_have_title("Example Domain")
```

## Need Help?

- View all options: `./bin/run-tests.sh --help`
- TestDino documentation: https://testdino.com/docs
