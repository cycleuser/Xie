# Xie

Convert Markdown to WeChat-compatible HTML with a single command. Works as a CLI tool, Python library, GUI app, or web service.

## Why

If you write in Markdown and publish to WeChat, you know the pain of formatting. WeChat only accepts a limited subset of HTML, so most Markdown-to-HTML converters produce code that just won't paste correctly.

Xie handles this for you. It outputs clean, WeChat-compatible HTML with proper inline styles that paste directly into the WeChat editor.

## Quick Start

```bash
# Install
pip install xie

# Convert a file
xie input.md -o output.html

# Or pipe content
echo "# Hello" | xie
```

## Installation

```bash
# From PyPI
pip install xie

# With GUI and web support
pip install xie[all]

# From source
git clone https://github.com/cycleuser/xie.git
cd xie
pip install -e .
```

## Three Ways to Use

### CLI

```bash
# Basic conversion
xie article.md -o article.html

# With standalone document (includes title, author, styles)
xie article.md --standalone --title "My Post" --author "John" -o article.html

# Programmatic JSON output
xie article.md --json > result.json
```

### Python Library

```python
from xie import convert

result = convert("# Hello\n\nThis is **bold** text", standalone=True)
if result.success:
    print(result.html)
```

### GUI or Web

```bash
# Launch desktop GUI
xie gui

# Start web server
xie web --port 5000
```

The web interface opens at http://localhost:5000. Write Markdown on the left, see the WeChat preview on the right, and click "Copy for WeChat" to grab formatted HTML ready to paste.

## Features

Xie supports the standard Markdown things: headers, bold, italic, links, images, code blocks, tables, blockquotes, lists.

It also handles:

- **Syntax highlighting** for code blocks. Xie uses Pygments to highlight 100+ languages, with colors applied as inline styles (no external CSS).
- **LaTeX math** via `$inline$` and `$$block$$` syntax.
- **WeChat-specific styling** on links, images, and code blocks that matches WeChat's appearance.

## Supported Syntax

```
# Headers        **bold**       *italic*      ~~strikethrough~~
[links](url)    ![images](url)  `code`        ```language blocks
> quotes         - lists         1. lists      | tables |
$math$          $$block math$$
```

## WeChat Compatibility

WeChat doesn't accept arbitrary HTML. Xie only outputs tags and styles that WeChat allows:

- All styles are inline (no `<style>` tags or CSS classes)
- Link color defaults to WeChat blue (#576b95)
- Images scale responsively
- Code blocks use inline colors instead of external stylesheets

## Requirements

- Python 3.8+
- mistune for Markdown parsing
- Pygments for code highlighting

Optional: PySide6 for GUI, Flask for web server.

## License

GPLv3
