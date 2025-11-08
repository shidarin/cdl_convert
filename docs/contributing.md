# Contributing

We welcome contributions to CDL Convert! Whether you're fixing bugs, adding features, improving documentation, or submitting sample files, your help is appreciated.

## Contributing CDL and EDL Samples

Please, *please*, **please** submit samples of the following formats:

- FLEx
- ALE
- CMX
- CCC
- CDL

These are complex formats, and seeing real-world samples helps write tests that ensure correct parsing of real-world EDLs and CDLs. If you don't see a CDL format listed that you know exists, [open an issue](https://github.com/shidarin/cdl_convert/issues) asking for parse/write support for the format, and include a sample.

## Issues & Bugs

Take a look at the [issues page](https://github.com/shidarin/cdl_convert/issues) and if you see something you think you can tackle, leave a comment saying you're going to work on it. While many issues are already assigned to the principal authors, just because it's assigned doesn't mean work has begun.

Feel welcome to post:
- Bug reports
- Feature requests
- Questions about behavior
- Documentation improvements

## Development Workflow

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cdl_convert.git
   cd cdl_convert
   ```

3. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in development mode with Hatch for running tools:**
   ```bash
   pip install hatch
   pip install -e .[dev]
   ```

4. **Create a feature branch:**
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   ```

### Making Changes

**Branch naming conventions:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation improvements
- `test/` - Test additions or improvements

### Submitting Your Changes

1. **Push your feature branch to GitHub:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a pull request** from your feature branch to the `develop` branch of the main repository

3. **Link to related issues** in your pull request description using `Fixes #123` or `Relates to #456`

## Pull Request Guidelines

CDL Convert needs your collaboration, but we only have limited time to review and merge contributions. Following these guidelines will ensure your pull request is accepted and integrated quickly.

### Run the Tests!

Before you submit a pull request, please run the entire test suite and code quality checks:

```bash
# Run tests with coverage
hatch run test:cov

# Run linting
hatch run lint

# Run type checking
hatch run type-check

# Format code
hatch run format
```

If the tests are failing, it's likely that you accidentally broke something. Note which tests are failing and how your code might have affected them. If your change is intentional (for example, you changed behavior), adjust the test suite to match, get it back into a passing state, and then submit it.

**If your code fails the tests, it will be rejected.** GitHub Actions checks all pull requests automatically.

### Testing Across Python Versions

To test across all supported Python versions (3.11-3.14):

```bash
hatch run test:all
```

This uses Hatch's matrix testing to run tests in Python 3.11, 3.12, 3.13, and 3.14.

### Writing Tests

If your pull request adds a feature but lacks tests, **it will be rejected**.

Older tests are written using the standard unittest framework, but new tests
can be written using pytest and I'll try and keep up. Please keep test cases as simple as possible while maintaining good coverage of the code you added.

**Example test structure:**
```python
def test_my_new_feature():
    """Test that my new feature works correctly."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = my_new_feature(input_data)
    
    # Assert
    assert result.expected_value == "expected"
```

- Test files should be in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names that explain what is being tested
- Include docstrings in test functions
- Use fixtures for common test data

## Documentation Contributions

Documentation is just as important as code! We use Sphinx with MyST Parser for documentation, which means you can write in Markdown.

### Writing Documentation

1. **Documentation files are in `cdl_convert/docs/`**
2. **Use Markdown (`.md`) for new documentation**
3. **Follow MyST syntax for directives and cross-references**

### Building Documentation Locally

Using Hatch (recommended):

```bash
# Build documentation
hatch run docs:build

# Clean and rebuild
hatch run docs:rebuild

# Serve documentation locally (opens on http://localhost:8000)
hatch run docs:serve

# Check for broken links
hatch run docs:linkcheck
```

Or manually:

```bash
cd cdl_convert/docs
pip install -r requirements.txt
python -m sphinx -b html . _build/html
```

Then open `_build/html/index.html` in your browser.

### Documentation Style Guide

- Use clear, concise language
- Include code examples where appropriate
- Add cross-references to related classes and functions
- Test that all cross-references resolve correctly
- Verify documentation renders correctly on GitHub

## Code Style Guidelines

**If the code style doesn't follow PEP-8, it will be rejected.**

Use Hatch to check and format your code:
```bash
# Check code style
hatch run lint

# Auto-format code
hatch run format

# Run type checking
hatch run type-check
```

### Python Version

CDL Convert supports Python 3.11-3.14. Write code that works across these versions.

### Development Workflow with Hatch

CDL Convert uses [Hatch](https://hatch.pypa.io/) for modern Python project management. Hatch provides isolated environments for testing, linting, and documentation building.

**Available Hatch commands:**

```bash
# Testing
hatch run test              # Run tests in current Python version
hatch run test:all          # Run tests across all Python versions (3.11-3.14)
hatch run test:cov          # Run tests with coverage report

# Code Quality
hatch run lint              # Check code style with ruff
hatch run format            # Auto-format code with ruff
hatch run type-check        # Run mypy type checking
hatch run security:scan     # Run security checks with bandit

# Documentation
hatch run docs:build        # Build documentation
hatch run docs:rebuild      # Clean and rebuild documentation
hatch run docs:serve        # Serve documentation locally
hatch run docs:linkcheck    # Check for broken links
```

You don't need to activate a virtual environment when using Hatch - it manages environments automatically!

### Type Hints

Use type hints for function signatures:
```python
def parse_file(input_file: str) -> ColorCorrection | ColorCollection:
    """Parse a CDL file and return the appropriate object."""
    ...
```

### Docstrings

Use Google-style docstrings:
```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
    """
    ...
```

### Imports

Organize imports in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import os
from pathlib import Path

import opentimelineio as otio

from cdl_convert.base import AscColorSpaceBase
from cdl_convert.correction import ColorCorrection
```

## Copyright of Submitted Contributions

When submitting, you'll be asked to waive copyright to your submitted code to the listed authors. This is so we can keep a handle on the code and change the license for future releases if needed.

## Getting Help

If you have questions about contributing:
- Check the {doc}`faq` for common questions
- Open a [GitHub Discussion](https://github.com/shidarin/cdl_convert/discussions)
- Ask in your pull request or issue

## Code of Conduct

Be respectful and constructive in all interactions. We're all here to make CDL Convert better!

## Thank You!

Your contributions make CDL Convert better for everyone. Thank you for taking the time to contribute!
