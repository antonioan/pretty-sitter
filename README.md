# pretty-sitter

[![PyPI version](https://badge.fury.io/py/pretty-sitter.svg)](https://badge.fury.io/py/pretty-sitter)
[![Python Support](https://img.shields.io/pypi/pyversions/pretty-sitter.svg)](https://pypi.org/project/pretty-sitter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/antonioan/pretty-sitter/workflows/CI/badge.svg)](https://github.com/antonioan/pretty-sitter/actions)
[![Documentation Status](https://readthedocs.org/projects/pretty-sitter/badge/?version=latest)](https://pretty-sitter.readthedocs.io/en/latest/?badge=latest)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A powerful and flexible pretty printer for [tree-sitter](https://tree-sitter.github.io/tree-sitter/) parse trees with rich formatting, filtering, and visualization capabilities.

## Overview

pretty-sitter transforms tree-sitter parse trees into beautifully formatted, colorized output that makes it easy to understand and analyze code structure. Whether you're debugging parsers, exploring ASTs, or building developer tools, pretty-sitter provides the visualization you need.

## Key Features

### 🎨 **Rich Visual Output**

- **Colorized syntax highlighting** with customizable color schemes
- **Configurable indentation** and formatting options
- **Column-aligned display** with optional dotted guides
- **Bold highlighting** for important node types

### 🔍 **Powerful Filtering**

- **Include/exclude node types** to focus on what matters
- **Hide trivial nodes** (where type equals text content)
- **Smart filtering** that preserves tree structure

### 🏷️ **Semantic Marking**

- **Highlight specific nodes** with custom colors and labels
- **Built-in support** for definitions, usages, and undefined references
- **Flexible marking system** for custom analysis workflows

### ⚙️ **Flexible Configuration**

- **Modular configuration system** with composable config objects
- **Context managers** for temporary configuration changes
- **Runtime reconfiguration** without recreating instances

### 🖥️ **Terminal Integration**

- **Automatic color detection** with terminal compatibility warnings
- **Pager support** for large parse trees (integrates with `less`)
- **TTY-aware output** with appropriate formatting

### 🐛 **Developer-Friendly**

- **Debug mode** with detailed processing information
- **Type hints** throughout the codebase
- **Comprehensive documentation** and examples

## Use Cases

- **Parser Development**: Visualize and debug tree-sitter grammars
- **Code Analysis**: Explore AST structure for static analysis tools
- **Educational Tools**: Teach programming language concepts through visual ASTs
- **IDE Features**: Build syntax highlighting and code navigation features
- **Research**: Analyze code patterns and language structures

## Quick Start

### Installation

Install pretty-sitter using pip:

```bash
pip install pretty-sitter
```

For development or to access the latest features:

```bash
pip install git+https://github.com/antonioan/pretty-sitter.git
```

### Basic Usage

```python
from pretty_sitter import PrettySitter
from tree_sitter import Language, Parser

# Set up tree-sitter (example with Python)
language = Language(library_path, 'python')
parser = Parser()
parser.set_language(language)

# Parse some code
code = b'''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
tree = parser.parse(code)

# Pretty print the parse tree
ps = PrettySitter()
ps.pprint(tree.root_node)
```

This will output a beautifully formatted, colorized representation of your parse tree:

```
(module
    (function_definition
        name: (identifier)                                                                    2: fibonacci
        parameters: (parameters
            (identifier)                                                                      2: n
        )
        body: (block
            (if_statement
                condition: (comparison_operator
                    (identifier)                                                              3: n
                    (integer)                                                                 3: 1
                )
                consequence: (block
                    (return_statement
                        (identifier)                                                          4: n
                    )
                )
            )
            (return_statement
                (binary_operator
                    left: (call
                        function: (identifier)                                                6: fibonacci
                        arguments: (argument_list
                            (binary_operator
                                left: (identifier)                                            6: n
                                right: (integer)                                              6: 1
                            )
                        )
                    )
                    right: (call
                        function: (identifier)                                                6: fibonacci
                        arguments: (argument_list
                            (binary_operator
                                left: (identifier)                                            6: n
                                right: (integer)                                              6: 2
                            )
                        )
                    )
                )
            )
        )
    )
)
```

### Configuration Examples

Focus on specific node types:

```python
from pretty_sitter.config import FilterConfig

# Show only function definitions and calls
ps.pprint(tree.root_node, FilterConfig(
    only_types=['function_definition', 'call']
))
```

Customize the visual appearance:

```python
from pretty_sitter.config import UIConfig

# Compact output without text content
ps.pprint(tree.root_node, UIConfig(
    with_text=False,
    indent_size=2,
    print_with_color=False
))
```

## Documentation

- **[Installation Guide](docs/getting-started/installation.md)** - Detailed setup instructions
- **[Quick Start Tutorial](docs/getting-started/quick-start.md)** - 5-minute getting started guide
- **[Configuration Guide](docs/guides/configuration-guide.md)** - Complete configuration reference
- **[API Reference](docs/reference/api/)** - Detailed API documentation
- **[Examples](docs/getting-started/basic-examples.md)** - Common usage patterns
- **[Advanced Usage](docs/guides/advanced-usage.md)** - Complex scenarios and best practices

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing/development-setup.md) for details on:

- Setting up your development environment
- Running tests and linting
- Submitting pull requests
- Coding standards and guidelines

## Support

- **[Documentation](https://pretty-sitter.readthedocs.io/)** - Complete documentation
- **[Issues](https://github.com/antonioan/pretty-sitter/issues)** - Bug reports and feature requests
- **[Discussions](https://github.com/antonioan/pretty-sitter/discussions)** - Questions and community support
- **[Changelog](CHANGELOG.md)** - Release notes and version history

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of the excellent [tree-sitter](https://tree-sitter.github.io/tree-sitter/) parsing library
- Inspired by the need for better AST visualization tools in the developer ecosystem
