#!/bin/bash
# Script to set up code quality tools for the NS-3 and Blockchain Simulation project

echo "Setting up code quality tools for your thesis project..."

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install development dependencies
echo "Installing code quality tools..."
pip install -U pip
pip install black pylint mypy pytest pytest-cov bandit pre-commit

# Install project dependencies if needed
if [ -f "requirements.txt" ]; then
    echo "Installing project dependencies..."
    pip install -r requirements.txt
fi

# Create configuration files for tools

# Create pyproject.toml for Black and other tools
echo "Creating pyproject.toml..."
cat > pyproject.toml << EOF
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
  | external
)/
'''

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
strict_optional = true

[[tool.mypy.overrides]]
module = "external.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "ns3.*"
ignore_missing_imports = true
EOF

# Create .pylintrc
echo "Creating .pylintrc..."
cat > .pylintrc << EOF
[MASTER]
ignore=external
extension-pkg-whitelist=numpy

[MESSAGES CONTROL]
disable=C0111,R0903,C0103,R0902,R0913,R0914,C0301,W0212,C0330,C0326,W0511,R0801,R0201,R0901,C0413,E1101,E0611,R0915,W0613,E0001

[FORMAT]
max-line-length=100

[DESIGN]
max-args=10
max-attributes=15
max-locals=25
max-returns=10
max-branches=15
max-statements=60
max-parents=7
max-complexity=15

[SIMILARITIES]
min-similarity-lines=6
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=yes
EOF

# Create .pre-commit-config.yaml
echo "Creating .pre-commit-config.yaml..."
cat > .pre-commit-config.yaml << EOF
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
    -   id: isort
        args: ["--profile", "black"]

-   repo: local
    hooks:
    -   id: pylint
        name: pylint
        entry: pylint
        language: system
        types: [python]
        args:
          [
            "-rn", # Only display messages
            "-sn", # Don't display the score
            "--recursive=y",
            "--ignore=external,venv",
          ]

    -   id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
        exclude: "external/|venv/"
        args: ["--ignore-missing-imports"]

    -   id: bandit
        name: bandit
        entry: bandit
        language: system
        types: [python]
        exclude: "tests/"
        args: ["-c", "pyproject.toml"]
EOF

# Create a setup.cfg for pytest
echo "Creating setup.cfg for pytest..."
cat > setup.cfg << EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = --cov=models --cov-report=term --cov-report=html

[coverage:run]
omit =
    */tests/*
    */external/*
    */venv/*
EOF

# Create a minimal test directory and example
mkdir -p tests
if [ ! -f "tests/__init__.py" ]; then
    touch tests/__init__.py
fi

if [ ! -f "tests/test_example.py" ]; then
    echo "Creating example test file..."
    cat > tests/test_example.py << EOF
"""
Example test file to demonstrate pytest functionality.
"""
import unittest

class TestExample(unittest.TestCase):
    """Example test class."""

    def test_addition(self):
        """Test that addition works correctly."""
        self.assertEqual(1 + 1, 2)
EOF
fi

# Initialize pre-commit
echo "Installing pre-commit hooks..."
pre-commit install

echo "Setup complete! Your code quality tools are ready to use."
echo ""
echo "Usage:"
echo "  - Pre-commit hooks will run automatically on git commit"
echo "  - Run Black manually: black ."
echo "  - Run Pylint manually: pylint models scripts"
echo "  - Run MyPy manually: mypy models scripts"
echo "  - Run tests: pytest"
echo "  - Generate test coverage: pytest --cov=models --cov-report=html"
echo "  - Run security check: bandit -r models scripts"
