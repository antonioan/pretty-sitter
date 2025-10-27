#!/usr/bin/env python3
"""
Validate navigation structure and search functionality for the documentation site.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


def extract_links_from_markdown(file_path: Path) -> List[str]:
    """Extract all markdown links from a file."""
    content = file_path.read_text()
    
    # Split content into code blocks and regular content
    parts = re.split(r'```[^`]*```', content, flags=re.DOTALL)
    
    # Only extract links from non-code parts (odd indices)
    markdown_content = ''.join(parts[::2])
    
    # Match markdown links: [text](url) but exclude code examples
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_content)
    return [url for text, url in links if not url.startswith('http') and not url in ['text', 'str', 'int', 'bool']]


def validate_internal_links(docs_dir: Path) -> Tuple[List[str], List[str]]:
    """Validate all internal links in documentation."""
    valid_links = []
    broken_links = []
    
    for md_file in docs_dir.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
            
        links = extract_links_from_markdown(md_file)
        for link in links:
            # Remove anchors for file existence check
            file_link = link.split('#')[0] if '#' in link else link
            
            if file_link:  # Skip empty links (anchor-only)
                # Resolve relative path
                target_path = (md_file.parent / file_link).resolve()
                
                if target_path.exists():
                    valid_links.append(f"{md_file.name} -> {link}")
                else:
                    broken_links.append(f"{md_file.name} -> {link} (missing: {target_path})")
    
    return valid_links, broken_links


def validate_navigation_structure(mkdocs_config: Path) -> Dict[str, any]:
    """Validate the navigation structure by parsing mkdocs.yml content."""
    content = mkdocs_config.read_text()
    
    validation_results = {
        'total_sections': 0,
        'total_pages': 0,
        'missing_files': [],
        'orphaned_files': [],
        'structure_issues': []
    }
    
    docs_dir = mkdocs_config.parent / 'docs'
    referenced_files = set()
    
    # Simple regex-based parsing for navigation files
    nav_section = False
    for line in content.split('\n'):
        line = line.strip()
        
        if line.startswith('nav:'):
            nav_section = True
            continue
        elif nav_section and line and not line.startswith(' ') and not line.startswith('-'):
            # End of nav section
            break
        elif nav_section and '.md' in line:
            # Extract file path from navigation line
            import re
            match = re.search(r'([a-zA-Z0-9/_-]+\.md)', line)
            if match:
                file_path = match.group(1)
                referenced_files.add(file_path)
                validation_results['total_pages'] += 1
                
                full_path = docs_dir / file_path
                if not full_path.exists():
                    validation_results['missing_files'].append(file_path)
    
    # Find orphaned files
    all_md_files = set()
    for md_file in docs_dir.rglob("*.md"):
        if not md_file.name.startswith('.'):
            rel_path = md_file.relative_to(docs_dir)
            all_md_files.add(str(rel_path))
    
    validation_results['orphaned_files'] = list(all_md_files - referenced_files)
    
    return validation_results


def validate_search_configuration(mkdocs_config: Path) -> Dict[str, any]:
    """Validate search plugin configuration by parsing content."""
    content = mkdocs_config.read_text()
    
    validation_results = {
        'search_enabled': 'search' in content,
        'search_config': {},
        'features_enabled': []
    }
    
    # Check for search features
    search_features = []
    if 'search.highlight' in content:
        search_features.append('search.highlight')
    if 'search.share' in content:
        search_features.append('search.share')
    if 'search.suggest' in content:
        search_features.append('search.suggest')
    
    validation_results['features_enabled'] = search_features
    
    return validation_results


def main():
    """Run all navigation and search validations."""
    print("🔍 Validating documentation navigation and search...")
    
    docs_dir = Path("docs")
    mkdocs_config = Path("mkdocs.yml")
    
    if not docs_dir.exists():
        print("❌ docs/ directory not found")
        return 1
    
    if not mkdocs_config.exists():
        print("❌ mkdocs.yml not found")
        return 1
    
    # Validate internal links
    print("\n📎 Checking internal links...")
    valid_links, broken_links = validate_internal_links(docs_dir)
    
    if broken_links:
        print(f"❌ Found {len(broken_links)} broken links:")
        for link in broken_links[:10]:  # Show first 10
            print(f"   {link}")
        if len(broken_links) > 10:
            print(f"   ... and {len(broken_links) - 10} more")
    else:
        print(f"✅ All {len(valid_links)} internal links are valid")
    
    # Validate navigation structure
    print("\n🧭 Checking navigation structure...")
    nav_results = validate_navigation_structure(mkdocs_config)
    
    print(f"   📊 {nav_results['total_sections']} sections, {nav_results['total_pages']} pages")
    
    if nav_results['missing_files']:
        print(f"❌ Missing files referenced in navigation:")
        for file in nav_results['missing_files']:
            print(f"   {file}")
    
    if nav_results['orphaned_files']:
        print(f"⚠️  Orphaned files (not in navigation):")
        for file in nav_results['orphaned_files'][:5]:  # Show first 5
            print(f"   {file}")
        if len(nav_results['orphaned_files']) > 5:
            print(f"   ... and {len(nav_results['orphaned_files']) - 5} more")
    
    if not nav_results['missing_files'] and not nav_results['orphaned_files']:
        print("✅ Navigation structure is valid")
    
    # Validate search configuration
    print("\n🔍 Checking search configuration...")
    search_results = validate_search_configuration(mkdocs_config)
    
    if search_results['search_enabled']:
        print("✅ Search plugin is enabled")
        if search_results['features_enabled']:
            print(f"   📋 Search features: {', '.join(search_results['features_enabled'])}")
    else:
        print("❌ Search plugin is not enabled")
    
    # Summary
    print("\n📋 Validation Summary:")
    total_issues = len(broken_links) + len(nav_results['missing_files'])
    
    if total_issues == 0:
        print("✅ All validations passed! Navigation and search are properly configured.")
        return 0
    else:
        print(f"⚠️  Found {total_issues} issues that should be addressed.")
        return 1


if __name__ == "__main__":
    exit(main())