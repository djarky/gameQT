#!/bin/sh

# run_tests.sh - GameQt Test Runner Wrapper (POSIX compliant)

# Get the directory where the script is located
SCRIPT_PATH="$0"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Display help message
show_help() {
    echo "Usage: $0 [options] [args...]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message and exit"
    echo ""
    echo "All other arguments will be passed directly to the Python test runner."
}

# Check for help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Set PYTHONPATH to include the project root so 'gameqt' can be imported
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Check for virtual environment and activate it if it exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "Activating virtual environment at $PROJECT_ROOT/.venv..."
    . "$PROJECT_ROOT/.venv/bin/activate"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    echo "Activating virtual environment at $PROJECT_ROOT/venv..."
    . "$PROJECT_ROOT/venv/bin/activate"
fi

# Ensure python3 is available
if ! command -v python3 > /dev/null 2>&1; then
    echo "Error: python3 is not installed or not in PATH."
    exit 1
fi

echo "Starting GameQt Test Runner..."
# Pass all script arguments to the Python runner
python3 "$SCRIPT_DIR/runner.py" "$@"
EXIT_CODE=$?

exit $EXIT_CODE
