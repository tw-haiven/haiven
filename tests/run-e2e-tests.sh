#!/bin/bash

# Haiven E2E Tests Runner
# This script runs the Playwright e2e tests from the tests directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "playwright.config.ts" ] || [ ! -d "e2e" ]; then
    print_error "This script must be run from the tests directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists node; then
    print_error "Node.js is required but not installed"
    exit 1
fi

if ! command_exists yarn; then
    print_error "Yarn is required but not installed"
    exit 1
fi

print_success "Prerequisites check passed"

# Function to setup e2e tests
setup_e2e_tests() {
    print_status "Setting up e2e tests..."
    
    # Install UI dependencies if needed
    if [ ! -d "../ui/node_modules" ]; then
        print_status "Installing UI dependencies..."
        cd ../ui && yarn install && cd ../tests
    fi
    
    # Install e2e test dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing e2e test dependencies..."
        npm install
    fi
    
    # Install Playwright browsers
    print_status "Installing Playwright browsers..."
    npm run test:install
    
    print_success "E2E tests setup completed"
}

# Function to run tests
run_tests() {
    local test_type="$1"
    
    print_status "Running e2e tests: $test_type"
    
    case "$test_type" in
        "all")
            npm test
            ;;
        "headed")
            npm run test:headed
            ;;
        "debug")
            npm run test:debug
            ;;
        "ui")
            npm run test:ui
            ;;
        "chromium")
            npm run test:chromium
            ;;
        "firefox")
            npm run test:firefox
            ;;
        "report")
            npm run test:report
            ;;
        *)
            print_error "Unknown test type: $test_type"
            print_status "Available options:"
            print_status "  all - Run all tests"
            print_status "  headed - Run tests in headed mode"
            print_status "  debug - Run tests in debug mode"
            print_status "  ui - Run tests with Playwright UI"
            print_status "  chromium/firefox - Run specific browser"
             exit 1
            ;;
    esac
}

# Function to show help
show_help() {
    echo "Haiven E2E Tests Runner"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTION]"
    echo ""
    echo "Commands:"
    echo "  setup     Setup e2e test environment"
    echo "  run       Run e2e tests"
    echo "  help      Show this help message"
    echo ""
    echo "Options for 'run' command:"
    echo "  all       Run all tests - default"
    echo "  headed    Run tests in headed mode"
    echo "  debug     Run tests in debug mode"
    echo "  ui        Run tests with Playwright UI"
    echo "  chromium  Run tests in Chromium only"
    echo "  report    Show test report"
    echo ""
}

# Main script logic
case "${1:-run}" in
    "setup")
        setup_e2e_tests
        ;;
    "run")
        run_tests "${2:-all}"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 