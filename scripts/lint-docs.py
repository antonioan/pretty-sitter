#!/usr/bin/env python3
"""
Comprehensive documentation linting and validation script.

This script runs multiple validation tools on the documentation:
- Markdown linting with markdownlint
- Spell checking with cspell
- Link validation with markdown-link-check
- Code example validation
- Documentation structure validation
"""

import subprocess
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import argparse
import json


class LintResult:
    """Represents the result of a linting operation."""
    
    def __init__(self, name: str, success: bool, output: str = "", error: str = ""):
        self.name = name
        self.success = success
        self.output = output
        self.error = error
    
    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.name}"


class DocumentationLinter:
    """Comprehensive documentation linter."""
    
    def __init__(self, docs_dir: Path, verbose: bool = False):
        self.docs_dir = docs_dir
        self.verbose = verbose
        self.results: List[LintResult] = []
    
    def _run_command(self, cmd: List[str], name: str, cwd: Optional[Path] = None) -> LintResult:
        """Run a command and return the result."""
        if self.verbose:
            print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or Path.cwd(),
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            return LintResult(
                name=name,
                success=success,
                output=result.stdout,
                error=result.stderr
            )
        
        except subprocess.TimeoutExpired:
            return LintResult(
                name=name,
                success=False,
                error="Command timed out after 5 minutes"
            )
        except FileNotFoundError:
            return LintResult(
                name=name,
                success=False,
                error="Command not found - tool may not be installed"
            )
        except Exception as e:
            return LintResult(
                name=name,
                success=False,
                error=f"Unexpected error: {e}"
            )
    
    def check_tool_availability(self) -> List[Tuple[str, bool]]:
        """Check which linting tools are available."""
        tools = [
            ("python", ["python", "--version"]),
            ("markdownlint", ["markdownlint", "--version"]),
            ("cspell", ["cspell", "--version"]),
            ("markdown-link-check", ["markdown-link-check", "--version"])
        ]
        
        availability = []
        for tool_name, cmd in tools:
            try:
                subprocess.run(cmd, capture_output=True, check=True, timeout=10)
                availability.append((tool_name, True))
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                availability.append((tool_name, False))
        
        return availability
    
    def lint_markdown_style(self) -> LintResult:
        """Run markdownlint on documentation files."""
        config_file = Path(".markdownlint.json")
        
        cmd = ["markdownlint", str(self.docs_dir)]
        if config_file.exists():
            cmd.extend(["--config", str(config_file)])
        
        return self._run_command(cmd, "Markdown Style (markdownlint)")
    
    def check_spelling(self) -> LintResult:
        """Run spell check on documentation files."""
        config_file = Path(".cspell.json")
        
        cmd = ["cspell", f"{self.docs_dir}/**/*.md"]
        if config_file.exists():
            cmd.extend(["--config", str(config_file)])
        
        return self._run_command(cmd, "Spell Check (cspell)")
    
    def check_links(self) -> LintResult:
        """Check links in documentation files."""
        # Find all markdown files
        md_files = list(self.docs_dir.rglob("*.md"))
        
        if not md_files:
            return LintResult(
                name="Link Check (markdown-link-check)",
                success=True,
                output="No markdown files found"
            )
        
        # Check links in each file
        all_output = []
        all_errors = []
        overall_success = True
        
        for md_file in md_files:
            result = self._run_command(
                ["markdown-link-check", str(md_file)],
                f"Link check for {md_file.name}"
            )
            
            if not result.success:
                overall_success = False
                all_errors.append(f"{md_file}: {result.error}")
            
            all_output.append(f"{md_file}: {result.output}")
        
        return LintResult(
            name="Link Check (markdown-link-check)",
            success=overall_success,
            output="\n".join(all_output),
            error="\n".join(all_errors)
        )
    
    def validate_code_examples(self) -> LintResult:
        """Validate code examples in documentation."""
        script_path = Path(__file__).parent / "validate-code-examples.py"
        
        if not script_path.exists():
            return LintResult(
                name="Code Example Validation",
                success=False,
                error="validate-code-examples.py script not found"
            )
        
        cmd = [
            sys.executable,
            str(script_path),
            "--docs-dir", str(self.docs_dir),
            "--fail-on-error"
        ]
        
        if self.verbose:
            cmd.append("--verbose")
        
        return self._run_command(cmd, "Code Example Validation")
    
    def validate_structure(self) -> LintResult:
        """Validate documentation structure."""
        script_path = Path(__file__).parent / "validate-docs.py"
        
        if not script_path.exists():
            return LintResult(
                name="Documentation Structure",
                success=False,
                error="validate-docs.py script not found"
            )
        
        return self._run_command(
            [sys.executable, str(script_path)],
            "Documentation Structure"
        )
    
    def run_all_checks(self, skip_tools: List[str] = None) -> List[LintResult]:
        """Run all available linting checks."""
        skip_tools = skip_tools or []
        
        # Check tool availability first
        if self.verbose:
            print("Checking tool availability...")
            availability = self.check_tool_availability()
            for tool, available in availability:
                status = "✅" if available else "❌"
                print(f"  {status} {tool}")
            print()
        
        # Define all checks
        checks = [
            ("structure", self.validate_structure),
            ("code-examples", self.validate_code_examples),
            ("markdown", self.lint_markdown_style),
            ("spelling", self.check_spelling),
            ("links", self.check_links),
        ]
        
        results = []
        
        for check_name, check_func in checks:
            if check_name in skip_tools:
                if self.verbose:
                    print(f"Skipping {check_name} check")
                continue
            
            if self.verbose:
                print(f"Running {check_name} check...")
            
            result = check_func()
            results.append(result)
            
            if self.verbose:
                print(f"  {result}")
                if result.output and self.verbose:
                    print(f"    Output: {result.output[:200]}...")
                if result.error:
                    print(f"    Error: {result.error[:200]}...")
                print()
        
        self.results = results
        return results
    
    def print_summary(self):
        """Print a summary of all linting results."""
        if not self.results:
            print("No linting results to display.")
            return
        
        print("📋 Documentation Linting Summary")
        print("=" * 50)
        
        passed = 0
        failed = 0
        
        for result in self.results:
            print(f"  {result}")
            if result.success:
                passed += 1
            else:
                failed += 1
        
        print()
        print(f"Total checks: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print(f"\n❌ Failed checks:")
            for result in self.results:
                if not result.success:
                    print(f"\n  {result.name}:")
                    if result.error:
                        print(f"    Error: {result.error}")
                    if result.output and "error" in result.output.lower():
                        print(f"    Output: {result.output}")
        
        success_rate = (passed / len(self.results)) * 100
        print(f"\nSuccess rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("🎉 All documentation checks passed!")
        else:
            print(f"⚠️  {failed} check(s) failed")
    
    def save_results(self, output_file: Path):
        """Save linting results to a JSON file."""
        results_data = []
        
        for result in self.results:
            results_data.append({
                "name": result.name,
                "success": result.success,
                "output": result.output,
                "error": result.error
            })
        
        with open(output_file, 'w') as f:
            json.dump({
                "timestamp": str(Path().cwd()),
                "docs_directory": str(self.docs_dir),
                "total_checks": len(self.results),
                "passed": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
                "results": results_data
            }, f, indent=2)
        
        print(f"Results saved to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive documentation linting and validation"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Documentation directory to lint (default: docs)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--skip",
        nargs="*",
        choices=["structure", "code-examples", "markdown", "spelling", "links"],
        default=[],
        help="Skip specific linting tools"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with error code if any checks fail"
    )
    
    args = parser.parse_args()
    
    if not args.docs_dir.exists():
        print(f"❌ Documentation directory not found: {args.docs_dir}")
        return 1
    
    print(f"🔍 Linting documentation in {args.docs_dir}")
    if args.skip:
        print(f"Skipping: {', '.join(args.skip)}")
    print()
    
    # Run linting
    linter = DocumentationLinter(args.docs_dir, verbose=args.verbose)
    results = linter.run_all_checks(skip_tools=args.skip)
    
    # Print summary
    linter.print_summary()
    
    # Save results if requested
    if args.output:
        linter.save_results(args.output)
    
    # Determine exit code
    failed_count = sum(1 for r in results if not r.success)
    
    if failed_count > 0 and args.fail_on_error:
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())