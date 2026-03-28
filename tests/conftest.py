"""
Pytest configuration and fixtures.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_markdown():
    """Sample markdown for testing."""
    return """# Heading 1

This is a paragraph with **bold** and *italic* text.

## Heading 2

- List item 1
- List item 2
- List item 3

```python
def hello():
    print("Hello, World!")
```

> This is a blockquote

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

[Link](https://example.com)
"""


@pytest.fixture
def simple_markdown():
    """Simple markdown for quick tests."""
    return "Hello **World**"
