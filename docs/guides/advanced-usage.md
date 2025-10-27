# Advanced Usage Guide

This guide covers advanced pretty-sitter usage patterns, performance optimization techniques, and complex integration scenarios. It's designed for users who want to get the most out of pretty-sitter in sophisticated development workflows.

## Complex Filtering Strategies

### Hierarchical Filtering

When working with large codebases, you often need sophisticated filtering strategies that go beyond simple type inclusion/exclusion.

```python
from pretty_sitter import PrettySitter
from pretty_sitter.config import FilterConfig, UIConfig
from tree_sitter import Node

def create_hierarchical_filter(focus_types: list[str], context_types: list[str]) -> FilterConfig:
    """Create a filter that shows focus types with minimal context."""
    # This approach requires custom logic in your application
    # to identify which nodes provide necessary context
    return FilterConfig(
        only_types=focus_types + context_types,
        excluded_types=['comment', 'whitespace']
    )

# Example: Focus on functions but keep class context
config = create_hierarchical_filter(
    focus_types=['function_definition', 'method_definition'],
    context_types=['class_definition', 'identifier']
)

ps = PrettySitter(config)
```

### Dynamic Filtering Based on Node Properties

```python
def filter_by_complexity(tree: Node, max_children: int = 10) -> list[str]:
    """Generate exclusion list based on node complexity."""
    complex_types = set()
    
    def visit(node: Node):
        if len(node.children) > max_children:
            complex_types.add(node.type)
        for child in node.children:
            visit(child)
    
    visit(tree)
    return list(complex_types)

# Apply dynamic filtering
excluded = filter_by_complexity(tree.root_node, max_children=5)
config = FilterConfig(excluded_types=excluded)
ps = PrettySitter(config)
```

## Advanced Marking and Semantic Highlighting

### Multi-Level Semantic Analysis

```python
from pretty_sitter.config import MarkingConfig
from tree_sitter import Node

class SemanticAnalyzer:
    """Advanced semantic analysis for code highlighting."""
    
    def __init__(self, tree: Node):
        self.tree = tree
        self.definitions = []
        self.usages = []
        self.undefined_usages = []
        self.symbol_table = {}
    
    def analyze(self) -> MarkingConfig:
        """Perform semantic analysis and return marking configuration."""
        self._build_symbol_table()
        self._classify_usages()
        
        return MarkingConfig(
            definition_nodes=self.definitions,
            usage_nodes=self.usages,
            undefined_usage_nodes=self.undefined_usages,
            marks=[
                ('Exported', 'cyan', self._find_exports()),
                ('Imported', 'blue', self._find_imports()),
                ('Deprecated', 'yellow', self._find_deprecated())
            ]
        )
    
    def _build_symbol_table(self):
        """Build symbol table from definitions."""
        def visit(node: Node):
            if node.type in ['function_definition', 'class_definition', 'variable_declaration']:
                name_node = self._get_name_node(node)
                if name_node:
                    self.symbol_table[name_node.text.decode()] = node
                    self.definitions.append(name_node)
            
            for child in node.children:
                visit(child)
        
        visit(self.tree)
    
    def _classify_usages(self):
        """Classify identifier usages as defined or undefined."""
        def visit(node: Node):
            if node.type == 'identifier' and node not in self.definitions:
                name = node.text.decode()
                if name in self.symbol_table:
                    self.usages.append(node)
                else:
                    self.undefined_usages.append(node)
            
            for child in node.children:
                visit(child)
        
        visit(self.tree)
    
    def _get_name_node(self, node: Node) -> Node | None:
        """Extract name node from definition."""
        # Implementation depends on language grammar
        for child in node.children:
            if child.type == 'identifier':
                return child
        return None
    
    def _find_exports(self) -> list[Node]:
        """Find exported symbols."""
        exports = []
        def visit(node: Node):
            if node.type in ['export_statement', 'public_declaration']:
                exports.extend(self._get_identifiers(node))
            for child in node.children:
                visit(child)
        visit(self.tree)
        return exports
    
    def _find_imports(self) -> list[Node]:
        """Find imported symbols."""
        imports = []
        def visit(node: Node):
            if node.type in ['import_statement', 'import_declaration']:
                imports.extend(self._get_identifiers(node))
            for child in node.children:
                visit(child)
        visit(self.tree)
        return imports
    
    def _find_deprecated(self) -> list[Node]:
        """Find deprecated symbols (example: based on comments)."""
        # Implementation would analyze comments or decorators
        return []
    
    def _get_identifiers(self, node: Node) -> list[Node]:
        """Extract all identifiers from a node."""
        identifiers = []
        def visit(n: Node):
            if n.type == 'identifier':
                identifiers.append(n)
            for child in n.children:
                visit(child)
        visit(node)
        return identifiers

# Usage
analyzer = SemanticAnalyzer(tree.root_node)
semantic_config = analyzer.analyze()
ps = PrettySitter(semantic_config)
```

### Cross-Reference Highlighting

```python
def create_cross_reference_config(symbol_name: str, tree: Node) -> MarkingConfig:
    """Highlight all occurrences of a specific symbol."""
    references = []
    
    def find_references(node: Node):
        if node.type == 'identifier' and node.text.decode() == symbol_name:
            references.append(node)
        for child in node.children:
            find_references(child)
    
    find_references(tree)
    
    return MarkingConfig(marks=[
        (f'References to "{symbol_name}"', 'cyan', references)
    ])

# Highlight all occurrences of 'main' function
config = create_cross_reference_config('main', tree.root_node)
ps = PrettySitter(config)
```

## Performance Optimization

### Lazy Loading and Streaming

For very large parse trees, consider implementing lazy loading:

```python
class LazyPrettySitter:
    """Pretty printer with lazy loading for large trees."""
    
    def __init__(self, *configs):
        self.ps = PrettySitter(*configs)
        self.node_cache = {}
    
    def pprint_subtree(self, node: Node, max_depth: int = 5):
        """Print only a subtree up to specified depth."""
        with self.ps.configure(UIConfig()):
            self._print_limited_depth(node, max_depth)
    
    def _print_limited_depth(self, node: Node, max_depth: int, current_depth: int = 0):
        """Internal method to limit tree depth."""
        if current_depth >= max_depth:
            print(f"{'  ' * current_depth}... (truncated at depth {max_depth})")
            return
        
        # Use normal pretty printing for this level
        self.ps.pprint(node)

# Usage for large files
lazy_ps = LazyPrettySitter(UIConfig(indent_size=2))
lazy_ps.pprint_subtree(large_tree.root_node, max_depth=3)
```

### Memory-Efficient Configuration

```python
def create_memory_efficient_config() -> list:
    """Create configuration optimized for memory usage."""
    return [
        UIConfig(
            with_text=False,        # Reduces string processing
            print_with_color=False, # Avoids color code generation
            color_legend=False,     # Skips legend generation
            column_width=50         # Smaller column width
        ),
        FilterConfig(
            excluded_types=[        # Filter out memory-heavy nodes
                'comment', 'whitespace', 'newline',
                'string_literal', 'raw_string'
            ]
        )
    ]

# Apply memory-efficient configuration
config = create_memory_efficient_config()
ps = PrettySitter(*config)
```

### Batch Processing

```python
class BatchProcessor:
    """Process multiple files efficiently."""
    
    def __init__(self, *configs):
        self.ps = PrettySitter(*configs)
        self.results = []
    
    def process_files(self, file_paths: list[str], parser) -> dict:
        """Process multiple files and collect results."""
        results = {}
        
        for file_path in file_paths:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                tree = parser.parse(content)
                
                # Capture output instead of printing
                output = self._capture_output(tree.root_node)
                results[file_path] = output
                
            except Exception as e:
                results[file_path] = f"Error: {e}"
        
        return results
    
    def _capture_output(self, node: Node) -> str:
        """Capture pretty-sitter output as string."""
        import io
        import sys
        from contextlib import redirect_stdout
        
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            self.ps.pprint(node)
        
        return output_buffer.getvalue()

# Usage
processor = BatchProcessor(
    UIConfig(print_with_color=False),
    FilterConfig(only_types=['function_definition'])
)

results = processor.process_files(['file1.py', 'file2.py'], python_parser)
```

## Integration Patterns

### IDE Integration

```python
class IDEIntegration:
    """Integration helper for IDE plugins."""
    
    def __init__(self):
        self.ps = PrettySitter()
    
    def get_node_at_position(self, tree: Node, line: int, column: int) -> Node | None:
        """Find the node at a specific cursor position."""
        def find_node(node: Node) -> Node | None:
            start_line, start_col = node.start_point
            end_line, end_col = node.end_point
            
            if (start_line <= line <= end_line and
                (line > start_line or start_col <= column) and
                (line < end_line or column <= end_col)):
                
                # Check children for more specific match
                for child in node.children:
                    child_result = find_node(child)
                    if child_result:
                        return child_result
                
                return node
            
            return None
        
        return find_node(tree)
    
    def get_context_tree(self, tree: Node, target_node: Node, context_levels: int = 2) -> str:
        """Get pretty-printed context around a target node."""
        # Find parent at specified level
        current = target_node
        for _ in range(context_levels):
            if current.parent:
                current = current.parent
        
        # Configure for context display
        config = [
            UIConfig(column_width=60, indent_size=2),
            MarkingConfig(marks=[('Target', 'red', [target_node])])
        ]
        
        with self.ps.configure(*config):
            import io
            import sys
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                self.ps.pprint(current)
            
            return output_buffer.getvalue()

# Usage in IDE plugin
ide = IDEIntegration()
cursor_node = ide.get_node_at_position(tree.root_node, line=10, column=5)
if cursor_node:
    context = ide.get_context_tree(tree.root_node, cursor_node)
    print(context)
```

### CI/CD Integration

```python
class CIIntegration:
    """Integration for continuous integration pipelines."""
    
    def __init__(self):
        self.config = [
            UIConfig(
                print_with_color=False,  # No colors in CI logs
                color_legend=False,
                column_width=120
            ),
            FilterConfig(
                excluded_types=['comment', 'whitespace']
            )
        ]
        self.ps = PrettySitter(*self.config)
    
    def analyze_diff(self, old_tree: Node, new_tree: Node) -> dict:
        """Analyze differences between two parse trees."""
        old_functions = self._extract_functions(old_tree)
        new_functions = self._extract_functions(new_tree)
        
        added = set(new_functions.keys()) - set(old_functions.keys())
        removed = set(old_functions.keys()) - set(new_functions.keys())
        modified = set()
        
        for name in set(old_functions.keys()) & set(new_functions.keys()):
            if self._function_changed(old_functions[name], new_functions[name]):
                modified.add(name)
        
        return {
            'added': list(added),
            'removed': list(removed),
            'modified': list(modified)
        }
    
    def _extract_functions(self, tree: Node) -> dict[str, Node]:
        """Extract all function definitions from tree."""
        functions = {}
        
        def visit(node: Node):
            if node.type == 'function_definition':
                name_node = self._get_function_name(node)
                if name_node:
                    functions[name_node.text.decode()] = node
            
            for child in node.children:
                visit(child)
        
        visit(tree)
        return functions
    
    def _get_function_name(self, func_node: Node) -> Node | None:
        """Extract function name from function definition."""
        for child in func_node.children:
            if child.type == 'identifier':
                return child
        return None
    
    def _function_changed(self, old_func: Node, new_func: Node) -> bool:
        """Check if function implementation changed."""
        # Simple comparison based on text content
        return old_func.text != new_func.text
    
    def generate_report(self, tree: Node, output_file: str):
        """Generate analysis report for CI."""
        with open(output_file, 'w') as f:
            f.write("# Parse Tree Analysis Report\n\n")
            
            # Capture pretty-sitter output
            import io
            import sys
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                self.ps.pprint(tree)
            
            f.write("## Tree Structure\n\n")
            f.write("```\n")
            f.write(output_buffer.getvalue())
            f.write("```\n")

# Usage in CI pipeline
ci = CIIntegration()
ci.generate_report(tree.root_node, 'analysis_report.md')
```

### Testing Framework Integration

```python
class TestingIntegration:
    """Integration with testing frameworks."""
    
    def __init__(self):
        self.debug_config = [
            UIConfig(with_text=True, column_width=80),
            DebugConfig(debug=True),
            TTYConfig(use_pager=False)  # No pager in tests
        ]
        self.ps = PrettySitter()
    
    def assert_tree_structure(self, tree: Node, expected_types: list[str]):
        """Assert that tree contains expected node types."""
        actual_types = self._collect_types(tree)
        
        for expected_type in expected_types:
            if expected_type not in actual_types:
                # Print debug info on failure
                with self.ps.configure(*self.debug_config):
                    print(f"\nExpected type '{expected_type}' not found in tree:")
                    self.ps.pprint(tree)
                
                raise AssertionError(f"Expected node type '{expected_type}' not found")
    
    def _collect_types(self, tree: Node) -> set[str]:
        """Collect all node types in tree."""
        types = set()
        
        def visit(node: Node):
            types.add(node.type)
            for child in node.children:
                visit(child)
        
        visit(tree)
        return types
    
    def debug_test_failure(self, tree: Node, test_name: str):
        """Generate debug output for test failures."""
        print(f"\n=== DEBUG INFO FOR FAILED TEST: {test_name} ===")
        
        with self.ps.configure(*self.debug_config):
            self.ps.pprint(tree)
        
        print("=== END DEBUG INFO ===\n")

# Usage in tests
def test_function_parsing():
    testing = TestingIntegration()
    
    # Parse test code
    tree = parser.parse(b'def test_func(): pass')
    
    try:
        testing.assert_tree_structure(tree.root_node, ['function_definition', 'identifier'])
    except AssertionError:
        testing.debug_test_failure(tree.root_node, 'test_function_parsing')
        raise
```

## Custom Extensions

### Custom Color Schemes

```python
from pretty_sitter.colorer import Colorer

class CustomColorer(Colorer):
    """Extended colorer with custom color schemes."""
    
    COLOR_MAP = {
        **Colorer.COLOR_MAP,
        'orange': 208,
        'purple': 135,
        'pink': 213,
        'lime': 154
    }
    
    def __init__(self, theme: str = 'default', **kwargs):
        super().__init__(**kwargs)
        self.theme = theme
    
    def apply_theme(self, text: str, node_type: str) -> str:
        """Apply theme-based coloring."""
        if self.theme == 'dark':
            return self._dark_theme_color(text, node_type)
        elif self.theme == 'light':
            return self._light_theme_color(text, node_type)
        else:
            return text
    
    def _dark_theme_color(self, text: str, node_type: str) -> str:
        """Dark theme color mapping."""
        color_map = {
            'function_definition': 'cyan',
            'class_definition': 'green2',
            'identifier': 'yellow',
            'string': 'orange',
            'number': 'purple'
        }
        color = color_map.get(node_type, 'gray')
        return self[color](text)
    
    def _light_theme_color(self, text: str, node_type: str) -> str:
        """Light theme color mapping."""
        color_map = {
            'function_definition': 'blue',
            'class_definition': 'green',
            'identifier': 'red',
            'string': 'purple',
            'number': 'cyan'
        }
        color = color_map.get(node_type, 'gray')
        return self[color](text)

# Usage with custom colorer
# Note: This would require modifying PrettySitter to accept custom colorers
```

### Plugin System

```python
class PrettySitterPlugin:
    """Base class for pretty-sitter plugins."""
    
    def pre_process(self, tree: Node) -> Node:
        """Process tree before pretty printing."""
        return tree
    
    def post_process(self, output: str) -> str:
        """Process output after pretty printing."""
        return output
    
    def get_config(self) -> list:
        """Return plugin-specific configuration."""
        return []

class StatisticsPlugin(PrettySitterPlugin):
    """Plugin that adds statistics to output."""
    
    def __init__(self):
        self.stats = {}
    
    def pre_process(self, tree: Node) -> Node:
        """Collect statistics during preprocessing."""
        self.stats = self._collect_stats(tree)
        return tree
    
    def post_process(self, output: str) -> str:
        """Add statistics to output."""
        stats_text = self._format_stats()
        return f"{stats_text}\n\n{output}"
    
    def _collect_stats(self, tree: Node) -> dict:
        """Collect tree statistics."""
        stats = {'total_nodes': 0, 'node_types': {}, 'max_depth': 0}
        
        def visit(node: Node, depth: int = 0):
            stats['total_nodes'] += 1
            stats['max_depth'] = max(stats['max_depth'], depth)
            
            if node.type not in stats['node_types']:
                stats['node_types'][node.type] = 0
            stats['node_types'][node.type] += 1
            
            for child in node.children:
                visit(child, depth + 1)
        
        visit(tree)
        return stats
    
    def _format_stats(self) -> str:
        """Format statistics for display."""
        lines = ["=== Tree Statistics ==="]
        lines.append(f"Total nodes: {self.stats['total_nodes']}")
        lines.append(f"Max depth: {self.stats['max_depth']}")
        lines.append(f"Node types: {len(self.stats['node_types'])}")
        
        # Top 5 most common types
        sorted_types = sorted(
            self.stats['node_types'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        lines.append("Most common types:")
        for node_type, count in sorted_types:
            lines.append(f"  {node_type}: {count}")
        
        return "\n".join(lines)

# Usage with plugins
plugin = StatisticsPlugin()
tree_processed = plugin.pre_process(tree.root_node)

# Normal pretty printing
ps = PrettySitter(*plugin.get_config())
# ... capture output ...
final_output = plugin.post_process(captured_output)
print(final_output)
```

## Best Practices for Advanced Usage

### Performance Guidelines

1. **Profile First**: Use Python's profiling tools to identify bottlenecks
2. **Filter Early**: Apply filtering as early as possible to reduce processing
3. **Cache Results**: Cache expensive operations like semantic analysis
4. **Batch Operations**: Process multiple files together when possible
5. **Memory Management**: Use generators for large datasets

### Error Handling

```python
class RobustPrettySitter:
    """Pretty printer with comprehensive error handling."""
    
    def __init__(self, *configs):
        self.ps = PrettySitter(*configs)
        self.error_log = []
    
    def safe_pprint(self, node: Node, fallback_config=None) -> bool:
        """Pretty print with error recovery."""
        try:
            self.ps.pprint(node)
            return True
        except Exception as e:
            self.error_log.append(f"Error printing node {node.type}: {e}")
            
            if fallback_config:
                try:
                    with self.ps.configure(*fallback_config):
                        self.ps.pprint(node)
                    return True
                except Exception as fallback_error:
                    self.error_log.append(f"Fallback failed: {fallback_error}")
            
            return False
    
    def get_errors(self) -> list[str]:
        """Get accumulated errors."""
        return self.error_log.copy()

# Usage with error handling
robust_ps = RobustPrettySitter(UIConfig(with_text=True))
fallback = [UIConfig(with_text=False, print_with_color=False)]

success = robust_ps.safe_pprint(tree.root_node, fallback_config=fallback)
if not success:
    print("Errors occurred:", robust_ps.get_errors())
```

### Testing Advanced Configurations

```python
import unittest
from pretty_sitter import PrettySitter
from pretty_sitter.config import UIConfig, FilterConfig, MarkingConfig

class TestAdvancedConfigurations(unittest.TestCase):
    """Test suite for advanced pretty-sitter configurations."""
    
    def setUp(self):
        # Set up test tree and nodes
        self.tree = self._create_test_tree()
        self.test_nodes = self._get_test_nodes()
    
    def test_complex_filtering(self):
        """Test complex filtering scenarios."""
        config = FilterConfig(
            only_types=['function_definition', 'identifier'],
            excluded_types=['comment']
        )
        
        ps = PrettySitter(config)
        # Test that output contains expected elements
        output = self._capture_output(ps, self.tree.root_node)
        
        self.assertIn('function_definition', output)
        self.assertNotIn('comment', output)
    
    def test_semantic_marking(self):
        """Test semantic marking functionality."""
        config = MarkingConfig(
            definition_nodes=[self.test_nodes['definition']],
            usage_nodes=[self.test_nodes['usage']]
        )
        
        ps = PrettySitter(config)
        output = self._capture_output(ps, self.tree.root_node)
        
        # Verify color legend appears
        self.assertIn('Definitions', output)
        self.assertIn('Usages', output)
    
    def _create_test_tree(self):
        """Create a test parse tree."""
        # Implementation depends on your test setup
        pass
    
    def _get_test_nodes(self):
        """Get specific nodes for testing."""
        # Implementation depends on your test setup
        pass
    
    def _capture_output(self, ps: PrettySitter, node: Node) -> str:
        """Capture pretty-sitter output as string."""
        import io
        import sys
        from contextlib import redirect_stdout
        
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            ps.pprint(node)
        
        return output_buffer.getvalue()

if __name__ == '__main__':
    unittest.main()
```

This advanced usage guide provides comprehensive coverage of sophisticated pretty-sitter usage patterns. These techniques enable you to build powerful code analysis tools, integrate pretty-sitter into complex workflows, and customize the output for specific use cases.