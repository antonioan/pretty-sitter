# Basic Examples

This guide provides practical examples of common pretty-sitter usage patterns. Each example includes complete, runnable code that demonstrates specific features and use cases.

## Table of Contents

- [Setup and Basic Usage](#setup-and-basic-usage)
- [Language-Specific Examples](#language-specific-examples)
- [Configuration Examples](#configuration-examples)
- [Filtering Examples](#filtering-examples)
- [Output Customization](#output-customization)
- [Practical Use Cases](#practical-use-cases)

## Setup and Basic Usage

### Basic Setup Template

Here's a reusable template for setting up pretty-sitter with any language:

```python
from pretty_sitter import PrettySitter
from tree_sitter import Language, Parser

def setup_parser(language_module, language_name):
    """Set up a tree-sitter parser for a specific language."""
    language = Language(language_module.language(), language_name)
    parser = Parser()
    parser.set_language(language)
    return parser

# Example usage
import tree_sitter_python as tspython
parser = setup_parser(tspython, "python")
ps = PrettySitter()
```

### Simple Parse and Print

```python
# Parse a simple code snippet
code = b'print("Hello, World!")'
tree = parser.parse(code)

# Pretty print with default settings
ps.pprint(tree.root_node)
```

## Language-Specific Examples

### Python

```python
import tree_sitter_python as tspython

# Set up Python parser
python_parser = setup_parser(tspython, "python")

# Example: Class with methods
python_code = b'''
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x, y):
        """Add two numbers."""
        return x + y
    
    def multiply(self, x, y):
        return x * y

calc = Calculator()
result = calc.add(5, 3)
'''

tree = python_parser.parse(python_code)
ps.pprint(tree.root_node)
```

### JavaScript

```python
import tree_sitter_javascript as tsjs

# Set up JavaScript parser
js_parser = setup_parser(tsjs, "javascript")

# Example: Modern JavaScript with arrow functions
js_code = b'''
const users = [
    { name: "Alice", age: 30 },
    { name: "Bob", age: 25 }
];

const adults = users
    .filter(user => user.age >= 18)
    .map(user => user.name);

console.log(adults);
'''

tree = js_parser.parse(js_code)
ps.pprint(tree.root_node)
```

### Java

```python
import tree_sitter_java as tsjava

# Set up Java parser
java_parser = setup_parser(tsjava, "java")

# Example: Simple Java class
java_code = b'''
public class HelloWorld {
    private String message;
    
    public HelloWorld(String message) {
        this.message = message;
    }
    
    public void greet() {
        System.out.println(message);
    }
    
    public static void main(String[] args) {
        HelloWorld hello = new HelloWorld("Hello, World!");
        hello.greet();
    }
}
'''

tree = java_parser.parse(java_code)
ps.pprint(tree.root_node)
```

### C/C++

```python
import tree_sitter_c as tsc

# Set up C parser
c_parser = setup_parser(tsc, "c")

# Example: C function with struct
c_code = b'''
#include <stdio.h>

struct Point {
    int x;
    int y;
};

int distance_squared(struct Point p1, struct Point p2) {
    int dx = p1.x - p2.x;
    int dy = p1.y - p2.y;
    return dx * dx + dy * dy;
}

int main() {
    struct Point a = {0, 0};
    struct Point b = {3, 4};
    printf("Distance squared: %d\\n", distance_squared(a, b));
    return 0;
}
'''

tree = c_parser.parse(c_code)
ps.pprint(tree.root_node)
```

## Configuration Examples

### UI Configuration

```python
from pretty_sitter.config import UIConfig

# Minimal output without text content
print("=== Structure Only ===")
ps.pprint(tree.root_node, UIConfig(with_text=False))

# Compact format with small indentation
print("\n=== Compact Format ===")
ps.pprint(tree.root_node, UIConfig(
    indent_size=2,
    column_width=50,
    with_text=False
))

# Plain text output (no colors)
print("\n=== Plain Text ===")
ps.pprint(tree.root_node, UIConfig(
    print_with_color=False,
    color_legend=False
))

# With dotted column guides
print("\n=== With Dotted Guides ===")
ps.pprint(tree.root_node, UIConfig(
    dotted=True,
    column_width=80
))
```

### Filter Configuration

```python
from pretty_sitter.config import FilterConfig

# Show only function definitions
print("=== Functions Only ===")
ps.pprint(tree.root_node, FilterConfig(
    only_types=['function_definition', 'method_definition']
))

# Exclude comments and docstrings
print("\n=== No Comments ===")
ps.pprint(tree.root_node, FilterConfig(
    excluded_types=['comment', 'string']
))

# Focus on control flow structures
print("\n=== Control Flow ===")
ps.pprint(tree.root_node, FilterConfig(
    only_types=['if_statement', 'for_statement', 'while_statement', 'try_statement']
))
```

### Terminal Configuration

```python
from pretty_sitter.config import TTYConfig

# Use pager for large outputs
ps.pprint(tree.root_node, TTYConfig(use_pager=True))

# Force color output even in non-TTY environments
from pretty_sitter.config import UIConfig
ps.pprint(tree.root_node, UIConfig(print_with_color=True))
```

## Filtering Examples

### Focus on Specific Node Types

```python
# Show only variable declarations and assignments
ps.pprint(tree.root_node, FilterConfig(
    only_types=[
        'variable_declaration',
        'assignment_expression',
        'identifier',
        'literal'
    ]
))

# Show only function calls
ps.pprint(tree.root_node, FilterConfig(
    only_types=['call_expression', 'call', 'identifier']
))

# Show class and function structure
ps.pprint(tree.root_node, FilterConfig(
    only_types=[
        'class_definition',
        'function_definition',
        'method_definition',
        'identifier'
    ]
))
```

### Exclude Noise

```python
# Remove trivial punctuation and whitespace
ps.pprint(tree.root_node, FilterConfig(
    excluded_types=[
        'comment',
        ';',
        ',',
        '(',
        ')',
        '{',
        '}',
        '[',
        ']'
    ]
))

# Focus on semantic content
ps.pprint(tree.root_node, UIConfig(
    with_trivial=False  # Hide nodes where type equals text
))
```

## Output Customization

### Combining Multiple Configurations

```python
from pretty_sitter.config import UIConfig, FilterConfig, TTYConfig

# Create a custom configuration for code review
code_review_config = [
    UIConfig(
        with_text=True,
        indent_size=2,
        column_width=60,
        print_with_color=True
    ),
    FilterConfig(
        only_types=[
            'function_definition',
            'class_definition',
            'method_definition',
            'identifier',
            'parameters',
            'return_statement'
        ]
    )
]

ps.pprint(tree.root_node, *code_review_config)
```

### Context Manager for Temporary Configuration

```python
# Temporarily change configuration
with ps.configure(UIConfig(with_text=False, indent_size=1)):
    print("=== Temporary Compact View ===")
    ps.pprint(tree.root_node)

# Original configuration is restored automatically
print("\n=== Back to Original ===")
ps.pprint(tree.root_node)
```

## Practical Use Cases

### Code Structure Analysis

```python
def analyze_code_structure(code, parser):
    """Analyze the high-level structure of code."""
    tree = parser.parse(code)
    
    print("=== Code Structure Analysis ===")
    ps.pprint(tree.root_node, FilterConfig(
        only_types=[
            'module',
            'class_definition',
            'function_definition',
            'method_definition',
            'import_statement',
            'import_from_statement',
            'identifier'
        ]
    ), UIConfig(
        with_text=True,
        indent_size=2
    ))

# Example usage
python_code = b'''
import os
from typing import List

class DataProcessor:
    def __init__(self, data_path: str):
        self.data_path = data_path
    
    def load_data(self) -> List[str]:
        with open(self.data_path, 'r') as f:
            return f.readlines()
    
    def process_data(self, data: List[str]) -> List[str]:
        return [line.strip().upper() for line in data]

def main():
    processor = DataProcessor("data.txt")
    data = processor.load_data()
    processed = processor.process_data(data)
    print(processed)
'''

analyze_code_structure(python_code, python_parser)
```

### Function Call Analysis

```python
def analyze_function_calls(code, parser):
    """Find all function calls in the code."""
    tree = parser.parse(code)
    
    print("=== Function Calls ===")
    ps.pprint(tree.root_node, FilterConfig(
        only_types=['call', 'call_expression', 'identifier', 'attribute']
    ), UIConfig(
        with_text=True,
        column_width=40
    ))

# Example with JavaScript
js_code = b'''
function fetchData(url) {
    return fetch(url)
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
}

const api = new APIClient();
api.authenticate("token");
fetchData("https://api.example.com/data");
'''

analyze_function_calls(js_code, js_parser)
```

### Error Location Debugging

```python
def debug_parse_errors(code, parser):
    """Help debug parsing issues by showing detailed structure."""
    tree = parser.parse(code)
    
    print("=== Debug Parse Tree ===")
    from pretty_sitter.config import DebugConfig
    
    ps.pprint(tree.root_node, 
        DebugConfig(debug=True),
        UIConfig(with_text=True, indent_size=2)
    )
    
    # Check for ERROR nodes
    def find_errors(node):
        if node.type == 'ERROR':
            print(f"ERROR found at line {node.start_point[0] + 1}: {node.text}")
        for child in node.children:
            find_errors(child)
    
    find_errors(tree.root_node)

# Example with intentionally broken code
broken_code = b'''
def broken_function(
    print("Missing closing parenthesis")
    return "This won't parse correctly"
'''

debug_parse_errors(broken_code, python_parser)
```

### Educational Code Visualization

```python
def create_teaching_example(code, parser, title):
    """Create clean visualizations for teaching programming concepts."""
    tree = parser.parse(code)
    
    print(f"=== {title} ===")
    
    # Clean, educational format
    ps.pprint(tree.root_node, 
        UIConfig(
            with_text=False,
            print_with_color=False,
            color_legend=False,
            indent_size=3,
            close_pars_early=True
        ),
        FilterConfig(
            excluded_types=['comment', 'docstring']
        )
    )

# Example: Teaching recursion
recursion_code = b'''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''

create_teaching_example(recursion_code, python_parser, "Recursion Structure")
```

## Performance Tips

### Working with Large Files

```python
# For large files, use filtering to focus on relevant parts
def analyze_large_file(code, parser):
    tree = parser.parse(code)
    
    # Only show top-level definitions
    ps.pprint(tree.root_node, FilterConfig(
        only_types=[
            'class_definition',
            'function_definition',
            'import_statement',
            'identifier'
        ]
    ), UIConfig(
        with_text=False,  # Faster rendering
        indent_size=1     # More compact
    ))

# Use pager for very large outputs
def view_large_tree(code, parser):
    tree = parser.parse(code)
    ps.pprint(tree.root_node, TTYConfig(use_pager=True))
```

### Batch Processing

```python
def process_multiple_files(file_paths, parser):
    """Process multiple files efficiently."""
    for file_path in file_paths:
        print(f"\n=== {file_path} ===")
        
        with open(file_path, 'rb') as f:
            code = f.read()
        
        tree = parser.parse(code)
        
        # Quick overview of each file
        ps.pprint(tree.root_node, FilterConfig(
            only_types=['function_definition', 'class_definition']
        ), UIConfig(
            with_text=False,
            indent_size=1
        ))
```

## Next Steps

Now that you've seen these basic examples, you can:

1. **[Explore Advanced Usage](../guides/advanced-usage.md)** - Learn about marking nodes, performance optimization, and complex filtering
2. **[Read the Configuration Guide](../guides/configuration-guide.md)** - Understand all available configuration options in detail
3. **[Check the API Reference](../reference/api/)** - Dive deep into the complete API documentation
4. **[See Integration Examples](../guides/integration-examples.md)** - Learn how to integrate pretty-sitter with other tools

## Common Patterns Summary

Here are the most useful patterns from these examples:

```python
# Quick structure overview
ps.pprint(node, UIConfig(with_text=False))

# Focus on functions and classes
ps.pprint(node, FilterConfig(only_types=['function_definition', 'class_definition']))

# Clean educational output
ps.pprint(node, UIConfig(print_with_color=False, with_text=False))

# Debug parsing issues
ps.pprint(node, DebugConfig(debug=True))

# Handle large outputs
ps.pprint(node, TTYConfig(use_pager=True))

# Combine multiple configurations
ps.pprint(node, UIConfig(...), FilterConfig(...), TTYConfig(...))
```

These patterns will cover most of your pretty-sitter usage needs!