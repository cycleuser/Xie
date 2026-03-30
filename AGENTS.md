# AGENTS.md - Xie Development Guide

## Project Overview

Xie is a Python CLI tool and library for converting Markdown to WeChat Public Account-compatible HTML. Python 3.8+ required.

**Version**: Defined in `xie/__init__.py` as `__version__` (single source of truth).

## Build/Lint/Test Commands

### Installation

```bash
# Basic install
pip install -e .

# With all dependencies (web, dev tools)
pip install -e .[all]

# Dev install (testing only)
pip install -e .[dev]
```

### Testing

```bash
# Run all tests
pytest

# Run with verbose output and short tracebacks (configured in pyproject.toml)
pytest -v --tb=short

# Run a single test file
pytest tests/test_core.py -v

# Run a single test class
pytest tests/test_core.py::TestConvertMarkdownToWechat -v

# Run a single test method
pytest tests/test_core.py::TestConvertMarkdownToWechat::test_convert_simple_text -v

# Run with coverage
pytest --cov=xie --cov-report=html
```

### Package Build

```bash
# Build distribution
python -m build

# Upload to PyPI (after configuring .pypirc)
python -m twine upload dist/*
```

## Code Style Guidelines

### General

- Python 3.8+ syntax only
- 4-space indentation (no tabs)
- Maximum line length: 100 characters (soft guideline)
- One statement per line

### Imports

Order imports in three blocks separated by blank lines:

1. Standard library (`re`, `dataclasses`, `typing`, `argparse`, etc.)
2. Third-party packages (`mistune`, `pygments`, `flask`)
3. Local project imports (`xie.core`, etc.)

```python
import re
from dataclasses import dataclass, field
from typing import Any, Optional, List

import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name

from xie.core import convert_markdown_to_wechat, ToolResult
```

### Type Hints

Use type hints for function parameters and return values:

```python
def convert_markdown_to_wechat(markdown_text: str, **kwargs) -> ToolResult:
    ...

def escape_html(text: str) -> str:
    ...
```

### Naming Conventions

- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`
- **Dataclass fields**: `snake_case`

```python
class WeChatRenderer:
    WECHAT_SAFE_TAGS = {...}  # class constant

    def render_link(self, link: str, text: str = None, ...) -> str:
        ...
```

### Dataclasses

Use `@dataclass` for data containers like `ToolResult`. Use `field(default_factory=...)` for mutable defaults:

```python
@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
```

### Docstrings

Use docstrings for all public functions and classes. Google style:

```python
def convert_markdown_to_wechat(markdown_text: str, **kwargs) -> ToolResult:
    """
    Convert Markdown text to WeChat Public Account compatible HTML.

    Args:
        markdown_text: Input markdown string
        **kwargs: Additional conversion options

    Returns:
        ToolResult with converted HTML and metadata
    """
```

### Error Handling

Use the `ToolResult` pattern for error handling in the API:

```python
def convert_markdown_to_wechat(markdown_text: str, **kwargs) -> ToolResult:
    try:
        if not isinstance(markdown_text, str):
            return ToolResult(success=False, error="Input must be a string")
        # ... processing ...
        return ToolResult(success=True, data={...}, metadata={...})
    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

For CLI, use `sys.exit(1)` on errors and print to `sys.stderr`:

```python
if not result.success:
    print(f"Error: {result.error}", file=sys.stderr)
    sys.exit(1)
```

### HTML Generation

- Use `html_escape()` from the `html` module to escape user content
- Use f-strings for HTML template composition
- WeChat link color: `#576b95`

### Project Structure

```
xie/
├── __init__.py       # Public API exports, __version__ (single source of truth)
├── __main__.py       # Entry point for python -m xie
├── core.py           # Core conversion logic, WeChatRenderer, ToolResult
├── api.py            # High-level Python API with convert() function
├── cli.py            # Command-line interface
├── app.py            # Flask web server
└── templates/        # Flask HTML templates
    └── index.html
tests/
├── __init__.py
├── conftest.py       # Pytest fixtures (sample_markdown, simple_markdown)
└── test_core.py      # All tests
images/
└── web.png           # Screenshot for README
```

### Public API (`__all__`)

Always define `__all__` in modules to explicitly declare public API:

```python
__all__ = [
    "convert_markdown_to_wechat",
    "create_wechat_html_document",
    "ToolResult",
    "escape_html",
    "clean_html_for_wechat",
    "__version__",
]
```

### Version Number

**Single source of truth**: `xie/__init__.py` contains `__version__ = "1.0.2"`.

To update the version:
1. Edit `xie/__init__.py` - change `__version__`
2. `pyproject.toml` version is for PyPI metadata only and may differ during development

### Testing Guidelines

- Group tests in classes: `TestConvertMarkdownToWechat`, `TestCreateWechatHtmlDocument`, etc.
- Use descriptive test method names: `test_convert_simple_text`, `test_convert_headings`
- Use fixtures from `conftest.py` for reusable test data
- Test both success and error paths
