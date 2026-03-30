# Xie

Convert Markdown to WeChat-compatible HTML with a single command. Works as a CLI tool, Python library, or web service.

**Xie** (写) means "to write" in Chinese.

## Why

If you write in Markdown and publish to WeChat, you know the pain of formatting. WeChat only accepts a limited subset of HTML, so most Markdown-to-HTML converters produce code that just won't paste correctly.

Xie handles this for you. It outputs clean, WeChat-compatible HTML with proper inline styles that paste directly into the WeChat editor.

## Quick Start

```bash
# Install
pip install xie

# Convert a file
xie convert test.md -o test.html

# Or pipe content
echo "# Hello" | xie
```

## Installation

```bash
# From PyPI
pip install xie

# With web support
pip install xie[all]

# From source
git clone https://github.com/cycleuser/xie.git
cd xie
pip install -e .
```

## Usage

### CLI

```bash
# Basic conversion
xie convert test.md -o test.html

# With standalone document (includes title, author, styles)
xie convert test.md --standalone --title "My Post" --author "John" -o test.html

# JSON output
xie convert test.md --json
```

### Python Library

```python
from xie import convert_markdown_to_wechat

result = convert_markdown_to_wechat("# Hello\n\nThis is **bold** text")
if result.success:
    print(result.data['html'])
```

### Web Service

```bash
# Start web server
xie web --port 5000
```

Open http://localhost:5000 in your browser. Write Markdown on the left, see the WeChat preview on the right, and click "Copy" to grab formatted HTML ready to paste.

![Web Interface](images/web.png)

## Features

- **Full Markdown support**: headers, bold, italic, links, images, code blocks, tables, blockquotes, lists
- **Syntax highlighting** for code blocks with 100+ languages (Pygments)
- **LaTeX math** via `$inline$` and `$$block$$` syntax
- **WeChat-compatible output**: all styles inline, no external CSS

## Supported Syntax

```
# Headers        **bold**       *italic*      ~~strikethrough~~
[links](url)    ![images](url)  `code`        ```language blocks
> quotes         - lists         1. lists      | tables |
$math$          $$block math$$
```

## Example

Input (`test.md`):

```markdown
# 一级标题

## 二级标题

**加粗**

* 分点1
* 分点2

> 引用

$$
\Sigma_e^t= \frac{1}{2}
$$

```python
print("hello")
```
```

Output: WeChat-compatible HTML with inline styles.

## Requirements

- Python 3.8+
- mistune (Markdown parsing)
- Pygments (code highlighting)
- Flask (optional, for web server)

## License

GPLv3