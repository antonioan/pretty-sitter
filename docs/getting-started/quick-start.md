# Quick Start Tutorial

Get up and running with pretty-sitter in just 5 minutes! This tutorial will walk you through the essential steps to start pretty-printing tree-sitter parse trees.

## Prerequisites

- Python 3.11 or higher installed
- Basic familiarity with Python programming
- A terminal or command prompt

## Step 1: Installation

Install pretty-sitter and the Python tree-sitter parser:

```bash
pip install pretty-sitter
pip install tree-sitter-python
```

## Step 2: Basic Setup

Create a new Python file called `quick_start.py` and add the following code:

```python
from pretty_sitter import PrettySitter
from tree_sitter import Language, Parser
import tree_sitter_python as tspython

# Set up the tree-sitter parser for Python
language = Language(tspython.language(), "python")
parser = Parser()
parser.set_language(language)

# Create a PrettySitter instance
ps = PrettySitter()
```

## Step 3: Parse and Pretty Print Your First Code

Add this code to parse a simple Python function:

```python
# Sample Python code to parse
code = b'''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''

# Parse the code into a tree
tree = parser.parse(code)

# Pretty print the parse tree
print("🌳 Parse Tree Visualization:")
ps.pprint(tree.root_node)
```

## Step 4: Run Your First Example

Execute your script:

```bash
python quick_start.py
```

You should see a beautifully formatted, colorized parse tree that looks something like this:

```
🌳 Parse Tree Visualization:
Color legend: Leaves
(module                                                                           
    (function_definition                                                          
        name: (identifier)                                                        2: fibonacci
        parameters: (parameters                                                   
            (identifier)                                                          2: n
        )                                                                         
        body: (block                                                              
            (expression_statement                                                 
                (string)                                                          3: "Calculate the nth Fibonacci number."
            )                                                                     
            (if_statement                                                         
                condition: (comparison_operator                                   
                    (identifier)                                                  4: n
                    (integer)                                                     4: 1
                )                                                                 
                consequence: (block                                               
                    (return_statement                                             
                        (identifier)                                              5: n
                    )                                                             
                )                                                                 
            )                                                                     
            (return_statement                                                     
                (binary_operator                                                  
                    left: (call                                                   
                        function: (identifier)                                    6: fibonacci
                        arguments: (argument_list                                 
                            (binary_operator                                      
                                left: (identifier)                                6: n
                                right: (integer)                                  6: 1
                            )                                                     
                        )                                                         
                    )                                                             
                    right: (call                                                  
                        function: (identifier)                                    6: fibonacci
                        arguments: (argument_list                                 
                            (binary_operator                                      
                                left: (identifier)                                6: n
                                right: (integer)                                  6: 2
                            )                                                     
                        )                                                         
                    )                                                             
                )                                                                 
            )                                                                     
        )                                                                         
    )                                                                             
)
```

## Step 5: Customize the Output

Now let's explore some customization options. Add this code to see different formatting styles:

```python
from pretty_sitter.config import UIConfig, FilterConfig

print("\n📝 Without text content (structure only):")
ps.pprint(tree.root_node, UIConfig(with_text=False))

print("\n🎯 Focus on function definitions and calls:")
ps.pprint(tree.root_node, FilterConfig(
    only_types=['function_definition', 'call', 'identifier']
))

print("\n🎨 Compact format with smaller indentation:")
ps.pprint(tree.root_node, UIConfig(
    indent_size=2,
    column_width=60,
    with_text=False
))
```

## Step 6: Try Different Programming Languages

Pretty-sitter works with any language supported by tree-sitter. Here's how to try JavaScript:

```bash
# Install JavaScript parser
pip install tree-sitter-javascript
```

Add this to your script:

```python
import tree_sitter_javascript as tsjs

# Set up JavaScript parser
js_language = Language(tsjs.language(), "javascript")
js_parser = Parser()
js_parser.set_language(js_language)

# Parse JavaScript code
js_code = b'''
function greet(name) {
    return `Hello, ${name}!`;
}

const message = greet("World");
console.log(message);
'''

js_tree = js_parser.parse(js_code)

print("\n🟨 JavaScript Parse Tree:")
ps.pprint(js_tree.root_node)
```

## Understanding the Output

The pretty-printed output shows:

- **Node types** in parentheses (e.g., `function_definition`, `identifier`)
- **Field names** when nodes have named fields (e.g., `name:`, `parameters:`)
- **Line numbers** on the right showing where each node appears in the source
- **Text content** showing the actual code text for leaf nodes
- **Colors** to distinguish different types of nodes:
  - Blue for structural nodes
  - Cyan for leaf nodes (actual text content)
  - Gray for line numbers and less important elements

## Next Steps

Congratulations! You've successfully set up pretty-sitter and created your first parse tree visualizations. Here's what to explore next:

### 🔧 **Configuration Options**
- **[Configuration Guide](../guides/configuration-guide.md)** - Learn about all available customization options
- **[Basic Examples](basic-examples.md)** - See common usage patterns and configurations

### 🎯 **Advanced Features**
- **[Advanced Usage](../guides/advanced-usage.md)** - Explore filtering, marking, and performance optimization
- **[Integration Examples](../guides/integration-examples.md)** - Learn how to integrate with other tools

### 📚 **Reference Documentation**
- **[API Reference](../reference/api/)** - Complete documentation of all classes and methods
- **[Configuration Options](../reference/configuration-options.md)** - Detailed reference for all config parameters

### 🛠️ **Troubleshooting**
- **[Common Issues](../troubleshooting/common-issues.md)** - Solutions to frequent problems
- **[FAQ](../troubleshooting/faq.md)** - Answers to common questions

## Common Use Cases

Here are some practical applications you can explore:

### Code Analysis
```python
# Focus on function definitions to understand code structure
ps.pprint(tree.root_node, FilterConfig(
    only_types=['function_definition', 'class_definition']
))
```

### Debugging Parsers
```python
# Enable debug mode to see processing details
from pretty_sitter.config import DebugConfig
ps.pprint(tree.root_node, DebugConfig(debug=True))
```

### Educational Tools
```python
# Clean output for teaching programming concepts
ps.pprint(tree.root_node, UIConfig(
    with_text=False,
    print_with_color=False,
    indent_size=2
))
```

### Large File Analysis
```python
# Use pager for large parse trees
from pretty_sitter.config import TTYConfig
ps.pprint(tree.root_node, TTYConfig(use_pager=True))
```

## Tips for Success

1. **Start Simple**: Begin with basic `ps.pprint(node)` calls before adding configurations
2. **Experiment with Filters**: Use `only_types` to focus on specific node types you care about
3. **Check Terminal Colors**: Ensure your terminal supports ANSI colors for the best experience
4. **Use Pager for Large Trees**: Enable `use_pager=True` when working with large files
5. **Combine Configurations**: You can pass multiple config objects to customize different aspects

## Getting Help

If you run into issues:

1. Check the [Installation Guide](installation.md) for setup problems
2. Review [Common Issues](../troubleshooting/common-issues.md) for known solutions
3. Visit our [GitHub Issues](https://github.com/antonioan/pretty-sitter/issues) for community support

Happy parsing! 🎉