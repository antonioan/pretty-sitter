# Frequently Asked Questions

## General Usage

### What is pretty-sitter and what does it do?

pretty-sitter is a Python library that provides pretty printing functionality for tree-sitter parse trees. It allows you to visualize the structure of source code in a formatted, colorized manner, making it easier to understand how tree-sitter parses your code.

### Which programming languages does pretty-sitter support?

pretty-sitter works with any programming language that has a tree-sitter grammar. Popular languages include:

- Python (`tree-sitter-python`)
- JavaScript/TypeScript (`tree-sitter-javascript`, `tree-sitter-typescript`)
- Java (`tree-sitter-java`)
- C/C++ (`tree-sitter-c`, `tree-sitter-cpp`)
- Rust (`tree-sitter-rust`)
- Go (`tree-sitter-go`)
- And many more...

You need to install the specific tree-sitter language library for each language you want to use.

### How do I install language support for my programming language?

Each language requires its own tree-sitter library. Install them using pip:

```bash
# For Python
pip install tree-sitter-python

# For JavaScript
pip install tree-sitter-javascript

# For other languages, follow the pattern:
pip install tree-sitter-<language-name>
```

### Can I use pretty-sitter without installing tree-sitter language libraries?

No, you need at least one tree-sitter language library to parse code. pretty-sitter itself only provides the pretty printing functionality - it relies on tree-sitter and language-specific libraries for parsing.

## Configuration and Customization

### How do I change the colors used in the output?

pretty-sitter uses a predefined color scheme, but you can customize it in several ways:

1. **Disable colors entirely**:
   ```python
   from pretty_sitter.config import UIConfig
   ps = PrettySitter(UIConfig(print_with_color=False))
   ```

2. **Use marking for custom colors**:
   ```python
   from pretty_sitter.config import MarkingConfig
   ps = PrettySitter(MarkingConfig(marks=[
       ('Important', 'red', [node1, node2]),
       ('Optional', 'blue', [node3])
   ]))
   ```

3. **Available colors**: red, green, green2, yellow, blue, cyan, gray

### How do I filter the output to show only specific node types?

Use `FilterConfig` to control which nodes are displayed:

```python
from pretty_sitter.config import FilterConfig

# Show only function and class definitions
ps = PrettySitter(FilterConfig(only_types=['function_definition', 'class_definition']))

# Exclude comments and whitespace
ps = PrettySitter(FilterConfig(excluded_types=['comment', 'whitespace']))

# Combine both (only_types is applied first, then excluded_types)
ps = PrettySitter(FilterConfig(
    only_types=['function_definition', 'class_definition'],
    excluded_types=['comment']
))
```

### How do I find out what node types are available for my language?

You can discover available node types by examining a parse tree:

```python
def collect_node_types(node, types=None):
    if types is None:
        types = set()
    types.add(node.type)
    for child in node.children:
        collect_node_types(child, types)
    return types

# Parse some code and collect types
tree = parser.parse(b"your code here")
available_types = collect_node_types(tree.root_node)
print("Available node types:", sorted(available_types))
```

### Can I temporarily change configuration for a single print operation?

Yes, use the `configure()` context manager or pass configs directly to `pprint()`:

```python
ps = PrettySitter()  # Default configuration

# Method 1: Context manager
with ps.configure(UIConfig(with_text=False)):
    ps.pprint(node)  # Prints without text content

# Method 2: Direct parameter
ps.pprint(node, UIConfig(with_text=False))  # Same effect
```

### How do I adjust the output width and formatting?

Use `UIConfig` to control formatting:

```python
from pretty_sitter.config import UIConfig

ps = PrettySitter(UIConfig(
    column_width=60,      # Adjust column width
    indent_size=2,        # Use 2 spaces for indentation
    dotted=True,          # Use dots for column alignment
    close_pars_early=False  # Don't close parentheses early
))
```

## Terminal and Display

### Why don't I see colors in my terminal?

This usually happens due to terminal compatibility issues:

1. **Check your TERM environment variable**:
   ```bash
   echo $TERM
   ```
   Should be `xterm-256color`, `screen-256color`, or `linux`.

2. **Set the correct TERM value**:
   ```bash
   export TERM=xterm-256color
   ```

3. **Test if your terminal supports colors**:
   ```bash
   echo -e "\033[31mRed\033[0m \033[32mGreen\033[0m"
   ```

4. **Use a color-capable terminal** like modern versions of Terminal.app, iTerm2, GNOME Terminal, or Windows Terminal.

### How do I use the pager feature?

Enable the pager to handle large outputs:

```python
from pretty_sitter.config import TTYConfig
ps = PrettySitter(TTYConfig(use_pager=True))
ps.pprint(large_tree)  # Output will be displayed in 'less'
```

**Requirements for pager**:
- Must be running in a TTY (not redirected output)
- `less` command must be available in your PATH
- Works best in interactive terminal sessions

### Can I save the output to a file?

Yes, but disable colors and pager for file output:

```python
from pretty_sitter.config import UIConfig, TTYConfig

# Configuration for file output
ps = PrettySitter(
    UIConfig(print_with_color=False, color_legend=False),
    TTYConfig(use_pager=False)
)

# Redirect output to file
import sys
with open('output.txt', 'w') as f:
    sys.stdout = f
    ps.pprint(tree.root_node)
    sys.stdout = sys.__stdout__  # Restore stdout
```

## Performance and Large Files

### pretty-sitter is slow with large files. How can I improve performance?

Several strategies can help with large files:

1. **Filter to relevant nodes only**:
   ```python
   # Instead of printing everything
   ps = PrettySitter(FilterConfig(only_types=['function_definition']))
   ```

2. **Disable expensive features**:
   ```python
   ps = PrettySitter(UIConfig(
       with_text=False,        # Skip text content
       print_with_color=False, # Skip color processing
       color_legend=False      # Skip legend
   ))
   ```

3. **Print specific subtrees**:
   ```python
   # Find and print only functions
   def print_functions(node):
       if node.type == 'function_definition':
           ps.pprint(node)
       for child in node.children:
           print_functions(child)
   ```

### How much memory does pretty-sitter use?

Memory usage depends on:
- Size of the parse tree (number of nodes)
- Whether text content is included (`with_text=True`)
- Number of marked nodes
- Use of pager (collects all output in memory first)

For very large files, consider processing subtrees individually rather than the entire tree at once.

## Integration and Advanced Usage

### How do I integrate pretty-sitter with tree-tagger for semantic highlighting?

tree-tagger provides semantic analysis that can be used with pretty-sitter's marking system:

```python
from pretty_sitter import PrettySitter
from pretty_sitter.config import FilterConfig, MarkingConfig

# Optional: handle missing tree-tagger gracefully
try:
    from tree_tagger import TreeTagger
    
    tree_tagger = TreeTagger(language, language_name)
    tags = tree_tagger.tag(root, find_usage_definitions=True)
    
    marking_config = MarkingConfig(
        definition_nodes=tags.definition_nodes,
        usage_nodes=tags.defined_usage_nodes,
        undefined_usage_nodes=tags.undefined_usage_nodes,
    )
    
    ps = PrettySitter(FilterConfig(only_types=["identifier"]), marking_config)
except ImportError:
    print("tree-tagger not available, using basic highlighting")
    ps = PrettySitter(FilterConfig(only_types=["identifier"]))

ps.pprint(root)
```

### Can I use pretty-sitter in Jupyter notebooks?

Yes, pretty-sitter works in Jupyter notebooks, but you may need to adjust the configuration:

```python
# Jupyter-friendly configuration
from pretty_sitter.config import UIConfig, TTYConfig

ps = PrettySitter(
    UIConfig(print_with_color=True),  # Colors usually work in Jupyter
    TTYConfig(use_pager=False)        # Disable pager in notebooks
)
```

### How do I create custom node marking based on my own analysis?

You can mark any nodes with custom colors and labels:

```python
from pretty_sitter.config import MarkingConfig

# Analyze your tree and collect nodes of interest
important_nodes = []
warning_nodes = []

def analyze_tree(node):
    if some_condition(node):
        important_nodes.append(node)
    elif other_condition(node):
        warning_nodes.append(node)
    
    for child in node.children:
        analyze_tree(child)

analyze_tree(tree.root_node)

# Create marking configuration
marking_config = MarkingConfig(marks=[
    ('Important', 'red', important_nodes),
    ('Warnings', 'yellow', warning_nodes)
])

ps = PrettySitter(marking_config)
ps.pprint(tree.root_node)
```

## Troubleshooting

### I'm getting "ModuleNotFoundError" for tree-sitter languages. What's wrong?

This means the language library isn't installed. Each language needs its own package:

```bash
# Check what you have installed
pip list | grep tree-sitter

# Install missing languages
pip install tree-sitter-python  # or whatever language you need
```

### The output looks garbled or has strange characters. How do I fix this?

This is usually an encoding or terminal issue:

1. **Check your terminal encoding** (should be UTF-8)
2. **Ensure your code is properly encoded**:
   ```python
   # Correct
   tree = parser.parse(bytes(code, "utf8"))
   
   # May cause issues
   tree = parser.parse(code.encode())  # Uses default encoding
   ```

3. **Try disabling colors**:
   ```python
   ps = PrettySitter(UIConfig(print_with_color=False))
   ```

### pretty-sitter shows no output. What could be wrong?

Common causes:

1. **Overly restrictive filtering**:
   ```python
   # Check if your filter is too narrow
   ps = PrettySitter(FilterConfig(only_types=['nonexistent_type']))
   ```

2. **All nodes are considered trivial**:
   ```python
   # Try including trivial nodes
   ps = PrettySitter(UIConfig(with_trivial=True))
   ```

3. **Parse errors in the input**:
   ```python
   # Check for parse errors
   def find_errors(node):
       if node.type == 'ERROR':
           print(f"Parse error: {node.text}")
       for child in node.children:
           find_errors(child)
   
   find_errors(tree.root_node)
   ```

### How do I report bugs or request features?

Please follow our bug reporting guidelines and provide:

1. **Minimal reproduction example**
2. **Your environment details** (Python version, OS, terminal)
3. **Expected vs actual behavior**
4. **Full error messages** if applicable

See our contributing documentation for detailed guidelines on reporting issues and submitting feature requests.

## Getting More Help

- **Check the troubleshooting guide** for detailed solutions to common problems
- **Review the configuration guide** for comprehensive configuration options
- **Look at the examples** in the getting started documentation
- **Enable debug output** to understand what's happening:
  ```python
  from pretty_sitter.config import DebugConfig
  ps = PrettySitter(DebugConfig(debug=True))
  ```