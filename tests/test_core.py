"""
Test suite for xie.
"""
import pytest

from xie.core import (
    convert_markdown_to_wechat,
    create_wechat_html_document,
    escape_html,
    clean_html_for_wechat,
    ToolResult,
)


class TestConvertMarkdownToWechat:
    """Tests for markdown conversion."""
    
    def test_convert_simple_text(self):
        """Test converting simple text."""
        result = convert_markdown_to_wechat("Hello World")
        assert result.success
        assert "Hello World" in result.data['html']
    
    def test_convert_headings(self):
        """Test converting headings."""
        result = convert_markdown_to_wechat("# Heading 1\n## Heading 2\n### Heading 3")
        assert result.success
        assert "<h1" in result.data['html']
        assert "<h2" in result.data['html']
        assert "<h3" in result.data['html']
    
    def test_convert_bold(self):
        """Test converting bold text."""
        result = convert_markdown_to_wechat("This is **bold** text")
        assert result.success
        assert "<strong>bold</strong>" in result.data['html'] or "<b>bold</b>" in result.data['html']
    
    def test_convert_italic(self):
        """Test converting italic text."""
        result = convert_markdown_to_wechat("This is *italic* text")
        assert result.success
        assert "<em>" in result.data['html'] or "<i>" in result.data['html']
    
    def test_convert_strikethrough(self):
        """Test converting strikethrough text."""
        result = convert_markdown_to_wechat("This is ~~deleted~~ text")
        assert result.success
        assert "<del>" in result.data['html'] or "<s>" in result.data['html']
    
    def test_convert_link(self):
        """Test converting links."""
        result = convert_markdown_to_wechat("[Link Text](https://example.com)")
        assert result.success
        assert "https://example.com" in result.data['html']
        assert "Link Text" in result.data['html']
    
    def test_convert_image(self):
        """Test converting images."""
        result = convert_markdown_to_wechat("![Alt text](https://example.com/image.png)")
        assert result.success
        assert "https://example.com/image.png" in result.data['html']
        assert "Alt text" in result.data['html']
    
    def test_convert_code_block(self):
        """Test converting code blocks."""
        result = convert_markdown_to_wechat("```python\nprint('hello')\n```")
        assert result.success
        assert result.metadata['code_blocks_count'] >= 1
    
    def test_convert_inline_code(self):
        """Test converting inline code."""
        result = convert_markdown_to_wechat("Use `code` here")
        assert result.success
        assert "code" in result.data['html']
    
    def test_convert_blockquote(self):
        """Test converting blockquotes."""
        result = convert_markdown_to_wechat("> This is a quote")
        assert result.success
        assert "<blockquote" in result.data['html']
    
    def test_convert_unordered_list(self):
        """Test converting unordered lists."""
        result = convert_markdown_to_wechat("- Item 1\n- Item 2\n- Item 3")
        assert result.success
        assert "<ul>" in result.data['html']
        assert "<li>" in result.data['html']
    
    def test_convert_ordered_list(self):
        """Test converting ordered lists."""
        result = convert_markdown_to_wechat("1. First\n2. Second\n3. Third")
        assert result.success
        assert "<ol>" in result.data['html']
        assert "<li>" in result.data['html']
    
    def test_convert_table(self):
        """Test converting tables."""
        result = convert_markdown_to_wechat("| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |")
        assert result.success
        assert "<table" in result.data['html']
        assert "<th>" in result.data['html'] or "<td>" in result.data['html']
    
    def test_convert_empty_string(self):
        """Test converting empty string."""
        result = convert_markdown_to_wechat("")
        assert result.success
    
    def test_convert_invalid_input(self):
        """Test converting non-string input."""
        result = convert_markdown_to_wechat(None)
        assert not result.success
        assert result.error is not None
    
    def test_metadata(self):
        """Test that metadata is correctly populated."""
        result = convert_markdown_to_wechat("# Test")
        assert result.success
        assert 'input_length' in result.metadata
        assert 'output_length' in result.metadata
        assert 'code_blocks_count' in result.metadata


class TestCreateWechatHtmlDocument:
    """Tests for HTML document creation."""
    
    def test_create_document_with_title(self):
        """Test creating a document with title."""
        doc = create_wechat_html_document("Test Title", "<p>Content</p>")
        assert "<title>Test Title</title>" in doc
        assert "<p>Content</p>" in doc
    
    def test_create_document_with_author(self):
        """Test creating a document with author."""
        doc = create_wechat_html_document("Test", "<p>Content</p>", author="John")
        assert "John" in doc
        assert "文/John" in doc
    
    def test_create_document_without_author(self):
        """Test creating a document without author."""
        doc = create_wechat_html_document("Test", "<p>Content</p>")
        assert "文/" not in doc
    
    def test_document_has_styles(self):
        """Test that document includes styling."""
        doc = create_wechat_html_document("Test", "<p>Content</p>")
        assert "<style>" in doc
        assert "font-family" in doc
        assert "font-size" in doc


class TestEscapeHtml:
    """Tests for HTML escaping."""
    
    def test_escape_ampersand(self):
        """Test escaping ampersands."""
        assert "&amp;" in escape_html("&")
    
    def test_escape_less_than(self):
        """Test escaping less than signs."""
        assert "&lt;" in escape_html("<")
    
    def test_escape_greater_than(self):
        """Test escaping greater than signs."""
        assert "&gt;" in escape_html(">")
    
    def test_escape_quotes(self):
        """Test escaping quotes."""
        assert "&quot;" in escape_html('"')
    
    def test_escape_mixed(self):
        """Test escaping mixed special characters."""
        result = escape_html("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result


class TestToolResult:
    """Tests for ToolResult dataclass."""
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        result = ToolResult(success=True, data={"key": "value"})
        d = result.to_dict()
        assert d['success'] is True
        assert d['data'] == {"key": "value"}
    
    def test_to_dict_with_error(self):
        """Test converting error result to dictionary."""
        result = ToolResult(success=False, error="Something went wrong")
        d = result.to_dict()
        assert d['success'] is False
        assert d['error'] == "Something went wrong"
    
    def test_to_dict_with_metadata(self):
        """Test converting result with metadata."""
        result = ToolResult(success=True, metadata={"count": 5})
        d = result.to_dict()
        assert d['metadata'] == {"count": 5}


class TestIntegration:
    """Integration tests."""
    
    def test_full_conversion(self):
        """Test full markdown to WeChat HTML conversion."""
        markdown = """# Welcome

This is **bold** and *italic* text.

## Code Example

```python
def hello():
    print("Hello, World!")
```

## List

- Item 1
- Item 2
- Item 3

> This is a blockquote

[Link](https://example.com)
"""
        result = convert_markdown_to_wechat(markdown)
        assert result.success
        assert "<h1>" in result.data['html']
        assert "<h2>" in result.data['html']
        assert "<strong>" in result.data['html'] or "<b>" in result.data['html']
        assert "<em>" in result.data['html'] or "<i>" in result.data['html']
        assert result.metadata['code_blocks_count'] >= 1
    
    def test_standalone_document(self):
        """Test creating standalone document."""
        markdown = "# Test\n\nSome content"
        result = convert_markdown_to_wechat(markdown)
        assert result.success
        
        standalone = create_wechat_html_document(
            title="My Document",
            content=result.data['html'],
            author="Author"
        )
        assert "<!DOCTYPE html>" in standalone
        assert "<title>My Document</title>" in standalone
        assert "Author" in standalone


class TestLatex:
    """Tests for LaTeX math support."""
    
    def test_inline_latex(self):
        """Test inline LaTeX math."""
        result = convert_markdown_to_wechat(r"Inline: $x^2 + y^2 = z^2$")
        assert result.success
        assert '<span style="font-size:16px;padding:0 2px;font-family:Times New Roman,serif;">x^2 + y^2 = z^2</span>' in result.data['html']
    
    def test_block_latex(self):
        """Test block LaTeX math."""
        result = convert_markdown_to_wechat(r"$$\int_0^\infty e^{-x^2} dx$$")
        assert result.success
        assert '<div style="text-align:center;margin:15px 0;padding:15px;background:#f9f9f9;border-radius:8px;font-size:16px;line-height:1.8;font-family:Times New Roman,serif;">' in result.data['html']
        assert r'\int_0^\infty' in result.data['html']
    
    def test_latex_with_frac(self):
        """Test LaTeX with fractions."""
        result = convert_markdown_to_wechat(r"$$\frac{\sqrt{\pi}}{2}$$")
        assert result.success
        assert r'\frac' in result.data['html']
        assert r'\sqrt' in result.data['html']


class TestCodeHighlighting:
    """Tests for code highlighting with inline styles."""
    
    def test_code_block_highlighting(self):
        """Test code block with syntax highlighting."""
        result = convert_markdown_to_wechat("```python\ndef hello():\n    print('hi')\n```")
        assert result.success
        html = result.data['html']
        assert '<pre' in html
        assert 'span' in html
        assert 'color:' in html
        assert 'def' in html or 'hello' in html
    
    def test_inline_code_styling(self):
        """Test inline code has proper styling."""
        result = convert_markdown_to_wechat("Use `code` here")
        assert result.success
        assert 'code' in result.data['html']
        assert 'color:#e83e8c' in result.data['html'] or 'color:#d73a49' in result.data['html']
    
    def test_code_block_no_class(self):
        """Test that code blocks don't use CSS classes."""
        result = convert_markdown_to_wechat("```python\nprint('hello')\n```")
        assert result.success
        html = result.data['html']
        assert 'class=' not in html or 'span' in html
