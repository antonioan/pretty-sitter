# Pull Request and Contribution Guidelines

This document provides detailed guidelines for submitting pull requests and contributing to pretty-sitter. Following these guidelines helps ensure a smooth review process and maintains the quality of the codebase.

## Before You Start

### 1. Check for Existing Work

Before starting work on a new feature or bug fix:

- **Search existing issues** to see if the problem is already being addressed
- **Check open pull requests** to avoid duplicate work
- **Look at the project roadmap** to understand planned features
- **Join the discussion** if you have questions about the approach

### 2. Create or Comment on an Issue

For significant changes:

- **Create an issue** describing the problem or feature request
- **Discuss the approach** with maintainers before implementing
- **Get feedback** on the proposed solution
- **Reference the issue** in your pull request

For small changes (typos, documentation fixes), you can submit a pull request directly.

## Setting Up Your Development Environment

Follow the [development setup guide](development-setup.md) to prepare your local environment.

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pretty-sitter.git
   cd pretty-sitter
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/antonioan/pretty-sitter.git
   ```

### Create a Feature Branch

Always create a new branch for your changes:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a new feature branch
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/issue-description
```

## Making Changes

### 1. Code Quality Standards

Ensure your code meets our quality standards:

```bash
# Run linting and formatting
ruff check .
ruff format .

# Run type checking
mypy pretty_sitter/

# Run tests
pytest

# Run security checks
bandit -r pretty_sitter/
```

### 2. Writing Tests

All new functionality must include tests:

- **Unit tests** for individual functions and methods
- **Integration tests** for component interactions
- **End-to-end tests** for complete workflows

Follow our [testing guidelines](coding-standards.md#testing-standards):

```python
def test_your_new_feature():
    # Arrange
    config = UIConfig(your_new_option=True)
    ps = PrettySitter(config)
    
    # Act
    result = ps.some_method()
    
    # Assert
    assert result == expected_value
```

### 3. Documentation Updates

Update documentation when your changes affect:

- **Public API**: Update docstrings and API reference
- **Configuration options**: Update configuration guide
- **User behavior**: Update user guides and examples
- **Installation or setup**: Update getting started guides

### 4. Commit Guidelines

Write clear, descriptive commit messages following [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: type(scope): description
feat(config): add support for custom color schemes
fix(colorer): resolve ANSI code stripping issue
docs(api): update PrettySitter class documentation
test(filter): add tests for complex filtering scenarios
refactor(core): simplify tree walking algorithm
```

#### Commit Types

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring without functional changes
- `perf`: Performance improvements
- `style`: Code style changes (formatting, etc.)
- `chore`: Maintenance tasks, dependency updates

#### Commit Best Practices

- **Keep commits focused**: One logical change per commit
- **Write descriptive messages**: Explain what and why, not just what
- **Use imperative mood**: "Add feature" not "Added feature"
- **Reference issues**: Include "Fixes #123" or "Closes #456"

## Submitting Your Pull Request

### 1. Pre-submission Checklist

Before submitting, ensure:

- [ ] **All tests pass** locally
- [ ] **Code follows style guidelines** (ruff check passes)
- [ ] **Type checking passes** (mypy passes)
- [ ] **Documentation is updated** if needed
- [ ] **Commit messages are clear** and follow conventions
- [ ] **Branch is up to date** with main branch

### 2. Update Your Branch

Ensure your branch is current:

```bash
# Fetch latest changes
git fetch upstream

# Rebase your branch (preferred) or merge
git rebase upstream/main
# or
git merge upstream/main

# Push your updated branch
git push origin your-branch-name
```

### 3. Create the Pull Request

1. **Go to GitHub** and navigate to your fork
2. **Click "New Pull Request"**
3. **Select the correct branches**: your feature branch → main
4. **Fill out the PR template** (see below)

### 4. Pull Request Template

Use this template for your pull request description:

```markdown
## Description

Brief description of the changes and their purpose.

Fixes #(issue number)

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing

Describe the tests you ran and how to reproduce them:

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing performed
- [ ] New tests added for new functionality

## Documentation

- [ ] Code is self-documenting with clear variable names and comments
- [ ] Docstrings updated for new/modified functions
- [ ] User documentation updated (if applicable)
- [ ] API documentation updated (if applicable)

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)

Include before/after screenshots for UI changes or examples of new output formats.

## Additional Notes

Any additional information that reviewers should know.
```

## Review Process

### What to Expect

1. **Automated checks** run first (CI/CD pipeline)
2. **Maintainer review** typically within 2-3 business days
3. **Feedback and discussion** through PR comments
4. **Approval and merge** once all requirements are met

### Responding to Feedback

- **Be responsive** to reviewer comments
- **Ask questions** if feedback is unclear
- **Make requested changes** promptly
- **Update tests and documentation** as needed
- **Resolve conversations** once addressed

### Common Review Comments

**Code Quality**:
- "Please add type hints to this function"
- "This method is too long, consider breaking it up"
- "Add error handling for this edge case"

**Testing**:
- "Please add tests for this new functionality"
- "This test case is missing"
- "Consider testing the error path as well"

**Documentation**:
- "Please update the docstring for this method"
- "Add an example to the user guide"
- "Update the configuration reference"

## Types of Contributions

### Bug Fixes

When fixing bugs:

1. **Reproduce the bug** and understand the root cause
2. **Write a test** that demonstrates the bug
3. **Fix the issue** with minimal changes
4. **Verify the test passes** with your fix
5. **Check for similar issues** elsewhere in the codebase

### New Features

For new features:

1. **Discuss the feature** in an issue first
2. **Design the API** carefully for consistency
3. **Implement incrementally** with tests at each step
4. **Update documentation** comprehensively
5. **Consider backward compatibility**

### Documentation Improvements

Documentation contributions are highly valued:

- **Fix typos and grammar** errors
- **Improve clarity** of explanations
- **Add missing examples**
- **Update outdated information**
- **Improve organization** and navigation

### Performance Improvements

When optimizing performance:

1. **Measure first** to establish baseline
2. **Profile the code** to identify bottlenecks
3. **Make targeted improvements**
4. **Verify improvements** with benchmarks
5. **Ensure correctness** is maintained

## Community Guidelines

### Code of Conduct

- **Be respectful** and professional
- **Welcome newcomers** and help them learn
- **Give constructive feedback**
- **Assume good intentions**
- **Focus on the code**, not the person

### Communication

- **Use clear, concise language**
- **Provide context** for your suggestions
- **Explain the "why"** behind your feedback
- **Be patient** with the review process
- **Thank contributors** for their time

## Advanced Contribution Scenarios

### Large Features

For significant features:

1. **Create a design document** outlining the approach
2. **Break work into smaller PRs** when possible
3. **Coordinate with maintainers** on timing
4. **Consider feature flags** for gradual rollout

### Breaking Changes

Breaking changes require special consideration:

1. **Discuss necessity** with maintainers
2. **Plan migration path** for users
3. **Update major version** number
4. **Document changes** thoroughly
5. **Provide migration guide**

### Security Issues

For security-related contributions:

1. **Report privately** first to maintainers
2. **Wait for coordination** before public disclosure
3. **Follow responsible disclosure** practices
4. **Help with testing** and verification

## Getting Help

### Resources

- **[Development Setup](development-setup.md)**: Environment setup
- **[Coding Standards](coding-standards.md)**: Style and quality guidelines
- **[Architecture](architecture.md)**: System design and patterns
- **[Troubleshooting](../troubleshooting/common-issues.md)**: Common problems and solutions

### Support Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Code Reviews**: Feedback on pull requests
- **Direct Contact**: Reach out to maintainers for sensitive issues

## Recognition

We appreciate all contributions to pretty-sitter! Contributors are recognized through:

- **Contributor list** in the README
- **Release notes** mentioning significant contributions
- **GitHub contributor graphs** and statistics
- **Community recognition** in discussions and issues

## Conclusion

Contributing to open source can be rewarding and educational. We're here to help you succeed and make meaningful contributions to pretty-sitter.

Key points to remember:

- **Start small** and build up to larger contributions
- **Ask questions** when you're unsure
- **Follow the guidelines** to streamline the review process
- **Be patient** with the review process
- **Learn from feedback** and improve over time

Thank you for contributing to pretty-sitter! Your efforts help make the project better for everyone. 🚀

## Quick Reference

### Essential Commands

```bash
# Setup
git clone https://github.com/YOUR_USERNAME/pretty-sitter.git
cd pretty-sitter
pip install -e .[dev]

# Development
git checkout -b feature/my-feature
# Make changes
ruff check . && ruff format .
pytest
git commit -m "feat: add my feature"
git push origin feature/my-feature

# Maintenance
git fetch upstream
git rebase upstream/main
```

### Useful Links

- [Issues](https://github.com/antonioan/pretty-sitter/issues)
- [Pull Requests](https://github.com/antonioan/pretty-sitter/pulls)
- [Discussions](https://github.com/antonioan/pretty-sitter/discussions)
- [Project Board](https://github.com/antonioan/pretty-sitter/projects)
- [Releases](https://github.com/antonioan/pretty-sitter/releases)