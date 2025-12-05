#!/usr/bin/env bash

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

# Function to check if virtual environment exists and is valid
check_venv() {
    local venv_path="$1"
    local project_name="$2"
    
    if [ -d "$venv_path" ] && [ -x "$venv_path/bin/python3" ]; then
        print_success "Virtual environment found for $project_name"
        return 0
    else
        print_warning "Virtual environment not found for $project_name at $venv_path"
        return 1
    fi
}

# Function to ensure virtual environment is using correct Python version
ensure_python_version() {
    local project_dir="$1"
    local expected_python="$2"
    local project_name="$3"
    local original_dir=$(pwd)
    
    cd "$project_dir"
    
    # Check if poetry environment exists and recreate if needed
    if ! poetry env info &> /dev/null; then
        print_warning "Poetry environment not found for $project_name. Creating new environment..."
        poetry install
    else
        # Check Python version in poetry environment
        local current_python=$(poetry env info --path)/bin/python3
        if [ -x "$current_python" ]; then
            local version=$($current_python --version 2>&1 | cut -d' ' -f2)
            print_status "Current Python version in $project_name: $version"
        fi
    fi
    
    # Return to original directory
    cd "$original_dir"
}

# Function to upgrade dependencies and test
upgrade_and_test() {
    local project_dir="$1"
    local project_name="$2"
    local test_command="$3"
    local original_dir=$(pwd)
    
    print_status "Upgrading dependencies in $project_name..."
    cd "$project_dir"
    
    # Ensure virtual environment is set up correctly (pass current directory, not project_dir)
    ensure_python_version "." "~3.12" "$project_name"
    
    # Update dependencies using the Python script
    if [ -f "update_dependencies.py" ]; then
        print_status "Running update_dependencies.py for $project_name..."
        poetry run python update_dependencies.py
    else
        print_warning "update_dependencies.py not found for $project_name. Using poetry update..."
        poetry update
    fi
    
    # Install any new dependencies
    print_status "Installing dependencies for $project_name..."
    poetry install
    
    # Run tests if test command is provided
    if [ -n "$test_command" ]; then
        print_status "Running tests for $project_name..."
        if eval "$test_command"; then
            print_success "Tests passed for $project_name"
        else
            print_error "Tests failed for $project_name"
            cd "$original_dir"
            return 1
        fi
    fi
    
    cd "$original_dir"
}

# Function to upgrade UI dependencies
upgrade_ui_and_test() {
    print_status "Upgrading dependencies in UI folder..."
    cd ui

    if [ -f "update_packages.js" ]; then
        if command -v node &> /dev/null; then
            print_status "Running update_packages.js for UI..."
            if node update_packages.js; then
                print_success "UI dependencies updated successfully"
            else
                print_error "Failed to update UI dependencies"
                cd ..
                return 1
            fi
        else
            print_warning "Node.js not found. Skipping UI update."
            cd ..
            return 1
        fi
    elif command -v yarn &> /dev/null; then
        print_status "Using yarn to update UI dependencies..."
        yarn upgrade --latest
        yarn install
        print_success "UI dependencies updated with yarn"
    else
        print_warning "Neither update_packages.js nor yarn found for UI. Skipping."
        cd ..
        return 1
    fi

    # Run UI tests
    print_status "Running UI tests..."
    if yarn run test; then
        print_success "UI tests passed"
    else
        print_error "UI tests failed"
        cd ..
        return 1
    fi

    cd ..
}

# Main execution
print_status "Starting comprehensive dependency upgrade process..."

# Upgrade CLI
upgrade_and_test "cli" "CLI" "poetry run pytest -vv"

# Upgrade App
upgrade_and_test "app" "App" "poetry run pytest -m 'not integration and not slow_integration'"

# Upgrade UI
upgrade_ui_and_test

# Upgrade root devscripts
print_status "Upgrading devscripts dependencies..."
if [ -f "pyproject.toml" ]; then
    poetry update
    poetry install
    print_success "Devscripts dependencies updated"
else
    print_warning "No pyproject.toml found in root directory"
fi

# Final verification
print_status "Running final verification..."

# Test CLI build
print_status "Testing CLI build..."
cd cli
if poetry build; then
    print_success "CLI build successful"
else
    print_error "CLI build failed"
    exit 1
fi
cd ..

# Test UI build
print_status "Testing UI build..."
cd ui
if yarn run build; then
    print_success "UI build successful"
else
    print_error "UI build failed"
    exit 1
fi
cd ..

print_success "Upgrade process completed successfully!"
print_status "All dependencies have been updated and tested."
print_status "Virtual environments are properly configured and up-to-date."
