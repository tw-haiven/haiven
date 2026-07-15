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

# Function to find a Python interpreter that matches a required major.minor version
find_python_interpreter() {
    local required_version="$1"
    local candidate

    # Prefer an explicit python3.X binary if available.
    if command -v "python${required_version}" > /dev/null 2>&1; then
        command -v "python${required_version}"
        return 0
    fi

    # Fall back to python3 when it already points at the required version.
    if command -v python3 > /dev/null 2>&1; then
        candidate=$(command -v python3)
        if "$candidate" --version 2>&1 | grep -q "Python ${required_version}"; then
            echo "$candidate"
            return 0
        fi
    fi

    # Fall back to python when it already points at the required version.
    if command -v python > /dev/null 2>&1; then
        candidate=$(command -v python)
        if "$candidate" --version 2>&1 | grep -q "Python ${required_version}"; then
            echo "$candidate"
            return 0
        fi
    fi

    return 1
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
    local required_python="${expected_python#\~}"
    local selected_python
    local current_python
    local version

    # Normalize specifiers like "~3.12" or ">=3.12" down to "3.12".
    if [[ ! "$required_python" =~ ^[0-9]+\.[0-9]+$ ]]; then
        required_python=$(echo "$expected_python" | sed -E 's/^[^0-9]*([0-9]+\.[0-9]+).*$/\1/')
    fi
    
    cd "$project_dir"

    if ! selected_python=$(find_python_interpreter "$required_python"); then
        print_error "Could not find a Python ${required_python} interpreter for $project_name"
        cd "$original_dir"
        return 1
    fi

    print_status "Using Python interpreter for $project_name: $selected_python"
    
    # Check if poetry environment exists and recreate if needed
    if ! poetry env info &> /dev/null; then
        print_warning "Poetry environment not found for $project_name. Creating new environment..."
        poetry env use "$selected_python"
        poetry install --no-root
    else
        # Check Python version in poetry environment
        current_python=$(poetry env info --path)/bin/python3
        if [ -x "$current_python" ]; then
            version=$($current_python --version 2>&1 | cut -d' ' -f2)
            print_status "Current Python version in $project_name: $version"

            if [[ "$version" != ${required_python}.* ]]; then
                print_warning "Switching poetry environment in $project_name to Python ${required_python}"
                poetry env use "$selected_python"
            fi
        else
            print_warning "Poetry environment python executable missing for $project_name. Recreating with Python ${required_python}."
            poetry env use "$selected_python"
        fi
    fi

    # Verify poetry now resolves to the required interpreter version.
    version=$(poetry run python --version 2>&1 | cut -d' ' -f2)
    if [[ "$version" != ${required_python}.* ]]; then
        print_error "Poetry is still using Python $version for $project_name (expected ${required_python}.x)"
        cd "$original_dir"
        return 1
    fi
    print_success "Poetry is using Python $version for $project_name"
    
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
    if ! ensure_python_version "." "~3.12" "$project_name"; then
        cd "$original_dir"
        return 1
    fi

    # Ensure helper scripts can import project dependencies in a fresh env.
    print_status "Bootstrapping dependencies for $project_name..."
    if ! poetry install --no-root; then
        print_error "Bootstrap install failed for $project_name"
        cd "$original_dir"
        return 1
    fi
    
    # Update dependencies using the Python script
    if [ -f "update_dependencies.py" ]; then
        print_status "Running update_dependencies.py for $project_name..."
        if ! poetry run python update_dependencies.py; then
            print_error "Dependency update script failed for $project_name"
            cd "$original_dir"
            return 1
        fi
    else
        print_warning "update_dependencies.py not found for $project_name. Using poetry update..."
        if ! poetry update; then
            print_error "poetry update failed for $project_name"
            cd "$original_dir"
            return 1
        fi
    fi
    
    # Install any new dependencies after update.
    print_status "Installing dependencies for $project_name..."
    if ! poetry install --no-root; then
        print_error "Final install failed for $project_name"
        cd "$original_dir"
        return 1
    fi
    
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
    poetry install --no-root
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
