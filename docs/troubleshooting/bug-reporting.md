# Bug Reporting and Feature Requests

This guide explains how to effectively report bugs and request new features for pretty-sitter. Following these guidelines helps maintainers understand and address issues quickly.

## Before Reporting

### Check Existing Issues

Before creating a new issue, please:

1. **Search existing issues** on the [GitHub issue tracker](https://github.com/antonioan/pretty-sitter/issues)
2. **Check the FAQ** and troubleshooting documentation
3. **Try the latest version** to see if the issue has been fixed

### Determine Issue Type

Choose the appropriate issue type:

- **Bug Report**: Something is broken or not working as expected
- **Feature Request**: Requesting new functionality or improvements
- **Documentation**: Issues with documentation or examples
- **Question**: General usage questions (consider FAQ first)

## Bug Reports

### Required Information

Every bug report should include:

#### 1. Environment Details
```
- Python version: (e.g., 3.11.5)
- pretty-sitter version: (e.g., 0.0.1)
- Operating system: (e.g., macOS 13.5, Ubuntu 22.04, Windows 11)
- Terminal: (e.g., iTerm2, GNOME Terminal, Windows Terminal)
- TERM environment variable: (output of `echo $TERM`)
```

#### 2. Minimal Reproduction Example

Provide the smallest possible code example that demonstrates the issue:

```python
from tree_sitter import Language, Parser
import tree_sitter_python
from pretty_sitter import PrettySitter

# Set up parser
language = Language(tree_sitter_python.language())
parser = Parser()
parser.set_language(language)

# Minimal code that triggers the issue
code = "def test(): pass"
tree = parser.parse(bytes(code, "utf8"))

# Configuration that causes the problem
ps = PrettySitter()  # Include any specific config here
ps.pprint(tree.root_node)

# Expected: [describe what should happen]
# Actual: [describe what actually happens]
```

#### 3. Expected vs Actual Behavior

Clearly describe:
- **What you expected to happen**
- **What actually happened**
- **Any error messages** (include full stack traces)

#### 4. Steps to Reproduce

Provide step-by-step instructions:
1. Install pretty-sitter version X.X.X
2. Run the provided code example
3. Observe the incorrect behavior

### Bug Report Template

```markdown
## Bug Description
[Brief description of the issue]

## Environment
- Python version: 
- pretty-sitter version: 
- Operating system: 
- Terminal: 
- TERM variable: 

## Reproduction Code
```python
# Minimal example here
```

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Error Messages
```
[Full error messages and stack traces]
```

## Additional Context
[Any other relevant information]
```

### Common Bug Categories

#### Installation Issues
- Include pip/conda version
- Show full installation command and output
- Include any error messages during installation

#### Display/Terminal Issues
- Include terminal screenshots if helpful
- Test with colors disabled: `UIConfig(print_with_color=False)`
- Include output of color test: `echo -e "\033[31mRed\033[0m"`

#### Performance Issues
- Include file size and complexity metrics
- Provide timing information if possible
- Test with minimal configuration

#### Configuration Issues
- Show complete configuration objects
- Test with default configuration
- Include debug output: `DebugConfig(debug=True)`

## Feature Requests

### Before Requesting

Consider:
- **Is this a common use case?** Will other users benefit?
- **Can it be achieved with existing features?** Check configuration options
- **Is it within scope?** pretty-sitter focuses on parse tree visualization

### Feature Request Template

```markdown
## Feature Description
[Clear description of the proposed feature]

## Use Case
[Explain why this feature would be useful]

## Proposed Solution
[Describe how you envision this working]

## Alternatives Considered
[Other approaches you've considered]

## Examples
[Code examples showing how the feature would be used]

## Additional Context
[Any other relevant information]
```

### Types of Feature Requests

#### New Configuration Options
- Explain the visual or functional impact
- Provide examples of when it would be useful
- Consider backward compatibility

#### New Output Formats
- Describe the target format (JSON, XML, etc.)
- Explain the use case for this format
- Consider existing export options

#### Performance Improvements
- Provide benchmarks or profiling data
- Describe the specific performance bottleneck
- Include test cases for measuring improvement

#### Integration Features
- Describe the target integration (IDE, tool, etc.)
- Explain the expected workflow
- Consider existing integration patterns

## Issue Labels and Priority

Issues are typically labeled with:

- **Type**: `bug`, `enhancement`, `documentation`, `question`
- **Priority**: `high`, `medium`, `low`
- **Component**: `config`, `display`, `performance`, `integration`
- **Status**: `needs-info`, `confirmed`, `in-progress`, `blocked`

### Priority Guidelines

**High Priority**:
- Security vulnerabilities
- Data corruption or loss
- Complete feature breakage
- Installation failures

**Medium Priority**:
- Partial feature breakage
- Performance regressions
- Usability issues
- Documentation errors

**Low Priority**:
- Minor visual issues
- Enhancement requests
- Edge case bugs
- Optimization opportunities

## Response Expectations

### Bug Reports
- **Acknowledgment**: Within 1-2 business days
- **Initial triage**: Within 1 week
- **Resolution timeline**: Depends on severity and complexity

### Feature Requests
- **Acknowledgment**: Within 1-2 business days
- **Design discussion**: May take several weeks
- **Implementation**: Depends on scope and maintainer availability

### Questions
- **Response**: Within 1-2 business days
- **Resolution**: Usually same day if information is complete

## Contributing Fixes

If you can fix the bug yourself:

1. **Fork the repository**
2. **Create a feature branch**
3. **Write tests** for your fix
4. **Submit a pull request**
5. **Reference the issue** in your PR description

See our [contributing guidelines](../contributing/development-setup.md) for detailed instructions.

## Security Issues

For security-related issues:

1. **Do not create public issues**
2. **Email maintainers directly** at [security contact]
3. **Include full details** but keep them private
4. **Allow time for fix** before public disclosure

## Getting Help

If you're unsure about reporting:

- **Start with a question** in discussions or issues
- **Ask in the community** (if applicable)
- **Check the FAQ** for common questions
- **Review troubleshooting docs** for known issues

## Quality Guidelines

### Good Bug Reports
- Include all required information
- Provide minimal reproduction cases
- Use clear, descriptive titles
- Follow the template format
- Test with latest version

### Good Feature Requests
- Explain the problem being solved
- Provide concrete use cases
- Consider implementation complexity
- Include code examples
- Research existing solutions

### What to Avoid
- Duplicate reports without checking existing issues
- Vague descriptions like "it doesn't work"
- Missing reproduction steps
- Demanding immediate fixes
- Off-topic discussions in issue comments

## Example Reports

### Good Bug Report
```markdown
Title: "Colors not displayed in Windows Terminal with TERM=xterm"

## Bug Description
ANSI color codes appear as literal text instead of colors when using 
Windows Terminal with TERM=xterm environment variable.

## Environment
- Python version: 3.11.5
- pretty-sitter version: 0.0.1
- Operating system: Windows 11
- Terminal: Windows Terminal 1.18.2681.0
- TERM variable: xterm

## Reproduction Code
```python
from tree_sitter import Language, Parser
import tree_sitter_python
from pretty_sitter import PrettySitter

language = Language(tree_sitter_python.language())
parser = Parser()
parser.set_language(language)
tree = parser.parse(b"def test(): pass")

ps = PrettySitter()
ps.pprint(tree.root_node)
```

## Expected Behavior
Node types should appear in blue color, text content in cyan.

## Actual Behavior
Output shows literal ANSI codes: `\033[94mdef\033[0m` instead of colored text.

## Additional Context
- Colors work correctly in PowerShell with TERM=xterm-256color
- Issue only occurs with TERM=xterm specifically
- Windows Terminal supports 256 colors
```

### Good Feature Request
```markdown
Title: "Add JSON export option for parse trees"

## Feature Description
Add ability to export parse tree structure as JSON format for integration 
with other tools and analysis pipelines.

## Use Case
I'm building a code analysis tool that needs to process parse tree data 
programmatically. Currently I have to parse the pretty-printed output, 
which is error-prone and inefficient.

## Proposed Solution
Add a new method `to_json()` or configuration option that outputs structured 
JSON instead of formatted text:

```python
ps = PrettySitter(OutputConfig(format='json'))
json_output = ps.to_json(tree.root_node)
```

## Examples
```json
{
  "type": "module",
  "start": [0, 0],
  "end": [1, 0],
  "children": [
    {
      "type": "function_definition",
      "start": [0, 0],
      "end": [0, 17],
      "text": "def test(): pass"
    }
  ]
}
```

## Additional Context
This would complement the existing pretty-printing functionality and 
enable programmatic analysis workflows.
```

Remember: Good issue reports lead to faster resolutions and better software for everyone!