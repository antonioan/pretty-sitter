#!/usr/bin/env python3
"""
Script to validate documentation configuration and structure.
"""

import sys
from pathlib import Path
import yaml


def validate_mkdocs_config():
    """Validate MkDocs configuration file."""
    config_path = Path("mkdocs.yml")

    if not config_path.exists():
        print("❌ mkdocs.yml not found")
        return False

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        required_fields = ["site_name", "nav", "theme", "plugins"]
        missing_fields = [field for field in required_fields if field not in config]

        if missing_fields:
            print(f"❌ Missing required fields in mkdocs.yml: {missing_fields}")
            return False

        print("✅ mkdocs.yml configuration is valid")
        return True

    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in mkdocs.yml: {e}")
        return False


def validate_docs_structure():
    """Validate documentation directory structure."""
    docs_dir = Path("docs")

    if not docs_dir.exists():
        print("❌ docs/ directory not found")
        return False

    required_dirs = [
        "getting-started",
        "guides",
        "reference/api",
        "troubleshooting",
        "contributing",
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not (docs_dir / dir_path).exists():
            missing_dirs.append(dir_path)

    if missing_dirs:
        print(f"❌ Missing documentation directories: {missing_dirs}")
        return False

    if not (docs_dir / "index.md").exists():
        print("❌ Missing docs/index.md")
        return False

    print("✅ Documentation structure is valid")
    return True


def main():
    """Run all validation checks."""
    print("Validating documentation setup...")

    checks = [validate_mkdocs_config, validate_docs_structure]

    all_passed = True
    for check in checks:
        if not check():
            all_passed = False

    if all_passed:
        print("\n🎉 All documentation validation checks passed!")
        return 0
    else:
        print("\n❌ Some validation checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
