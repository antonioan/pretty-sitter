# Integration Examples

This guide demonstrates how to integrate pretty-sitter with various tools and frameworks, with a focus on tree-tagger integration for semantic highlighting and advanced marking features.

## Tree-Tagger Integration

Tree-tagger is a powerful tool for semantic analysis of code. When combined with pretty-sitter, it enables sophisticated highlighting of definitions, usages, and semantic relationships.

### Basic Tree-Tagger Setup

```python
from pretty_sitter import PrettySitter
from pretty_sitter.config import MarkingConfig
from tree_sitter import Language, Parser, Node
import tree_tagger  # Hypothetical tree-tagger library

class TreeTaggerIntegration:
    """Integration between pretty-sitter and tree-tagger."""
    
    def __init__(self, language_path: str, language_name: str):
        # Set up tree-sitter parser
        self.language = Language(language_path, language_name)
        self.parser = Parser()
        self.parser.set_language(self.language)
        
        # Initialize tree-tagger
        self.tagger = tree_tagger.TreeTagger(language_name)
        
        # Initialize pretty-sitter
        self.ps = PrettySitter()
    
    def analyze_and_print(self, source_code: str):
        """Analyze code with tree-tagger and pretty-print with semantic highlighting."""
        # Parse with tree-sitter
        tree = self.parser.parse(source_code.encode())
        
        # Analyze with tree-tagger
        semantic_info = self.tagger.analyze(tree)
        
        # Create marking configuration from semantic analysis
        marking_config = self._create_marking_config(semantic_info)
        
        # Pretty-print with semantic highlighting
        with self.ps.configure(marking_config):
            self.ps.pprint(tree.root_node)
    
    def _create_marking_config(self, semantic_info) -> MarkingConfig:
        """Convert tree-tagger results to pretty-sitter marking configuration."""
        return MarkingConfig(
            definition_nodes=semantic_info.definitions,
            usage_nodes=semantic_info.usages,
            undefined_usage_nodes=semantic_info.undefined_usages,
            marks=[
                ('Exported Symbols', 'cyan', semantic_info.exports),
                ('Imported Symbols', 'blue', semantic_info.imports),
                ('Type Annotations', 'yellow', semantic_info.type_annotations)
            ]
        )

# Usage example
integration = TreeTaggerIntegration('/path/to/python.so', 'python')
integration.analyze_and_print('''
def fibonacci(n: int) -> int:
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(result)
''')
```

### Advanced Semantic Analysis

```python
class AdvancedSemanticAnalyzer:
    """Advanced semantic analysis combining tree-sitter and tree-tagger."""
    
    def __init__(self, parser: Parser, tagger):
        self.parser = parser
        self.tagger = tagger
        self.symbol_table = {}
        self.call_graph = {}
        self.type_info = {}
    
    def full_analysis(self, source_code: str) -> dict:
        """Perform comprehensive semantic analysis."""
        tree = self.parser.parse(source_code.encode())
        
        # Build symbol table
        self._build_symbol_table(tree.root_node)
        
        # Analyze with tree-tagger
        tagger_results = self.tagger.analyze(tree)
        
        # Build call graph
        self._build_call_graph(tree.root_node)
        
        # Extract type information
        self._extract_type_info(tree.root_node, tagger_results)
        
        return {
            'tree': tree,
            'symbols': self.symbol_table,
            'calls': self.call_graph,
            'types': self.type_info,
            'tagger_results': tagger_results
        }
    
    def create_comprehensive_marking(self, analysis: dict) -> MarkingConfig:
        """Create comprehensive marking from analysis results."""
        marks = []
        
        # Function definitions and calls
        func_defs = [node for node, info in analysis['symbols'].items() 
                    if info['type'] == 'function_definition']
        func_calls = [node for node, info in analysis['calls'].items()]
        
        marks.extend([
            ('Function Definitions', 'green2', func_defs),
            ('Function Calls', 'cyan', func_calls),
            ('Class Definitions', 'blue', 
             [node for node, info in analysis['symbols'].items() 
              if info['type'] == 'class_definition']),
            ('Variable Definitions', 'yellow',
             [node for node, info in analysis['symbols'].items() 
              if info['type'] == 'variable_definition'])
        ])
        
        # Type annotations
        type_nodes = [node for node, type_info in analysis['types'].items()]
        if type_nodes:
            marks.append(('Type Annotations', 'purple', type_nodes))
        
        # Tree-tagger specific results
        tagger = analysis['tagger_results']
        return MarkingConfig(
            marks=marks,
            definition_nodes=tagger.definitions,
            usage_nodes=tagger.usages,
            undefined_usage_nodes=tagger.undefined_usages
        )
    
    def _build_symbol_table(self, node: Node):
        """Build comprehensive symbol table."""
        def visit(node: Node):
            if node.type in ['function_definition', 'class_definition', 'variable_declaration']:
                name_node = self._extract_name(node)
                if name_node:
                    self.symbol_table[name_node] = {
                        'type': node.type,
                        'scope': self._get_scope(node),
                        'line': node.start_point[0],
                        'definition_node': node
                    }
            
            for child in node.children:
                visit(child)
        
        visit(node)
    
    def _build_call_graph(self, node: Node):
        """Build function call graph."""
        def visit(node: Node, current_function=None):
            if node.type == 'function_definition':
                func_name = self._extract_name(node)
                current_function = func_name.text.decode() if func_name else None
                if current_function:
                    self.call_graph[current_function] = []
            
            elif node.type == 'call_expression' and current_function:
                called_func = self._extract_called_function(node)
                if called_func:
                    self.call_graph[current_function].append({
                        'name': called_func,
                        'node': node,
                        'line': node.start_point[0]
                    })
            
            for child in node.children:
                visit(child, current_function)
        
        visit(node)
    
    def _extract_type_info(self, node: Node, tagger_results):
        """Extract type information from nodes."""
        def visit(node: Node):
            if node.type == 'type_annotation':
                self.type_info[node] = {
                    'annotation': node.text.decode(),
                    'line': node.start_point[0]
                }
            
            # Use tagger results for additional type info
            if hasattr(tagger_results, 'type_info'):
                for typed_node, type_data in tagger_results.type_info.items():
                    self.type_info[typed_node] = type_data
            
            for child in node.children:
                visit(child)
        
        visit(node)
    
    def _extract_name(self, node: Node) -> Node | None:
        """Extract name node from definition."""
        for child in node.children:
            if child.type == 'identifier':
                return child
        return None
    
    def _extract_called_function(self, call_node: Node) -> str | None:
        """Extract function name from call expression."""
        for child in call_node.children:
            if child.type == 'identifier':
                return child.text.decode()
        return None
    
    def _get_scope(self, node: Node) -> str:
        """Determine the scope of a node."""
        parent = node.parent
        scope_parts = []
        
        while parent:
            if parent.type in ['class_definition', 'function_definition']:
                name_node = self._extract_name(parent)
                if name_node:
                    scope_parts.append(name_node.text.decode())
            parent = parent.parent
        
        return '.'.join(reversed(scope_parts)) if scope_parts else 'global'

# Usage example
analyzer = AdvancedSemanticAnalyzer(parser, tagger)
analysis = analyzer.full_analysis(source_code)
marking_config = analyzer.create_comprehensive_marking(analysis)

ps = PrettySitter(marking_config)
ps.pprint(analysis['tree'].root_node)
```

### Cross-Reference Analysis

```python
class CrossReferenceAnalyzer:
    """Analyze cross-references between symbols using tree-tagger."""
    
    def __init__(self, parser: Parser, tagger):
        self.parser = parser
        self.tagger = tagger
    
    def analyze_references(self, source_code: str, target_symbol: str) -> dict:
        """Analyze all references to a specific symbol."""
        tree = self.parser.parse(source_code.encode())
        tagger_results = self.tagger.analyze(tree)
        
        # Find all occurrences of the target symbol
        references = self._find_symbol_references(tree.root_node, target_symbol)
        
        # Classify references using tree-tagger data
        classified = self._classify_references(references, tagger_results)
        
        return {
            'tree': tree,
            'target_symbol': target_symbol,
            'total_references': len(references),
            'definitions': classified['definitions'],
            'usages': classified['usages'],
            'modifications': classified['modifications'],
            'calls': classified['calls']
        }
    
    def create_reference_marking(self, analysis: dict) -> MarkingConfig:
        """Create marking configuration for cross-reference visualization."""
        return MarkingConfig(marks=[
            (f'Definitions of "{analysis["target_symbol"]}"', 'red', analysis['definitions']),
            (f'Usages of "{analysis["target_symbol"]}"', 'green2', analysis['usages']),
            (f'Modifications of "{analysis["target_symbol"]}"', 'yellow', analysis['modifications']),
            (f'Calls to "{analysis["target_symbol"]}"', 'cyan', analysis['calls'])
        ])
    
    def _find_symbol_references(self, node: Node, symbol: str) -> list[Node]:
        """Find all nodes that reference the target symbol."""
        references = []
        
        def visit(node: Node):
            if (node.type == 'identifier' and 
                node.text.decode() == symbol):
                references.append(node)
            
            for child in node.children:
                visit(child)
        
        visit(node)
        return references
    
    def _classify_references(self, references: list[Node], tagger_results) -> dict:
        """Classify references by their semantic role."""
        classified = {
            'definitions': [],
            'usages': [],
            'modifications': [],
            'calls': []
        }
        
        for ref in references:
            # Use tree-tagger results to classify
            if ref in tagger_results.definitions:
                classified['definitions'].append(ref)
            elif self._is_modification(ref):
                classified['modifications'].append(ref)
            elif self._is_function_call(ref):
                classified['calls'].append(ref)
            else:
                classified['usages'].append(ref)
        
        return classified
    
    def _is_modification(self, node: Node) -> bool:
        """Check if node represents a modification (assignment)."""
        parent = node.parent
        while parent:
            if parent.type in ['assignment_expression', 'augmented_assignment']:
                # Check if this identifier is on the left side
                if parent.children and parent.children[0] == node:
                    return True
            parent = parent.parent
        return False
    
    def _is_function_call(self, node: Node) -> bool:
        """Check if node represents a function call."""
        parent = node.parent
        return parent and parent.type == 'call_expression'

# Usage example
ref_analyzer = CrossReferenceAnalyzer(parser, tagger)
ref_analysis = ref_analyzer.analyze_references(source_code, 'fibonacci')
ref_marking = ref_analyzer.create_reference_marking(ref_analysis)

ps = PrettySitter(ref_marking)
ps.pprint(ref_analysis['tree'].root_node)
```

## Language Server Protocol (LSP) Integration

```python
import json
from typing import Dict, List, Optional

class LSPIntegration:
    """Integration with Language Server Protocol for enhanced semantic information."""
    
    def __init__(self, parser: Parser, lsp_client):
        self.parser = parser
        self.lsp_client = lsp_client
        self.ps = PrettySitter()
    
    def analyze_with_lsp(self, file_path: str, source_code: str) -> dict:
        """Analyze code using LSP server for semantic information."""
        # Parse with tree-sitter
        tree = self.parser.parse(source_code.encode())
        
        # Get semantic information from LSP
        lsp_info = self._get_lsp_semantic_info(file_path, source_code)
        
        # Combine tree-sitter and LSP information
        combined_analysis = self._combine_analysis(tree, lsp_info)
        
        return combined_analysis
    
    def create_lsp_marking(self, analysis: dict) -> MarkingConfig:
        """Create marking configuration from LSP analysis."""
        marks = []
        
        # LSP semantic tokens
        if 'semantic_tokens' in analysis:
            for token_type, nodes in analysis['semantic_tokens'].items():
                color = self._get_color_for_token_type(token_type)
                marks.append((token_type.title(), color, nodes))
        
        # LSP diagnostics (errors, warnings)
        if 'diagnostics' in analysis:
            error_nodes = [d['node'] for d in analysis['diagnostics'] if d['severity'] == 'error']
            warning_nodes = [d['node'] for d in analysis['diagnostics'] if d['severity'] == 'warning']
            
            if error_nodes:
                marks.append(('Errors', 'red', error_nodes))
            if warning_nodes:
                marks.append(('Warnings', 'yellow', warning_nodes))
        
        # LSP references
        if 'references' in analysis:
            marks.append(('References', 'cyan', analysis['references']))
        
        return MarkingConfig(marks=marks)
    
    def _get_lsp_semantic_info(self, file_path: str, source_code: str) -> dict:
        """Get semantic information from LSP server."""
        # Open document in LSP
        self.lsp_client.did_open(file_path, source_code)
        
        # Get semantic tokens
        semantic_tokens = self.lsp_client.semantic_tokens_full(file_path)
        
        # Get diagnostics
        diagnostics = self.lsp_client.get_diagnostics(file_path)
        
        # Get document symbols
        symbols = self.lsp_client.document_symbols(file_path)
        
        return {
            'semantic_tokens': semantic_tokens,
            'diagnostics': diagnostics,
            'symbols': symbols
        }
    
    def _combine_analysis(self, tree: Node, lsp_info: dict) -> dict:
        """Combine tree-sitter parse tree with LSP semantic information."""
        # Map LSP positions to tree-sitter nodes
        semantic_tokens = {}
        diagnostics = []
        references = []
        
        # Process semantic tokens
        if lsp_info.get('semantic_tokens'):
            semantic_tokens = self._map_semantic_tokens(tree, lsp_info['semantic_tokens'])
        
        # Process diagnostics
        if lsp_info.get('diagnostics'):
            diagnostics = self._map_diagnostics(tree, lsp_info['diagnostics'])
        
        return {
            'tree': tree,
            'semantic_tokens': semantic_tokens,
            'diagnostics': diagnostics,
            'references': references
        }
    
    def _map_semantic_tokens(self, tree: Node, tokens: list) -> dict:
        """Map LSP semantic tokens to tree-sitter nodes."""
        token_map = {}
        
        for token in tokens:
            # Find tree-sitter node at token position
            node = self._find_node_at_position(
                tree, token['line'], token['character']
            )
            
            if node:
                token_type = token['type']
                if token_type not in token_map:
                    token_map[token_type] = []
                token_map[token_type].append(node)
        
        return token_map
    
    def _map_diagnostics(self, tree: Node, diagnostics: list) -> list:
        """Map LSP diagnostics to tree-sitter nodes."""
        mapped_diagnostics = []
        
        for diagnostic in diagnostics:
            node = self._find_node_at_position(
                tree, diagnostic['range']['start']['line'],
                diagnostic['range']['start']['character']
            )
            
            if node:
                mapped_diagnostics.append({
                    'node': node,
                    'message': diagnostic['message'],
                    'severity': diagnostic.get('severity', 'info'),
                    'source': diagnostic.get('source', 'lsp')
                })
        
        return mapped_diagnostics
    
    def _find_node_at_position(self, tree: Node, line: int, character: int) -> Optional[Node]:
        """Find the tree-sitter node at a specific position."""
        def find_node(node: Node) -> Optional[Node]:
            start_line, start_col = node.start_point
            end_line, end_col = node.end_point
            
            if (start_line <= line <= end_line and
                (line > start_line or start_col <= character) and
                (line < end_line or character <= end_col)):
                
                # Check children for more specific match
                for child in node.children:
                    child_result = find_node(child)
                    if child_result:
                        return child_result
                
                return node
            
            return None
        
        return find_node(tree)
    
    def _get_color_for_token_type(self, token_type: str) -> str:
        """Map LSP semantic token types to colors."""
        color_map = {
            'namespace': 'blue',
            'class': 'green2',
            'enum': 'green',
            'interface': 'cyan',
            'struct': 'green',
            'typeParameter': 'yellow',
            'type': 'blue',
            'parameter': 'gray',
            'variable': 'gray',
            'property': 'cyan',
            'enumMember': 'cyan',
            'event': 'yellow',
            'function': 'green2',
            'method': 'green2',
            'macro': 'red',
            'keyword': 'blue',
            'modifier': 'blue',
            'comment': 'gray',
            'string': 'yellow',
            'number': 'cyan',
            'regexp': 'red',
            'operator': 'gray'
        }
        return color_map.get(token_type, 'gray')

# Usage example
lsp_integration = LSPIntegration(parser, lsp_client)
lsp_analysis = lsp_integration.analyze_with_lsp('example.py', source_code)
lsp_marking = lsp_integration.create_lsp_marking(lsp_analysis)

ps = PrettySitter(lsp_marking)
ps.pprint(lsp_analysis['tree'].root_node)
```

## Static Analysis Tool Integration

```python
class StaticAnalysisIntegration:
    """Integration with static analysis tools like pylint, mypy, etc."""
    
    def __init__(self, parser: Parser):
        self.parser = parser
        self.ps = PrettySitter()
    
    def analyze_with_pylint(self, file_path: str, source_code: str) -> dict:
        """Analyze code with pylint and create visual representation."""
        import subprocess
        import json
        import tempfile
        import os
        
        # Parse with tree-sitter
        tree = self.parser.parse(source_code.encode())
        
        # Run pylint analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            # Run pylint with JSON output
            result = subprocess.run([
                'pylint', '--output-format=json', temp_file
            ], capture_output=True, text=True)
            
            pylint_issues = json.loads(result.stdout) if result.stdout else []
            
        finally:
            os.unlink(temp_file)
        
        # Map pylint issues to tree nodes
        mapped_issues = self._map_pylint_issues(tree, pylint_issues)
        
        return {
            'tree': tree,
            'pylint_issues': mapped_issues,
            'source_code': source_code
        }
    
    def create_pylint_marking(self, analysis: dict) -> MarkingConfig:
        """Create marking configuration from pylint analysis."""
        marks = []
        
        # Group issues by type
        issue_groups = {}
        for issue in analysis['pylint_issues']:
            issue_type = issue['type']
            if issue_type not in issue_groups:
                issue_groups[issue_type] = []
            issue_groups[issue_type].append(issue['node'])
        
        # Create marks for each issue type
        color_map = {
            'error': 'red',
            'warning': 'yellow',
            'refactor': 'blue',
            'convention': 'cyan',
            'info': 'gray'
        }
        
        for issue_type, nodes in issue_groups.items():
            color = color_map.get(issue_type, 'gray')
            marks.append((f'Pylint {issue_type.title()}', color, nodes))
        
        return MarkingConfig(marks=marks)
    
    def analyze_with_mypy(self, file_path: str, source_code: str) -> dict:
        """Analyze code with mypy for type checking."""
        import subprocess
        import tempfile
        import os
        import re
        
        tree = self.parser.parse(source_code.encode())
        
        # Run mypy analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            result = subprocess.run([
                'mypy', '--show-error-codes', '--no-error-summary', temp_file
            ], capture_output=True, text=True)
            
            mypy_output = result.stdout
            
        finally:
            os.unlink(temp_file)
        
        # Parse mypy output
        mypy_issues = self._parse_mypy_output(mypy_output, tree)
        
        return {
            'tree': tree,
            'mypy_issues': mypy_issues,
            'source_code': source_code
        }
    
    def create_mypy_marking(self, analysis: dict) -> MarkingConfig:
        """Create marking configuration from mypy analysis."""
        marks = []
        
        # Group by error type
        error_nodes = []
        warning_nodes = []
        note_nodes = []
        
        for issue in analysis['mypy_issues']:
            if issue['severity'] == 'error':
                error_nodes.append(issue['node'])
            elif issue['severity'] == 'warning':
                warning_nodes.append(issue['node'])
            else:
                note_nodes.append(issue['node'])
        
        if error_nodes:
            marks.append(('MyPy Errors', 'red', error_nodes))
        if warning_nodes:
            marks.append(('MyPy Warnings', 'yellow', warning_nodes))
        if note_nodes:
            marks.append(('MyPy Notes', 'cyan', note_nodes))
        
        return MarkingConfig(marks=marks)
    
    def _map_pylint_issues(self, tree: Node, pylint_issues: list) -> list:
        """Map pylint issues to tree-sitter nodes."""
        mapped_issues = []
        
        for issue in pylint_issues:
            line = issue.get('line', 1) - 1  # Convert to 0-based
            column = issue.get('column', 0)
            
            node = self._find_node_at_position(tree, line, column)
            if node:
                mapped_issues.append({
                    'node': node,
                    'type': issue.get('type', 'unknown'),
                    'message': issue.get('message', ''),
                    'symbol': issue.get('symbol', ''),
                    'message_id': issue.get('message-id', '')
                })
        
        return mapped_issues
    
    def _parse_mypy_output(self, output: str, tree: Node) -> list:
        """Parse mypy output and map to tree nodes."""
        issues = []
        
        for line in output.strip().split('\n'):
            if not line:
                continue
            
            # Parse mypy output format: file:line:column: severity: message
            match = re.match(r'[^:]+:(\d+):(\d+):\s*(\w+):\s*(.+)', line)
            if match:
                line_num = int(match.group(1)) - 1  # Convert to 0-based
                column = int(match.group(2))
                severity = match.group(3)
                message = match.group(4)
                
                node = self._find_node_at_position(tree, line_num, column)
                if node:
                    issues.append({
                        'node': node,
                        'severity': severity,
                        'message': message,
                        'line': line_num,
                        'column': column
                    })
        
        return issues
    
    def _find_node_at_position(self, tree: Node, line: int, character: int) -> Optional[Node]:
        """Find the tree-sitter node at a specific position."""
        def find_node(node: Node) -> Optional[Node]:
            start_line, start_col = node.start_point
            end_line, end_col = node.end_point
            
            if (start_line <= line <= end_line and
                (line > start_line or start_col <= character) and
                (line < end_line or character <= end_col)):
                
                # Check children for more specific match
                for child in node.children:
                    child_result = find_node(child)
                    if child_result:
                        return child_result
                
                return node
            
            return None
        
        return find_node(tree)

# Usage examples
static_analyzer = StaticAnalysisIntegration(parser)

# Pylint integration
pylint_analysis = static_analyzer.analyze_with_pylint('example.py', source_code)
pylint_marking = static_analyzer.create_pylint_marking(pylint_analysis)

ps = PrettySitter(pylint_marking)
ps.pprint(pylint_analysis['tree'].root_node)

# MyPy integration
mypy_analysis = static_analyzer.analyze_with_mypy('example.py', source_code)
mypy_marking = static_analyzer.create_mypy_marking(mypy_analysis)

ps = PrettySitter(mypy_marking)
ps.pprint(mypy_analysis['tree'].root_node)
```

## Git Integration for Diff Analysis

```python
import subprocess
import re
from typing import List, Tuple

class GitIntegration:
    """Integration with Git for analyzing code changes."""
    
    def __init__(self, parser: Parser):
        self.parser = parser
        self.ps = PrettySitter()
    
    def analyze_diff(self, file_path: str, commit1: str = 'HEAD~1', commit2: str = 'HEAD') -> dict:
        """Analyze differences between two Git commits."""
        # Get file content from both commits
        old_content = self._get_file_at_commit(file_path, commit1)
        new_content = self._get_file_at_commit(file_path, commit2)
        
        # Parse both versions
        old_tree = self.parser.parse(old_content.encode()) if old_content else None
        new_tree = self.parser.parse(new_content.encode()) if new_content else None
        
        # Get Git diff information
        diff_info = self._get_diff_info(file_path, commit1, commit2)
        
        # Analyze changes
        changes = self._analyze_changes(old_tree, new_tree, diff_info)
        
        return {
            'old_tree': old_tree,
            'new_tree': new_tree,
            'changes': changes,
            'diff_info': diff_info
        }
    
    def create_diff_marking(self, analysis: dict, show_version: str = 'new') -> MarkingConfig:
        """Create marking configuration for diff visualization."""
        marks = []
        changes = analysis['changes']
        
        if show_version == 'new' and analysis['new_tree']:
            # Mark changes in the new version
            if changes['added_nodes']:
                marks.append(('Added', 'green2', changes['added_nodes']))
            if changes['modified_nodes']:
                marks.append(('Modified', 'yellow', changes['modified_nodes']))
            
        elif show_version == 'old' and analysis['old_tree']:
            # Mark changes in the old version
            if changes['removed_nodes']:
                marks.append(('Removed', 'red', changes['removed_nodes']))
            if changes['modified_nodes_old']:
                marks.append(('Modified', 'yellow', changes['modified_nodes_old']))
        
        return MarkingConfig(marks=marks)
    
    def _get_file_at_commit(self, file_path: str, commit: str) -> str | None:
        """Get file content at a specific commit."""
        try:
            result = subprocess.run([
                'git', 'show', f'{commit}:{file_path}'
            ], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return None
    
    def _get_diff_info(self, file_path: str, commit1: str, commit2: str) -> dict:
        """Get Git diff information."""
        try:
            result = subprocess.run([
                'git', 'diff', '--unified=0', f'{commit1}..{commit2}', file_path
            ], capture_output=True, text=True, check=True)
            
            return self._parse_diff_output(result.stdout)
        except subprocess.CalledProcessError:
            return {'hunks': []}
    
    def _parse_diff_output(self, diff_output: str) -> dict:
        """Parse Git diff output to extract change information."""
        hunks = []
        current_hunk = None
        
        for line in diff_output.split('\n'):
            # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
            hunk_match = re.match(r'@@\s*-(\d+)(?:,(\d+))?\s*\+(\d+)(?:,(\d+))?\s*@@', line)
            if hunk_match:
                old_start = int(hunk_match.group(1))
                old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                new_start = int(hunk_match.group(3))
                new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1
                
                current_hunk = {
                    'old_start': old_start - 1,  # Convert to 0-based
                    'old_count': old_count,
                    'new_start': new_start - 1,  # Convert to 0-based
                    'new_count': new_count,
                    'added_lines': [],
                    'removed_lines': [],
                    'context_lines': []
                }
                hunks.append(current_hunk)
            
            elif current_hunk and line.startswith('+') and not line.startswith('+++'):
                current_hunk['added_lines'].append(line[1:])
            elif current_hunk and line.startswith('-') and not line.startswith('---'):
                current_hunk['removed_lines'].append(line[1:])
            elif current_hunk and line.startswith(' '):
                current_hunk['context_lines'].append(line[1:])
        
        return {'hunks': hunks}
    
    def _analyze_changes(self, old_tree: Node | None, new_tree: Node | None, diff_info: dict) -> dict:
        """Analyze changes between two parse trees using diff information."""
        changes = {
            'added_nodes': [],
            'removed_nodes': [],
            'modified_nodes': [],
            'modified_nodes_old': []
        }
        
        if not old_tree or not new_tree:
            return changes
        
        # Map diff hunks to tree nodes
        for hunk in diff_info['hunks']:
            # Find nodes in the changed regions
            old_nodes = self._find_nodes_in_range(
                old_tree, hunk['old_start'], hunk['old_start'] + hunk['old_count']
            )
            new_nodes = self._find_nodes_in_range(
                new_tree, hunk['new_start'], hunk['new_start'] + hunk['new_count']
            )
            
            # Classify changes
            if hunk['added_lines'] and not hunk['removed_lines']:
                # Pure addition
                changes['added_nodes'].extend(new_nodes)
            elif hunk['removed_lines'] and not hunk['added_lines']:
                # Pure removal
                changes['removed_nodes'].extend(old_nodes)
            else:
                # Modification
                changes['modified_nodes'].extend(new_nodes)
                changes['modified_nodes_old'].extend(old_nodes)
        
        return changes
    
    def _find_nodes_in_range(self, tree: Node, start_line: int, end_line: int) -> List[Node]:
        """Find all nodes that intersect with a line range."""
        nodes = []
        
        def visit(node: Node):
            node_start, _ = node.start_point
            node_end, _ = node.end_point
            
            # Check if node intersects with the range
            if node_start <= end_line and node_end >= start_line:
                nodes.append(node)
            
            for child in node.children:
                visit(child)
        
        visit(tree)
        return nodes

# Usage example
git_integration = GitIntegration(parser)

# Analyze changes between commits
diff_analysis = git_integration.analyze_diff('example.py', 'HEAD~1', 'HEAD')

# Show new version with changes highlighted
new_marking = git_integration.create_diff_marking(diff_analysis, 'new')
ps = PrettySitter(new_marking)
if diff_analysis['new_tree']:
    ps.pprint(diff_analysis['new_tree'].root_node)

# Show old version with changes highlighted
old_marking = git_integration.create_diff_marking(diff_analysis, 'old')
ps = PrettySitter(old_marking)
if diff_analysis['old_tree']:
    ps.pprint(diff_analysis['old_tree'].root_node)
```

## Best Practices for Integration

### Error Handling and Robustness

```python
class RobustIntegration:
    """Robust integration with comprehensive error handling."""
    
    def __init__(self, parser: Parser):
        self.parser = parser
        self.ps = PrettySitter()
        self.error_log = []
    
    def safe_integration(self, source_code: str, integrations: list) -> dict:
        """Safely run multiple integrations with error recovery."""
        tree = self.parser.parse(source_code.encode())
        results = {'tree': tree, 'integrations': {}}
        
        for integration_name, integration_func in integrations:
            try:
                result = integration_func(source_code, tree)
                results['integrations'][integration_name] = result
            except Exception as e:
                self.error_log.append(f"Integration {integration_name} failed: {e}")
                results['integrations'][integration_name] = None
        
        return results
    
    def create_fallback_marking(self, results: dict) -> MarkingConfig:
        """Create marking configuration with fallback for failed integrations."""
        marks = []
        
        # Collect marks from successful integrations
        for name, result in results['integrations'].items():
            if result and 'marks' in result:
                marks.extend(result['marks'])
        
        # Add basic structural highlighting as fallback
        if not marks:
            marks = self._create_basic_structural_marks(results['tree'])
        
        return MarkingConfig(marks=marks)
    
    def _create_basic_structural_marks(self, tree: Node) -> list:
        """Create basic structural highlighting as fallback."""
        functions = []
        classes = []
        
        def visit(node: Node):
            if node.type == 'function_definition':
                functions.append(node)
            elif node.type == 'class_definition':
                classes.append(node)
            
            for child in node.children:
                visit(child)
        
        visit(tree)
        
        marks = []
        if functions:
            marks.append(('Functions', 'green2', functions))
        if classes:
            marks.append(('Classes', 'blue', classes))
        
        return marks

# Usage example
robust = RobustIntegration(parser)

integrations = [
    ('tree_tagger', lambda code, tree: tree_tagger_analysis(code, tree)),
    ('lsp', lambda code, tree: lsp_analysis(code, tree)),
    ('static_analysis', lambda code, tree: static_analysis(code, tree))
]

results = robust.safe_integration(source_code, integrations)
marking = robust.create_fallback_marking(results)

ps = PrettySitter(marking)
ps.pprint(results['tree'].root_node)
```

### Performance Optimization

```python
class OptimizedIntegration:
    """Performance-optimized integration patterns."""
    
    def __init__(self, parser: Parser):
        self.parser = parser
        self.ps = PrettySitter()
        self.cache = {}
    
    def cached_analysis(self, source_code: str, cache_key: str = None) -> dict:
        """Perform analysis with caching for repeated operations."""
        if cache_key is None:
            cache_key = hash(source_code)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Perform expensive analysis
        tree = self.parser.parse(source_code.encode())
        analysis = self._perform_analysis(tree, source_code)
        
        # Cache results
        self.cache[cache_key] = analysis
        return analysis
    
    def batch_analysis(self, files: dict[str, str]) -> dict:
        """Analyze multiple files efficiently."""
        results = {}
        
        # Pre-compile patterns and initialize tools once
        self._initialize_batch_tools()
        
        for file_path, source_code in files.items():
            try:
                results[file_path] = self._analyze_single_file(source_code)
            except Exception as e:
                results[file_path] = {'error': str(e)}
        
        return results
    
    def _perform_analysis(self, tree: Node, source_code: str) -> dict:
        """Perform comprehensive analysis."""
        # Implementation would include various analysis steps
        return {'tree': tree, 'analysis_complete': True}
    
    def _initialize_batch_tools(self):
        """Initialize tools for batch processing."""
        # Pre-compile regular expressions, initialize external tools, etc.
        pass
    
    def _analyze_single_file(self, source_code: str) -> dict:
        """Analyze a single file efficiently."""
        tree = self.parser.parse(source_code.encode())
        return self._perform_analysis(tree, source_code)

# Usage example
optimized = OptimizedIntegration(parser)

# Single file with caching
analysis = optimized.cached_analysis(source_code, 'example.py')

# Batch processing
files = {
    'file1.py': source_code1,
    'file2.py': source_code2,
    'file3.py': source_code3
}
batch_results = optimized.batch_analysis(files)
```

This integration examples guide demonstrates how to combine pretty-sitter with various tools and frameworks to create powerful code analysis and visualization systems. The examples show practical implementations that can be adapted for specific use cases and requirements.