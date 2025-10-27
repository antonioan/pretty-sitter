#!/usr/bin/env python3
"""
Script to install documentation linting tools.

This script installs the required Node.js tools for documentation linting:
- markdownlint-cli
- cspell
- markdown-link-check
"""

import subprocess
import sys
import shutil
from pathlib import Path


def check_node_installed():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js is not working properly")
            return False
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        return False


def check_npm_installed():
    """Check if npm is installed."""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ npm is not working properly")
            return False
    except FileNotFoundError:
        print("❌ npm is not installed")
        return False


def install_npm_package(package_name):
    """Install an npm package globally."""
    print(f"Installing {package_name}...")
    try:
        result = subprocess.run(
            ["npm", "install", "-g", package_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ {package_name} installed successfully")
            return True
        else:
            print(f"❌ Failed to install {package_name}")
            print(f"Error: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"❌ Installation of {package_name} timed out")
        return False
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False


def check_tool_installed(tool_name, version_cmd):
    """Check if a tool is installed and working."""
    try:
        result = subprocess.run(version_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✅ {tool_name} is available: {version}")
            return True
        else:
            print(f"❌ {tool_name} is not working properly")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"❌ {tool_name} is not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking {tool_name}: {e}")
        return False


def main():
    """Main installation process."""
    print("🔧 Installing documentation linting tools")
    print("=" * 50)
    
    # Check prerequisites
    if not check_node_installed():
        print("\n❌ Node.js is required but not installed.")
        print("Please install Node.js from https://nodejs.org/")
        return 1
    
    if not check_npm_installed():
        print("\n❌ npm is required but not installed.")
        print("npm usually comes with Node.js. Please reinstall Node.js.")
        return 1
    
    print()
    
    # Define tools to install
    tools = [
        ("markdownlint-cli", ["markdownlint", "--version"]),
        ("cspell", ["cspell", "--version"]),
        ("markdown-link-check", ["markdown-link-check", "--version"])
    ]
    
    # Check which tools are already installed
    print("Checking existing installations...")
    already_installed = []
    need_installation = []
    
    for package_name, version_cmd in tools:
        if check_tool_installed(package_name, version_cmd):
            already_installed.append(package_name)
        else:
            need_installation.append((package_name, version_cmd))
    
    print()
    
    if not need_installation:
        print("🎉 All linting tools are already installed!")
        return 0
    
    # Install missing tools
    print(f"Installing {len(need_installation)} missing tools...")
    failed_installations = []
    
    for package_name, version_cmd in need_installation:
        if install_npm_package(package_name):
            # Verify installation
            if not check_tool_installed(package_name, version_cmd):
                failed_installations.append(package_name)
        else:
            failed_installations.append(package_name)
    
    print()
    
    # Summary
    if failed_installations:
        print(f"❌ Failed to install: {', '.join(failed_installations)}")
        print("\nYou can try installing them manually:")
        for package in failed_installations:
            print(f"  npm install -g {package}")
        return 1
    else:
        print("🎉 All linting tools installed successfully!")
        print("\nYou can now run:")
        print("  python scripts/lint-docs.py")
        print("  make docs-lint")
        return 0


if __name__ == "__main__":
    sys.exit(main())