# Code Quality Tools for NS-3 and Blockchain Simulation Project

This document explains the code quality tools set up for this project and how to use them effectively.

## Available Tools

The project uses the following code quality tools:

1. **Black** - Code formatter that ensures consistent style
2. **Pylint** - Linter that checks for errors and code smells
3. **MyPy** - Static type checker for Python
4. **Bandit** - Security-focused tool to find common security issues
5. **pytest** - Testing framework with coverage reporting
6. **pre-commit** - Automatically runs checks before each commit

## Setup

To set up all the code quality tools, run:

```bash
cd test_ns3_blocksim
chmod +x setup_code_quality.sh
./setup_code_quality.sh
```

This script will:
1. Create a virtual environment (if it doesn't exist)
2. Install all necessary tools
3. Create configuration files
4. Set up pre-commit hooks

## Running Code Analysis

To analyze your code without committing changes, use the provided script:

```bash
cd test_ns3_blocksim
chmod +x run_code_analysis.sh
./run_code_analysis.sh
```

This will run all checks and generate an HTML report in the `code_analysis_reports` directory.

### Options for Code Analysis

Run specific checks:
- `./run_code_analysis.sh --format` - Check code formatting only
- `./run_code_analysis.sh --lint` - Run linting only
- `./run_code_analysis.sh --type` - Run type checking only
- `./run_code_analysis.sh --security` - Run security checks only

Specify custom directories:
- `./run_code_analysis.sh --dirs models,scripts,examples`

## Pre-commit Hooks

After setup, pre-commit hooks will automatically run when you try to commit changes. If any checks fail, the commit will be blocked until you fix the issues.

To manually run all pre-commit hooks:

```bash
pre-commit run --all-files
```

## Manual Usage of Tools

You can also run each tool manually:

### Code Formatting

```bash
# Check formatting without making changes
black --check models scripts

# Format code
black models scripts
```

### Linting

```bash
# Run pylint on specific directories
pylint --recursive=y models scripts
```

### Type Checking

```bash
# Run type checking
mypy --ignore-missing-imports models scripts
```

### Security Checks

```bash
# Run security checks
bandit -r models scripts
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=models --cov-report=html
```

## Integration with CI/CD

These tools can be integrated into a CI/CD pipeline. Here's an example GitHub Actions workflow:

```yaml
name: Code Quality

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        pip install black pylint mypy bandit pytest pytest-cov
    - name: Check formatting
      run: black --check .
    - name: Lint with pylint
      run: pylint --recursive=y models scripts
    - name: Type check with mypy
      run: mypy --ignore-missing-imports models scripts
    - name: Security check with bandit
      run: bandit -r models scripts
    - name: Test with pytest
      run: pytest --cov=models --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Best Practices

1. **Run Black First** - Always format your code first before running other checks
2. **Add Type Hints** - Gradually add type hints to improve code quality and catch errors early
3. **Fix Security Issues Immediately** - Security issues identified by Bandit should be fixed as soon as possible
4. **Write Tests** - Aim for high test coverage, especially for critical components
5. **Document Functions** - Add docstrings to all functions and classes

## Configuration

All tools are configured with reasonable defaults for this project:

- **Black**: 88 character line length, compatible with PEP 8
- **Pylint**: Customized rules to reduce false positives
- **MyPy**: Gradual typing approach
- **Bandit**: Standard security checks
- **pytest**: Configured to generate coverage reports

You can modify these configurations in:
- `pyproject.toml` - Black and MyPy configuration
- `.pylintrc` - Pylint configuration
- `setup.cfg` - pytest configuration

## Adding More Tools

If you need more tools, you can add them to the setup script. Some additional tools to consider:

- **Interrogate** - Checks docstring coverage
- **Vulture** - Finds unused code
- **Radon** - Analyzes code complexity
- **Pyright** - Alternative type checker from Microsoft
- **Codecov** - For code coverage tracking in CI/CD
