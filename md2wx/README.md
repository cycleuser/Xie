# Markdown to WeChat HTML Converter

A command-line tool and Python library for converting Markdown documents to WeChat Public Account (公众号) compatible HTML.

## Project Background

Markdown has become the de facto standard for technical documentation and content creation due to its simple syntax and readability. However, WeChat Public Account only supports a limited subset of HTML for formatting articles. This creates a friction point for content creators who write in Markdown but need to publish on WeChat.

MD2WX solves this problem by providing a robust conversion pipeline that transforms standard Markdown into WeChat-compatible HTML. The tool handles the various complexities of WeChat's HTML restrictions, including supported tags, CSS constraints, and code block rendering.

This project addresses the practical need for content creators, developers, and technical writers who maintain their content in Markdown format but need to publish on WeChat Public Accounts. By automating the conversion process, MD2WX saves significant manual effort and ensures consistent formatting across platforms.

## Application Scenarios

**Technical Documentation Publishing**: Developers who write API documentation, tutorials, or technical blog posts in Markdown can now easily publish them to WeChat without manual HTML conversion.

**Educational Content Creation**: Teachers and educators who create course materials in Markdown can distribute them through WeChat Public Accounts with proper formatting.

**Software Product Announcements**: Product teams can maintain release notes and announcements in Markdown and publish them directly to WeChat with a single command.

**Cross-Platform Content Distribution**: Content creators who publish to multiple platforms (blogs, Medium, GitHub) can use the same Markdown source for WeChat articles.

## Hardware Compatibility

MD2WX is a lightweight Python application with minimal hardware requirements:

- **CPU**: Any modern x86_64 or ARM64 processor
- **Memory**: Minimum 256MB RAM; 512MB recommended
- **Storage**: Less than 50MB for installation
- **No GPU required**: All processing is CPU-based

## Operating Systems

MD2WX supports all major operating systems:

- **macOS**: macOS 10.13 (High Sierra) or later
- **Linux**: Ubuntu 18.04+, Debian 10+, Fedora 30+, and most other Linux distributions with Python 3.8+
- **Windows**: Windows 10 or later with WSL2 or native Python

## Dependencies

MD2WX requires Python 3.8 or higher. Core dependencies include:

- **Python**: >= 3.8
- **mistune**: >= 2.0.0 (Markdown parser)
- **Pygments**: >= 2.14.0 (Syntax highlighting for code blocks)

Optional dependencies:

- **PySide6**: >= 6.4.0 (For GUI interface)
- **Flask**: >= 2.3.0 (For web interface)
- **pytest**: >= 7.0.0 (For testing)

## Installation

### From PyPI (Recommended)

```bash
pip install md2wx
```

### From Source

```bash
git clone https://github.com/cycleuser/md2wx.git
cd md2wx
pip install -e .
```

### With All Dependencies

```bash
pip install md2wx[all]
```

### Development Installation

```bash
git clone https://github.com/cycleuser/md2wx.git
cd md2wx
pip install -e .[dev]
```

## Usage

### Command-Line Interface

Convert a markdown file:

```bash
md2wx input.md -o output.html
```

Convert from stdin:

```bash
echo "# Hello World" | md2wx
```

Create standalone HTML with styles:

```bash
md2wx input.md --standalone --title "My Article" --author "John" -o output.html
```

Get JSON output for programmatic use:

```bash
md2wx input.md --json
```

Verbose mode:

```bash
md2wx -v input.md -o output.html
```

### Python API

```python
from md2wx import convert

result = convert("# Hello\n\nThis is **bold** text", standalone=True)

if result.success:
    print(result.html)
else:
    print(f"Error: {result.error}")
```

### GUI Mode

Launch the graphical interface:

```bash
md2wx gui
```

### Web Server Mode

Start the web interface:

```bash
md2wx web --host 0.0.0.0 --port 5000
```

Then open http://localhost:5000 in your browser.

## Screenshots

| GUI Interface | Web Interface |
|:-------------:|:-------------:|
| ![GUI](images/gui_placeholder.png) | ![Web](images/web_placeholder.png) |

## CLI Help

```
usage: md2wx [-h] [-V] [-v] [-o OUTPUT] [--json] [-q] [--title TITLE]
             [--author AUTHOR] [--standalone]
             [input]

Convert Markdown to WeChat Public Account HTML

positional arguments:
  input                 Input markdown file or markdown text

optional arguments:
  -h, --help           show this help message and exit
  -V, --version        show program's version number and exit
  -v, --verbose        Verbose output
  -o, --output         Output file path
  --json               Output as JSON
  -q, --quiet          Suppress output
  --title              Document title (default: 'Untitled')
  --author             Document author
  --standalone         Create standalone HTML document with styles
```

## Supported Markdown Features

- Headers (h1-h6)
- Bold, italic, underline, strikethrough
- Links with proper WeChat styling
- Images with responsive sizing
- Code blocks with syntax highlighting
- Inline code
- Blockquotes with WeChat-compatible styling
- Ordered and unordered lists
- Tables with proper borders
- Horizontal rules

## WeChat Compatibility Notes

MD2WX generates HTML that complies with WeChat's content guidelines:

- Uses only supported HTML tags
- Applies WeChat-compatible inline styles
- Ensures images have responsive width
- Formats code blocks for readability
- Uses proper link colors (#576b95)

## License

GPLv3. See [LICENSE](LICENSE) for details.
