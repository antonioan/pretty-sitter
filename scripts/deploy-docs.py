#!/usr/bin/env python3
"""
Script to deploy documentation to GitHub Pages.

This script provides utilities for:
- Building and testing documentation locally
- Deploying to GitHub Pages
- Managing versioned documentation
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=False)


def build_docs(strict: bool = True) -> bool:
    """Build the documentation."""
    print("Building documentation...")
    cmd = ["mkdocs", "build"]
    if strict:
        cmd.append("--strict")
    
    try:
        run_command(cmd)
        print("✅ Documentation built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Documentation build failed: {e}")
        return False


def serve_docs(port: int = 8000) -> None:
    """Serve documentation locally."""
    print(f"Serving documentation on http://localhost:{port}")
    run_command(["mkdocs", "serve", "--dev-addr", f"localhost:{port}"])


def deploy_docs(version: str = "latest") -> bool:
    """Deploy documentation using mike for versioning."""
    print(f"Deploying documentation version: {version}")
    
    try:
        if version == "latest":
            run_command(["mike", "deploy", "--push", "--update-aliases", "latest", "main"])
            run_command(["mike", "set-default", "--push", "latest"])
        else:
            run_command(["mike", "deploy", "--push", "--update-aliases", version, "latest"])
            run_command(["mike", "set-default", "--push", "latest"])
        
        print("✅ Documentation deployed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Documentation deployment failed: {e}")
        return False


def validate_deployment() -> bool:
    """Validate that the deployment is working correctly."""
    print("Validating deployment...")
    
    # Check if site directory exists and has required files
    site_dir = Path("site")
    if not site_dir.exists():
        print("❌ Site directory not found. Run build first.")
        return False
    
    required_files = [
        "index.html",
        "getting-started/installation/index.html",
        "reference/api/pretty-sitter/index.html",
        "search/search_index.json"
    ]
    
    for file_path in required_files:
        full_path = site_dir / file_path
        if not full_path.exists():
            print(f"❌ Required file missing: {file_path}")
            return False
    
    print("✅ Deployment validation passed")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Deploy documentation")
    parser.add_argument(
        "action",
        choices=["build", "serve", "deploy", "validate"],
        help="Action to perform"
    )
    parser.add_argument(
        "--version",
        default="latest",
        help="Version to deploy (for deploy action)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for local server (for serve action)"
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Disable strict mode for build"
    )
    
    args = parser.parse_args()
    
    if args.action == "build":
        success = build_docs(strict=not args.no_strict)
        sys.exit(0 if success else 1)
    elif args.action == "serve":
        serve_docs(args.port)
    elif args.action == "deploy":
        success = deploy_docs(args.version)
        sys.exit(0 if success else 1)
    elif args.action == "validate":
        success = validate_deployment()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()