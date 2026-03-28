"""
Core conversion module for Markdown to WeChat Public Account HTML.
"""
import re
from dataclasses import dataclass, field
from typing import Any, Optional, List
from html import escape as html_escape

import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter


@dataclass
class ToolResult:
    """Unified result type for all API functions."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }


class WeChatRenderer(mistune.HTMLRenderer):
    """Renderer that produces WeChat-compatible HTML from Markdown."""
    
    WECHAT_SAFE_TAGS = {
        'section', 'header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'strong', 'b', 'em', 'i', 'u', 's', 'strike', 'del',
        'p', 'br', 'span', 'a', 'img', 'blockquote', 'pre', 'code',
        'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'ruby', 'rt', 'sup', 'sub'
    }
    
    def __init__(self):
        super().__init__()
        self._code_blocks: List[str] = []
    
    def block_code(self, code: str, info: str = None, **attrs) -> str:
        """Render code block with syntax highlighting."""
        lang = None
        if info:
            lang = info.split()[0] if info else None
        
        if lang and lang not in ('plain', 'text', 'none', ''):
            try:
                lexer = get_lexer_by_name(lang)
            except:
                lexer = TextLexer()
        else:
            lexer = TextLexer()
        
        try:
            formatter = HtmlFormatter(
                cssclass='highlight',
                nowrap=True,
                linenos=False
            )
            highlighted = highlight(code, lexer, formatter)
        except:
            highlighted = f'<code>{html_escape(code)}</code>'
        
        highlighted = highlighted.strip()
        uid = f'code-{len(self._code_blocks)}'
        self._code_blocks.append(highlighted)
        
        placeholder = f'<code class="code-block" data-id="{uid}">{html_escape(code[:50])}...</code>'
        return f'<pre>{placeholder}</pre>\n'
    
    def render_image(self, src: str, alt: str = '', title: str = None, **attrs) -> str:
        """Render image with WeChat-compatible attributes."""
        alt_attr = f' alt="{html_escape(alt)}"' if alt else ''
        title_attr = f' title="{html_escape(title)}"' if title else ''
        return f'<img src="{html_escape(src)}"{alt_attr}{title_attr} style="max-width:100%;height:auto;"/>\n'
    
    def render_link(self, link: str, text: str = None, title: str = None, **attrs) -> str:
        """Render link with WeChat-compatible format."""
        text = text or link
        title_attr = f' title="{html_escape(title)}"' if title else ''
        return f'<a href="{html_escape(link)}"{title_attr} style="color:#576b95;">{text}</a>'
    
    def render_quote(self, text: str, **attrs) -> str:
        """Render blockquote with WeChat styling."""
        return f'<blockquote style="border-left:3px solid #e5e5e5;padding:5px 10px;margin:10px 0;color:#666;">{text}</blockquote>\n'
    
    def render_table(self, text: str, head: str = None, **attrs) -> str:
        """Render table with WeChat-compatible styling."""
        return (
            f'<table style="border-collapse:collapse;width:100%;margin:10px 0;">'
            f'{head or ""}{text}'
            f'</table>\n'
        )
    
    def render_table_head(self, text: str, **attrs) -> str:
        """Render table head."""
        return f'<thead>{text}</thead>\n'
    
    def render_table_body(self, text: str, **attrs) -> str:
        """Render table body."""
        return f'<tbody>{text}</tbody>\n'
    
    def render_table_row(self, text: str, **attrs) -> str:
        """Render table row."""
        return f'<tr>{text}</tr>\n'
    
    def render_table_cell(self, text: str, head: bool = False, **attrs) -> str:
        """Render table cell with borders."""
        tag = 'th' if head else 'td'
        align = attrs.get('align')
        align_style = f' text-align:{align};' if align else ''
        border_style = f'border:1px solid #e5e5e5;padding:8px;{align_style}'
        return f'<{tag} style="{border_style}">{text}</{tag}>\n'
    
    def render_heading(self, text: str, level: int, **attrs) -> str:
        """Render heading with WeChat-compatible styling."""
        sizes = {1: '24px', 2: '22px', 3: '20px', 4: '18px', 5: '16px', 6: '15px'}
        size = sizes.get(level, '16px')
        margin = f'margin:{20-level*2}px 0 10px;'
        return f'<h{level} style="{margin}font-size:{size};font-weight:bold;">{text}</h{level}>\n'
    
    def render_paragraph(self, text: str, **attrs) -> str:
        """Render paragraph."""
        return f'<p style="margin:10px 0;line-height:1.8;">{text}</p>\n'
    
    def render_list(self, text: str, ordered: bool = False, **attrs) -> str:
        """Render list with WeChat-compatible styling."""
        tag = 'ol' if ordered else 'ul'
        return f'<{tag} style="margin:10px 0;padding-left:20px;">{text}</{tag}>\n'
    
    def render_list_item(self, text: str, **attrs) -> str:
        """Render list item."""
        return f'<li style="margin:5px 0 5px 20px;">{text}</li>\n'
    
    def get_code_blocks(self) -> List[str]:
        """Get all code blocks for separate rendering."""
        return self._code_blocks.copy()
    
    def reset(self):
        """Reset internal state."""
        self._code_blocks = []


def convert_markdown_to_wechat(markdown_text: str, **kwargs) -> ToolResult:
    """
    Convert Markdown text to WeChat Public Account compatible HTML.
    
    Args:
        markdown_text: Input markdown string
        **kwargs: Additional conversion options
        
    Returns:
        ToolResult with converted HTML and metadata
    """
    try:
        if not isinstance(markdown_text, str):
            return ToolResult(
                success=False,
                error="Input must be a string"
            )
        
        renderer = WeChatRenderer()
        md = mistune.create_markdown(
            renderer=renderer,
            plugins=['strikethrough', 'table']
        )
        
        html = md(markdown_text)
        
        code_blocks = renderer.get_code_blocks()
        
        metadata = {
            'code_blocks_count': len(code_blocks),
            'input_length': len(markdown_text),
            'output_length': len(html),
        }
        
        return ToolResult(
            success=True,
            data={
                'html': html,
                'code_blocks': code_blocks,
            },
            metadata=metadata
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            error=str(e)
        )


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return html_escape(text)


def clean_html_for_wechat(html: str) -> str:
    """
    Clean HTML to be WeChat-compatible.
    Removes unsupported tags and attributes.
    """
    allowed_tags = WeChatRenderer.WECHAT_SAFE_TAGS
    
    def replace_tag(match):
        tag = match.group(1)
        attrs = match.group(2) or ''
        if tag.lower() in allowed_tags:
            if tag.lower() == 'img':
                safe_attrs = re.sub(r'src="[^"]*"', '', attrs)
                safe_attrs = re.sub(r'alt="[^"]*"', '', safe_attrs)
                return f'<{tag} {safe_attrs}src=...>'
            return match.group(0)
        return ''
    
    cleaned = re.sub(r'<(\w+)\s*([^>]*)>', replace_tag, html)
    
    cleaned = re.sub(r'<(\w+)[^>]*>(.*?)</\1>', 
                     lambda m: f'<{m.group(1)}>{m.group(2)}</{m.group(1)}>' 
                     if m.group(1).lower() in allowed_tags else m.group(2),
                     html, flags=re.DOTALL)
    
    return cleaned


def create_wechat_html_document(title: str, content: str, author: str = None) -> str:
    """
    Create a complete WeChat-compatible HTML document.
    
    Args:
        title: Document title
        content: HTML content body
        author: Optional author name
        
    Returns:
        Complete HTML document string
    """
    author_html = f'<p style="text-align:right;color:#999;font-size:14px;">文/{author or "Anonymous"}</p>' if author else ''
    
    doc = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(title)}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.8;
            color: #333;
            max-width: 100%;
            padding: 10px;
            margin: 0 auto;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-weight: bold;
            line-height: 1.3;
            margin: 20px 0 10px;
        }}
        h1 {{ font-size: 24px; }}
        h2 {{ font-size: 22px; }}
        h3 {{ font-size: 20px; }}
        h4 {{ font-size: 18px; }}
        h5 {{ font-size: 16px; }}
        h6 {{ font-size: 15px; }}
        p {{ margin: 10px 0; }}
        a {{ color: #576b95; text-decoration: none; }}
        img {{ max-width: 100%; height: auto; display: block; margin: 10px 0; }}
        blockquote {{
            border-left: 3px solid #e5e5e5;
            padding: 5px 10px;
            margin: 10px 0;
            color: #666;
            background: #f9f9f9;
        }}
        pre {{
            background: #f6f8fa;
            border-radius: 4px;
            padding: 10px;
            overflow-x: auto;
            margin: 10px 0;
        }}
        code {{
            background: #f6f8fa;
            padding: 2px 4px;
            border-radius: 2px;
            font-family: "SF Mono", Consolas, Monaco, monospace;
            font-size: 14px;
        }}
        .code-block {{
            background: #f6f8fa;
            border-radius: 4px;
            padding: 10px;
            overflow-x: auto;
            margin: 10px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }}
        th, td {{
            border: 1px solid #e5e5e5;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background: #f6f8fa;
        }}
        ul, ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e5e5e5;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1 style="text-align:center;">{escape_html(title)}</h1>
    {author_html}
    <div class="content">
        {content}
    </div>
</body>
</html>'''
    
    return doc
