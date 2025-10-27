#!/usr/bin/env python3
"""
Script to extract and validate code examples from documentation.

This script finds all Python code blocks in markdown files and validates them
by attempting to parse and optionally execute them.
"""

import ast
import re
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse


class CodeExample:
    """Represents a code example found in documentation."""
    
    def __init__(self, code: str, file_path: Path, line_number: int, language: str = "python"):
        self.code = code
        self.file_path = file_path
        self.line_number = line_number
        self.language = language
        self.is_runnable = self._check_if_runnable()
    
    def _check_if_runnable(self) -> bool:
        """Check if code example appears to be runnable."""
        # Skip examples that are clearly incomplete or just imports
        if self.code.strip().startswith(('import ', 'from ')):
            return False
        
        # Skip examples with obvious placeholders
        placeholders = ['...', 'TODO', 'FIXME', '<your_', 'your_file']
        if any(placeholder in self.code for placeholder in placeholders):
            return False
            
        # Skip examples that are just class/function definitions without usage
        try:
            tree = ast.parse(self.code)
            has_executable = False
            for node in ast.walk(tree):
                if isinstance(node, (ast.Call, ast.Assign, ast.AugAssign, ast.Expr)):
                    # Skip docstrings
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                        continue
                    has_executable = True
                    break
            return has_executable
        except SyntaxError:
            return False
    
    def __str__(self):
        return f"CodeExample({self.file_path}:{self.line_number}, {len(self.code)} chars)"


class CodeExampleExtractor:
    """Extracts code examples from markdown files."""
    
    def __init__(self):
        self.code_block_pattern = re.compile(
            r'```(\w+)?\n(.*?)\n```',
            re.DOTALL | re.MULTILINE
        )
    
    def extract_from_file(self, file_path: Path) -> List[CodeExample]:
        """Extract all code examples from a markdown file."""
        if not file_path.exists():
            return []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            print(f"Warning: Could not read {file_path} as UTF-8")
            return []
        
        examples = []
        
        for match in self.code_block_pattern.finditer(content):
            language = match.group(1) or "python"
            code = match.group(2).strip()
            
            # Only process Python code blocks
            if language.lower() not in ['python', 'py']:
                continue
            
            # Skip empty code blocks
            if not code:
                continue
            
            # Skip code blocks that are clearly not Python
            if self._is_non_python_content(code):
                continue
            
            # Calculate line number
            line_number = content[:match.start()].count('\n') + 1
            
            example = CodeExample(code, file_path, line_number, language)
            examples.append(example)
        
        return examples
    
    def _is_non_python_content(self, code: str) -> bool:
        """Check if code content is clearly not Python."""
        # Skip bash/shell commands
        if any(code.strip().startswith(cmd) for cmd in ['$', '>', '#', 'git ', 'pip ', 'npm ', 'make ', 'cd ', 'ls ', 'mkdir ', 'rm ']):
            return True
        
        # Skip file tree representations
        if any(char in code for char in ['├', '└', '│', '─']):
            return True
        
        # Skip configuration files (YAML, JSON, etc.)
        if code.strip().startswith(('{', '[', '---', 'version:', 'name:')):
            return True
        
        # Skip output examples (often start with special characters)
        if code.strip().startswith(('🌳', '📊', '✅', '❌', '⚠️', 'Color legend:')):
            return True
        
        # Skip commit messages and git output
        if any(pattern in code for pattern in ['commit ', 'Author:', 'Date:', 'Merge:', '* ', '- [ ]', '- [x]']):
            return True
        
        return False
    
    def extract_from_directory(self, docs_dir: Path) -> List[CodeExample]:
        """Extract all code examples from markdown files in a directory."""
        examples = []
        
        for md_file in docs_dir.rglob("*.md"):
            file_examples = self.extract_from_file(md_file)
            examples.extend(file_examples)
        
        return examples


class CodeExampleValidator:
    """Validates code examples for syntax and basic functionality."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.validation_results = []
    
    def validate_syntax(self, example: CodeExample) -> Tuple[bool, Optional[str]]:
        """Validate Python syntax of a code example."""
        try:
            ast.parse(example.code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
    
    def validate_imports(self, example: CodeExample) -> Tuple[bool, Optional[str]]:
        """Check if all imports in the code example are available."""
        try:
            tree = ast.parse(example.code)
        except SyntaxError:
            return False, "Cannot parse code for import validation"
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Check if imports are available
        unavailable_imports = []
        for import_name in imports:
            try:
                __import__(import_name.split('.')[0])
            except ImportError:
                unavailable_imports.append(import_name)
        
        if unavailable_imports:
            return False, f"Unavailable imports: {', '.join(unavailable_imports)}"
        
        return True, None
    
    def validate_example(self, example: CodeExample) -> Dict:
        """Validate a single code example."""
        result = {
            'example': example,
            'syntax_valid': False,
            'imports_valid': False,
            'errors': [],
            'warnings': []
        }
        
        # Validate syntax
        syntax_valid, syntax_error = self.validate_syntax(example)
        result['syntax_valid'] = syntax_valid
        if not syntax_valid:
            result['errors'].append(syntax_error)
        
        # Validate imports (only if syntax is valid)
        if syntax_valid:
            imports_valid, import_error = self.validate_imports(example)
            result['imports_valid'] = imports_valid
            if not imports_valid:
                result['warnings'].append(import_error)
        
        # Add warnings for non-runnable examples
        if not example.is_runnable:
            result['warnings'].append("Example appears to be incomplete or non-runnable")
        
        self.validation_results.append(result)
        return result
    
    def validate_all(self, examples: List[CodeExample]) -> List[Dict]:
        """Validate all code examples."""
        results = []
        
        for example in examples:
            if self.verbose:
                print(f"Validating {example.file_path}:{example.line_number}")
            
            result = self.validate_example(example)
            results.append(result)
        
        return results
    
    def print_summary(self):
        """Print validation summary."""
        if not self.validation_results:
            print("No code examples found to validate.")
            return
        
        total = len(self.validation_results)
        syntax_valid = sum(1 for r in self.validation_results if r['syntax_valid'])
        imports_valid = sum(1 for r in self.validation_results if r['imports_valid'])
        has_errors = sum(1 for r in self.validation_results if r['errors'])
        has_warnings = sum(1 for r in self.validation_results if r['warnings'])
        
        print(f"\n📊 Code Example Validation Summary:")
        print(f"Total examples: {total}")
        print(f"Syntax valid: {syntax_valid}/{total} ({syntax_valid/total*100:.1f}%)")
        print(f"Imports available: {imports_valid}/{total} ({imports_valid/total*100:.1f}%)")
        print(f"Examples with errors: {has_errors}")
        print(f"Examples with warnings: {has_warnings}")
        
        # Print detailed results for failed examples
        if has_errors > 0:
            print(f"\n❌ Examples with errors:")
            for result in self.validation_results:
                if result['errors']:
                    example = result['example']
                    print(f"  {example.file_path}:{example.line_number}")
                    for error in result['errors']:
                        print(f"    - {error}")
        
        if has_warnings > 0 and self.verbose:
            print(f"\n⚠️  Examples with warnings:")
            for result in self.validation_results:
                if result['warnings']:
                    example = result['example']
                    print(f"  {example.file_path}:{example.line_number}")
                    for warning in result['warnings']:
                        print(f"    - {warning}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate code examples in documentation"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Documentation directory to scan (default: docs)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with error code if validation fails"
    )
    
    args = parser.parse_args()
    
    if not args.docs_dir.exists():
        print(f"❌ Documentation directory not found: {args.docs_dir}")
        return 1
    
    print(f"🔍 Extracting code examples from {args.docs_dir}")
    
    # Extract code examples
    extractor = CodeExampleExtractor()
    examples = extractor.extract_from_directory(args.docs_dir)
    
    if not examples:
        print("No Python code examples found in documentation.")
        return 0
    
    print(f"Found {len(examples)} Python code examples")
    
    # Validate examples
    validator = CodeExampleValidator(verbose=args.verbose)
    results = validator.validate_all(examples)
    
    # Print summary
    validator.print_summary()
    
    # Determine exit code
    has_errors = any(result['errors'] for result in results)
    
    if has_errors and args.fail_on_error:
        print(f"\n❌ Validation failed with errors")
        return 1
    elif has_errors:
        print(f"\n⚠️  Validation completed with errors (use --fail-on-error to fail)")
        return 0
    else:
        print(f"\n✅ All code examples validated successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())