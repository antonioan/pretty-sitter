#!/usr/bin/env python3
"""
Generate additional SEO and navigation files for the documentation site.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def generate_search_keywords() -> Dict[str, List[str]]:
    """Generate search keywords for better discoverability."""
    return {
        "pretty-sitter": ["pretty", "sitter", "tree-sitter", "parser", "syntax", "tree", "ast"],
        "configuration": ["config", "settings", "options", "customize", "theme", "color"],
        "colorer": ["color", "highlight", "syntax", "theme", "brush", "ansi"],
        "installation": ["install", "setup", "pip", "python", "dependencies"],
        "examples": ["example", "tutorial", "demo", "usage", "how-to"],
        "troubleshooting": ["error", "issue", "problem", "debug", "fix", "help"],
        "api": ["reference", "documentation", "method", "class", "function"],
        "contributing": ["contribute", "development", "pull-request", "github"]
    }


def generate_navigation_data() -> Dict[str, Any]:
    """Generate navigation metadata for enhanced search."""
    return {
        "sections": [
            {
                "title": "Getting Started",
                "description": "Quick start guides and installation instructions",
                "pages": ["installation", "quick-start", "basic-examples"],
                "difficulty": "beginner"
            },
            {
                "title": "User Guides", 
                "description": "Comprehensive guides for effective usage",
                "pages": ["configuration-guide", "advanced-usage", "integration-examples"],
                "difficulty": "intermediate"
            },
            {
                "title": "API Reference",
                "description": "Complete API documentation and reference",
                "pages": ["pretty-sitter", "colorer", "config", "configuration-options"],
                "difficulty": "reference"
            },
            {
                "title": "Troubleshooting",
                "description": "Solutions to common problems and issues",
                "pages": ["common-issues", "faq", "bug-reporting"],
                "difficulty": "support"
            },
            {
                "title": "Contributing",
                "description": "Guidelines for contributing to the project",
                "pages": ["development-setup", "coding-standards", "architecture", "pull-request-guidelines"],
                "difficulty": "advanced"
            }
        ],
        "cross_references": {
            "installation": ["quick-start", "troubleshooting"],
            "configuration-guide": ["api-reference", "advanced-usage"],
            "troubleshooting": ["installation", "faq"],
            "contributing": ["development-setup", "coding-standards"]
        }
    }


def main():
    """Generate navigation and search enhancement files."""
    docs_dir = Path("docs")
    
    # Generate search keywords
    keywords = generate_search_keywords()
    keywords_file = docs_dir / ".search_keywords.json"
    with open(keywords_file, "w") as f:
        json.dump(keywords, f, indent=2)
    
    # Generate navigation metadata
    nav_data = generate_navigation_data()
    nav_file = docs_dir / ".navigation.json"
    with open(nav_file, "w") as f:
        json.dump(nav_data, f, indent=2)
    
    # Generate robots.txt
    robots_content = """User-agent: *
Allow: /

Sitemap: https://antonioan.github.io/pretty-sitter/sitemap.xml
"""
    
    robots_file = docs_dir / "robots.txt"
    with open(robots_file, "w") as f:
        f.write(robots_content)
    
    print("✅ Generated navigation and search enhancement files")
    print(f"   - {keywords_file}")
    print(f"   - {nav_file}")
    print(f"   - {robots_file}")


if __name__ == "__main__":
    main()