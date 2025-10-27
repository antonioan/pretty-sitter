# Installation Guide

This guide provides comprehensive instructions for installing pretty-sitter in different Python environments and scenarios.

## System Requirements

- **Python**: 3.11 or higher
- **Operating System**: Linux, macOS, or Windows
- **Terminal**: Color-capable terminal recommended for best experience

## Quick Installation

For most users, the simplest installation method is using pip:

```bash
pip install pretty-sitter
```

## Installation Methods

### Method 1: Using pip (Recommended)

#### Standard Installation

Install the latest stable release from PyPI:

```bash
pip install pretty-sitter
```

#### Development Version

To install the latest development version directly from GitHub:

```bash
pip install git+https://github.com/antonioan/pretty-sitter.git
```

#### With Optional Dependencies

Install with documentation building capabilities:

```bash
pip install "pretty-sitter[docs]"
```

Install with development dependencies:

```bash
pip install "pretty-sitter[dev]"
```

Install with all optional dependencies:

```bash
pip install "pretty-sitter[dev,docs]"
```

### Method 2: Using conda

If you prefer conda for package management:

```bash
# Add conda-forge channel if not already added
conda config --add channels conda-forge

# Install pretty-sitter
conda install pretty-sitter
```

**Note**: If pretty-sitter is not available on conda-forge, you can still use pip within your conda environment:

```bash
conda create -n pretty-sitter-env python=3.11
conda activate pretty-sitter-env
pip install pretty-sitter
```

### Method 3: Using Poetry

For projects using Poetry for dependency management:

```bash
# Add to your project
poetry add pretty-sitter

# Or for development dependencies
poetry add --group dev pretty-sitter
```

Add to your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
pretty-sitter = "^0.0.1"

# Or for development dependencies
[tool.poetry.group.dev.dependencies]
pretty-sitter = "^0.0.1"
```

### Method 4: Using pipenv

For projects using pipenv:

```bash
# Install for production
pipenv install pretty-sitter

# Or install for development
pipenv install --dev pretty-sitter
```

### Method 5: From Source

For contributors or users who need the absolute latest changes:

```bash
# Clone the repository
git clone https://github.com/antonioan/pretty-sitter.git
cd pretty-sitter

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev,docs]"
```

## Tree-sitter Language Setup

pretty-sitter requires tree-sitter language parsers to work with specific programming languages. Here's how to set them up:

### Installing Language Parsers

#### Python Parser (Most Common)

```bash
# Using the development dependencies (recommended)
pip install "pretty-sitter[dev]"

# Or install manually
pip install git+https://github.com/tree-sitter/tree-sitter-python.git
```

#### Other Language Parsers

For other languages, you'll need to install the corresponding tree-sitter parser:

```bash
# JavaScript/TypeScript
pip install tree-sitter-javascript

# Java
pip install tree-sitter-java

# C/C++
pip install tree-sitter-c tree-sitter-cpp

# Rust
pip install tree-sitter-rust

# Go
pip install tree-sitter-go
```

### Building Language Libraries

Some parsers may require compilation. Here's how to build them:

```python
from tree_sitter import Language, Parser

# Build the language library
Language.build_library(
    # Store the library in the current directory
    'build/my-languages.so',
    
    # Include one or more languages
    [
        'vendor/tree-sitter-python',
        'vendor/tree-sitter-javascript',
    ]
)
```

## Installation Verification

### Basic Verification

Verify that pretty-sitter is installed correctly:

```bash
python -c "import pretty_sitter; print('pretty-sitter installed successfully!')"
```

### Complete Verification

Test the full installation with a simple example:

```python
# test_installation.py
from pretty_sitter import PrettySitter
from tree_sitter import Language, Parser
import tree_sitter_python as tspython

# Set up the parser
language = Language(tspython.language(), "python")
parser = Parser()
parser.set_language(language)

# Parse a simple Python snippet
code = b'def hello(): return "world"'
tree = parser.parse(code)

# Test pretty-sitter
ps = PrettySitter()
print("Installation verification successful!")
ps.pprint(tree.root_node)
```

Run the verification:

```bash
python test_installation.py
```

Expected output should show a colorized parse tree representation.

## Troubleshooting

### Common Installation Issues

#### Issue: "No module named 'tree_sitter'"

**Solution**: Install the tree-sitter dependency:

```bash
pip install tree-sitter
```

#### Issue: "Microsoft Visual C++ 14.0 is required" (Windows)

**Solution**: Install Microsoft C++ Build Tools:

1. Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Or install Visual Studio with C++ development tools
3. Retry the installation

#### Issue: "Failed building wheel for tree-sitter"

**Solution**: Install build dependencies:

```bash
# On Ubuntu/Debian
sudo apt-get install build-essential

# On CentOS/RHEL/Fedora
sudo yum groupinstall "Development Tools"
# or
sudo dnf groupinstall "Development Tools"

# On macOS
xcode-select --install
```

#### Issue: Language parser not found

**Solution**: Ensure language parsers are installed:

```bash
# Check what's installed
pip list | grep tree-sitter

# Install missing parsers
pip install tree-sitter-python  # or other language parsers
```

#### Issue: Colors not displaying in terminal

**Solution**: Verify terminal color support:

```python
import sys
print(f"Terminal supports color: {sys.stdout.isatty()}")

# Force color output if needed
from pretty_sitter.config import TTYConfig
ps.pprint(tree.root_node, TTYConfig(force_color=True))
```

### Environment-Specific Issues

#### Virtual Environments

If you're having issues with virtual environments:

```bash
# Ensure you're in the correct environment
which python
which pip

# Recreate the environment if needed
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install pretty-sitter
```

#### Permission Issues

If you encounter permission errors:

```bash
# Install for current user only
pip install --user pretty-sitter

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install pretty-sitter
```

### Getting Help

If you continue to experience issues:

1. **Check the [FAQ](../troubleshooting/faq.md)** for common questions
2. **Review [Common Issues](../troubleshooting/common-issues.md)** for known problems
3. **Search existing [GitHub Issues](https://github.com/antonioan/pretty-sitter/issues)**
4. **Create a new issue** with:
   - Your operating system and version
   - Python version (`python --version`)
   - Installation method used
   - Complete error message
   - Steps to reproduce the issue

## Next Steps

Once installation is complete:

1. **[Quick Start Tutorial](quick-start.md)** - Get up and running in 5 minutes
2. **[Basic Examples](basic-examples.md)** - Common usage patterns
3. **[Configuration Guide](../guides/configuration-guide.md)** - Customize pretty-sitter for your needs
4. **[API Reference](../reference/api/)** - Detailed documentation of all features

## Development Installation

For contributors who want to set up a development environment:

```bash
# Clone the repository
git clone https://github.com/antonioan/pretty-sitter.git
cd pretty-sitter

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode with all dependencies
pip install -e ".[dev,docs]"

# Verify development setup
python -m pytest tests/
```

See the [Development Setup Guide](../contributing/development-setup.md) for complete development environment configuration.