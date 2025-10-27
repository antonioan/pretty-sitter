# Troubleshooting

Having issues with Pretty Sitter? This section provides solutions to common problems and guidance on getting help.

## Quick Solutions

### Most Common Issues

1. **Installation Problems** - See [Common Issues](common-issues.md#installation-issues)
2. **Color Output Not Working** - Check [Terminal and Display Issues](common-issues.md#terminal-and-display-issues)
3. **Parse Tree Empty** - Verify [Parse Tree Issues](common-issues.md#parse-tree-issues)
4. **Performance Issues** - Review [Memory and Performance Issues](common-issues.md#memory-and-performance-issues)

### Quick Diagnostic Steps

Before diving into detailed troubleshooting:

1. **Check your Python version**: Pretty Sitter requires Python 3.11+
2. **Verify installation**: Run `python -c "import pretty_sitter; print('OK')"`
3. **Test basic functionality**: Try the examples from [Quick Start](../getting-started/quick-start.md)
4. **Check dependencies**: Ensure tree-sitter parsers are properly installed

## Documentation Sections

- **[Common Issues](common-issues.md)** - Known problems and their solutions
- **[FAQ](faq.md)** - Frequently asked questions
- **[Bug Reporting](bug-reporting.md)** - How to report bugs effectively

## Getting Help

### Self-Service Resources

1. **Search the documentation** - Use the search box above to find relevant information
2. **Check examples** - Review [Basic Examples](../getting-started/basic-examples.md) and [Integration Examples](../guides/integration-examples.md)
3. **Review configuration** - Ensure your [Configuration](../guides/configuration-guide.md) is correct

### Community Support

If you can't find a solution in the documentation:

1. **Search existing issues** on the [GitHub repository](https://github.com/antonioan/pretty-sitter/issues)
2. **Create a new issue** following our [Bug Reporting Guidelines](bug-reporting.md)
3. **Include diagnostic information** as described in the bug reporting guide

### Before Reporting Issues

Please gather this information:

- Python version (`python --version`)
- Pretty Sitter version (`pip show pretty-sitter`)
- Operating system and terminal type
- Minimal code example that reproduces the issue
- Expected vs. actual behavior

## Contributing Fixes

Found a bug and know how to fix it? We welcome contributions! See our [Contributing Guidelines](../contributing/development-setup.md) for information on:

- Setting up a development environment
- Running tests
- Submitting pull requests