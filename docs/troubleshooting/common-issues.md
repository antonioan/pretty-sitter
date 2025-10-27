# Common Issues and Solutions

This guide covers the most frequently encountered issues when using pretty-sitter and provides step-by-step solutions to resolve them.

## Installation Issues

### Tree-sitter Language Libraries Not Found

**Problem**: Getting errors like `ModuleNotFoundError: No module named 'tree_sitter_python'` or similar for other languages.

**Cause**: Tree-sitter language libraries are separate packages that need to be installed independently.

**Solution**:
```bash
# For Python language support
pip install tree-sitter-python

# For other languages, install the corresponding package
pip install tree-sitter-javascript
pip install tree-sitter-java
# etc.
```

**Alternative Solution** (building from source):
```python
from tree_sitter import Language
import tree_sitter_python

# This should work if tree-sitter-python is properly installed
language = Language(tree_sitter_python.language())
```

### Python Version Compatibility

**Problem**: Installation fails with version compatibility errors.

**Cause**: pretty-sitter requires Python 3.11 or higher.

**Solution**:
1. Check your Python version:
   ```bash
   python --version
   ```
2. If you have Python < 3.11, upgrade to Python 3.11+ or use a virtual environment with the correct version:
   ```bash
   # Using pyenv
   pyenv install 3.11.0
   pyenv local 3.11.0
   
   # Using conda
   conda create -n pretty-sitter python=3.11
   conda activate pretty-sitter
   ```

### Missing Development Dependencies

**Problem**: Import errors when trying to run examples or tests.

**Cause**: Development dependencies are not installed by default.

**Solution**:
```bash
# Install with development dependencies
pip install pretty-sitter[dev]

# Or install manually
pip install pytest tree-sitter-python
```

## Terminal and Display Issues

### Colors Not Displaying Properly

**Problem**: ANSI color codes appear as text instead of colors, or colors look wrong.

**Symptoms**:
- Seeing literal `\033[91m` codes in output
- Colors appearing incorrectly or not at all
- Warning: "color might not appear properly"

**Solutions**:

1. **Check terminal compatibility**:
   ```bash
   echo $TERM
   ```
   Should be one of: `xterm-256color`, `screen-256color`, or `linux`

2. **Set correct TERM environment variable**:
   ```bash
   export TERM=xterm-256color
   ```

3. **Disable colors if terminal doesn't support them**:
   ```python
   from pretty_sitter import PrettySitter
   from pretty_sitter.config import UIConfig
   
   ps = PrettySitter(UIConfig(print_with_color=False))
   ```

4. **Test color support**:
   ```bash
   # This should display colors
   echo -e "\033[31mRed\033[0m \033[32mGreen\033[0m \033[34mBlue\033[0m"
   ```

### Pager Issues

**Problem**: Pager not working or displaying incorrectly.

**Symptoms**:
- Warning: "paging might not work, since stdout was not detected as a TTY"
- Output appears all at once instead of in pager
- Pager crashes or displays garbled text

**Solutions**:

1. **Ensure you're running in a TTY**:
   ```python
   import sys
   print(sys.stdout.isatty())  # Should be True for pager to work
   ```

2. **Check if `less` is available**:
   ```bash
   which less
   ```

3. **Disable pager if not needed**:
   ```python
   from pretty_sitter import PrettySitter
   from pretty_sitter.config import TTYConfig
   
   ps = PrettySitter(TTYConfig(use_pager=False))
   ```

4. **For redirected output, disable pager**:
   ```bash
   # This will trigger pager warnings
   python script.py > output.txt
   
   # Better: disable pager in script when output is redirected
   ```

### Text Wrapping and Display Width

**Problem**: Output is too wide and wraps awkwardly in terminal.

**Symptoms**:
- Warning: "word wrapping might drive you crazy"
- Lines wrap at awkward positions
- Difficult to read tree structure

**Solutions**:

1. **Use pager for better navigation**:
   ```python
   from pretty_sitter import PrettySitter
   from pretty_sitter.config import TTYConfig
   
   ps = PrettySitter(TTYConfig(use_pager=True))
   ```

2. **Adjust column width**:
   ```python
   from pretty_sitter import PrettySitter
   from pretty_sitter.config import UIConfig
   
   # Reduce column width for narrower terminals
   ps = PrettySitter(UIConfig(column_width=60))
   ```

3. **Disable text content for structure-only view**:
   ```python
   from pretty_sitter import PrettySitter
   from pretty_sitter.config import UIConfig
   
   ps = PrettySitter(UIConfig(with_text=False))
   ```

## Usage and Configuration Issues

### Empty or Unexpected Output

**Problem**: pretty-sitter produces no output or doesn't show expected nodes.

**Possible Causes and Solutions**:

1. **Filtering too restrictive**:
   ```python
   # Problem: only_types is too specific
   ps = PrettySitter(FilterConfig(only_types=['nonexistent_type']))
   
   # Solution: Check available node types first
   def print_node_types(node, types=None):
       if types is None:
           types = set()
       types.add(node.type)
       for child in node.children:
           print_node_types(child, types)
       return types
   
   available_types = print_node_types(tree.root_node)
   print("Available node types:", sorted(available_types))
   ```

2. **Excluding too many types**:
   ```python
   # Problem: excluding important structural nodes
   ps = PrettySitter(FilterConfig(excluded_types=['identifier', 'string']))
   
   # Solution: Be more selective with exclusions
   ps = PrettySitter(FilterConfig(excluded_types=['comment']))
   ```

3. **Trivial nodes hidden**:
   ```python
   # Problem: important nodes are considered "trivial"
   ps = PrettySitter(UIConfig(with_trivial=False))  # Default
   
   # Solution: Include trivial nodes
   ps = PrettySitter(UIConfig(with_trivial=True))
   ```

### Parse Tree Issues

**Problem**: Tree-sitter parsing fails or produces unexpected results.

**Symptoms**:
- Empty parse trees
- Error nodes in output
- Unexpected tree structure

**Solutions**:

1. **Check input encoding**:
   ```python
   # Ensure input is properly encoded as bytes
   code = "def hello(): pass"
   tree = parser.parse(bytes(code, "utf8"))  # Not just code.encode()
   ```

2. **Verify language setup**:
   ```python
   from tree_sitter import Language, Parser
   import tree_sitter_python
   
   # Correct setup
   language = Language(tree_sitter_python.language())
   parser = Parser()
   parser.set_language(language)
   ```

3. **Check for parse errors**:
   ```python
   tree = parser.parse(bytes(code, "utf8"))
   
   def find_errors(node):
       if node.type == 'ERROR':
           print(f"Parse error at {node.start_point}: {node.text}")
       for child in node.children:
           find_errors(child)
   
   find_errors(tree.root_node)
   ```

### Memory and Performance Issues

**Problem**: pretty-sitter is slow or uses too much memory with large files.

**Solutions**:

1. **Filter to relevant nodes only**:
   ```python
   # Instead of printing entire tree
   ps = PrettySitter()
   ps.pprint(tree.root_node)
   
   # Filter to specific node types
   ps = PrettySitter(FilterConfig(only_types=['function_definition', 'class_definition']))
   ps.pprint(tree.root_node)
   ```

2. **Print subtrees instead of full tree**:
   ```python
   # Find and print specific subtrees
   def find_functions(node):
       if node.type == 'function_definition':
           ps.pprint(node)
       for child in node.children:
           find_functions(child)
   
   find_functions(tree.root_node)
   ```

3. **Disable expensive features**:
   ```python
   # Minimal configuration for performance
   ps = PrettySitter(
       UIConfig(
           with_text=False,      # Skip text content
           print_with_color=False,  # Skip color processing
           color_legend=False    # Skip legend generation
       )
   )
   ```

## Integration Issues

### Tree-tagger Integration Problems

**Problem**: Errors when using tree-tagger for semantic highlighting.

**Symptoms**:
- `ModuleNotFoundError: No module named 'tree_tagger'`
- Marking doesn't work as expected
- Performance issues with large files

**Solutions**:

1. **Install tree-tagger**:
   ```bash
   pip install git+https://github.com/antonioan/tree-tagger.git
   ```

2. **Handle optional dependency gracefully**:
   ```python
   from pretty_sitter import PrettySitter
   from pretty_sitter.config import FilterConfig, MarkingConfig
   
   extra_configs = []
   try:
       from tree_tagger import TreeTagger
       tree_tagger = TreeTagger(language, language_name)
       tags = tree_tagger.tag(root, find_usage_definitions=True)
       extra_configs.append(
           MarkingConfig(
               definition_nodes=tags.definition_nodes,
               usage_nodes=tags.defined_usage_nodes,
               undefined_usage_nodes=tags.undefined_usage_nodes,
           )
       )
   except ImportError:
       print("tree-tagger not available, skipping semantic highlighting")
   
   ps = PrettySitter(FilterConfig(only_types=["identifier"]))
   ps.pprint(root, *extra_configs)
   ```

### Custom Configuration Issues

**Problem**: Configuration not working as expected or conflicting settings.

**Solutions**:

1. **Understand configuration precedence**:
   ```python
   # Later configs override earlier ones
   ps = PrettySitter(
       UIConfig(with_text=True),    # This setting...
       UIConfig(with_text=False)    # ...is overridden by this
   )
   ```

2. **Use temporary configuration correctly**:
   ```python
   ps = PrettySitter(UIConfig(with_text=True))
   
   # Temporary override
   with ps.configure(UIConfig(with_text=False)):
       ps.pprint(node)  # Prints without text
   # Original configuration restored here
   ```

3. **Debug configuration issues**:
   ```python
   ps = PrettySitter(DebugConfig(debug=True))
   ps.pprint(node)  # Shows debug information about filtering decisions
   ```

## Getting Help

If you encounter issues not covered in this guide:

1. **Enable debug output** to understand what's happening:
   ```python
   from pretty_sitter.config import DebugConfig
   ps = PrettySitter(DebugConfig(debug=True))
   ```

2. **Check the FAQ** for additional common questions.

3. **Report bugs** following the guidelines in our bug reporting documentation.

4. **Provide minimal reproduction examples** when asking for help:
   ```python
   # Minimal example that demonstrates the issue
   from tree_sitter import Language, Parser
   import tree_sitter_python
   from pretty_sitter import PrettySitter
   
   language = Language(tree_sitter_python.language())
   parser = Parser()
   parser.set_language(language)
   tree = parser.parse(b"def test(): pass")
   
   ps = PrettySitter()
   ps.pprint(tree.root_node)  # Describe what goes wrong here
   ```