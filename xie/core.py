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
from pygments.token import (
    Keyword, Name, Comment, String, Error, Number, Operator, Generic,
    Token, Whitespace, Punctuation
)


WECHAT_SAFE_TAGS = {
    'section', 'header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'b', 'em', 'i', 'u', 's', 'strike', 'del',
    'p', 'br', 'span', 'a', 'img', 'blockquote', 'pre', 'code',
    'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'ruby', 'rt', 'sup', 'sub', 'section'
}


PYGMENTS_STYLES = {
    Keyword: 'color:#d73a49;font-weight:bold;',
    Keyword.Constant: 'color:#005cc5;',
    Keyword.Declaration: 'color:#6f42c1;',
    Keyword.Namespace: 'color:#e36209;',
    Keyword.Pseudo: 'color:#e36209;',
    Keyword.Reserved: 'color:#6f42c1;',
    Keyword.Type: 'color:#005cc5;',
    Name: 'color:#24292e;',
    Name.Attribute: 'color:#6f42c1;',
    Name.Builtin: 'color:#005cc5;',
    Name.Builtin.Pseudo: 'color:#005cc5;',
    Name.Class: 'color:#6f42c1;',
    Name.Constant: 'color:#005cc5;',
    Name.Decorator: 'color:#6f42c1;',
    Name.Entity: 'color:#6f42c1;',
    Name.Exception: 'color:#e36209;',
    Name.Function: 'color:#6f42c1;',
    Name.Property: 'color:#24292e;',
    Name.Label: 'color:#24292e;',
    Name.Namespace: 'color:#24292e;',
    Name.Other: 'color:#24292e;',
    Name.Tag: 'color:#22863a;',
    Name.Variable: 'color:#e36209;',
    Name.Variable.Class: 'color:#6f42c1;',
    Name.Variable.Global: 'color:#e36209;',
    Name.Variable.Instance: 'color:#e36209;',
    Number: 'color:#005cc5;',
    Number.Float: 'color:#005cc5;',
    Number.Hex: 'color:#005cc5;',
    Number.Integer: 'color:#005cc5;',
    Number.Integer.Long: 'color:#005cc5;',
    Number.Oct: 'color:#005cc5;',
    Operator: 'color:#d73a49;',
    Operator.Word: 'color:#d73a49;',
    Punctuation: 'color:#24292e;',
    String: 'color:#032f62;',
    String.Affix: 'color:#032f62;',
    String.Backtick: 'color:#032f62;',
    String.Char: 'color:#032f62;',
    String.Delimiter: 'color:#24292e;',
    String.Doc: 'color:#6a737d;',
    String.Double: 'color:#032f62;',
    String.Escape: 'color:#e36209;',
    String.Heredoc: 'color:#032f62;',
    String.Interpol: 'color:#032f62;',
    String.Other: 'color:#032f62;',
    String.Regex: 'color:#032f62;',
    String.Single: 'color:#032f62;',
    String.Symbol: 'color:#032f62;',
    Comment: 'color:#6a737d;font-style:italic;',
    Comment.Multiline: 'color:#6a737d;font-style:italic;',
    Comment.Preproc: 'color:#6a737d;',
    Comment.PreprocFile: 'color:#6a737d;',
    Comment.Single: 'color:#6a737d;font-style:italic;',
    Comment.Special: 'color:#6a737d;font-style:italic;',
    Generic: 'color:#24292e;',
    Generic.Deleted: 'color:#b31d28;',
    Generic.Emph: 'font-style:italic;',
    Generic.Error: 'color:#b31d28;',
    Generic.Heading: 'font-weight:bold;',
    Generic.Inserted: 'color:#22863a;',
    Generic.Output: 'color:#24292e;',
    Generic.Prompt: 'color:#005cc5;',
    Generic.Strong: 'font-weight:bold;',
    Generic.Subheading: 'font-weight:bold;',
    Generic.Traceback: 'color:#b31d28;',
    Error: 'color:#b31d28;',
    Token: 'color:#24292e;',
    Whitespace: 'color:#24292e;',
}


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


def get_inline_style_for_token(token_type):
    """Get inline style for a Pygments token type."""
    while token_type:
        if token_type in PYGMENTS_STYLES:
            return PYGMENTS_STYLES[token_type]
        token_type = token_type.parent
    return 'color:#24292e;'


PYGMENTS_ABBREV_MAP = {
    'k': 'Keyword',
    'kc': 'Keyword.Constant',
    'kd': 'Keyword.Declaration',
    'kn': 'Keyword.Namespace',
    'kp': 'Keyword.Pseudo',
    'kr': 'Keyword.Reserved',
    'kt': 'Keyword.Type',
    'n': 'Name',
    'na': 'Name.Attribute',
    'nb': 'Name.Builtin',
    'bp': 'Name.Builtin.Pseudo',
    'nc': 'Name.Class',
    'no': 'Name.Constant',
    'nd': 'Name.Decorator',
    'ni': 'Name.Entity',
    'ne': 'Name.Exception',
    'nf': 'Name.Function',
    'py': 'Name.Property',
    'nl': 'Name.Label',
    'nn': 'Name.Namespace',
    'nx': 'Name.Other',
    'nt': 'Name.Tag',
    'nv': 'Name.Variable',
    'vc': 'Name.Variable.Class',
    'vg': 'Name.Variable.Global',
    'vi': 'Name.Variable.Instance',
    'o': 'Operator',
    'ow': 'Operator.Word',
    'p': 'Punctuation',
    's': 'String',
    'sa': 'String.Affix',
    'sb': 'String.Backtick',
    'sc': 'String.Char',
    'dl': 'String.Delimiter',
    'sd': 'String.Doc',
    'se': 'String.Escape',
    'sh': 'String.Heredoc',
    'si': 'String.Interpol',
    'sx': 'String.Other',
    'sr': 'String.Regex',
    's1': 'String.Single',
    's2': 'String.Double',
    'ss': 'String.Symbol',
    'm': 'Number',
    'mf': 'Number.Float',
    'mh': 'Number.Hex',
    'mi': 'Number.Integer',
    'il': 'Number.Integer.Long',
    'mo': 'Number.Oct',
    'c': 'Comment',
    'cm': 'Comment.Multiline',
    'cp': 'Comment.Preproc',
    'cpf': 'Comment.PreprocFile',
    'cs': 'Comment.Single',
    'c1': 'Comment.Single',
    'c2': 'Comment.Special',
    'g': 'Generic',
    'gd': 'Generic.Deleted',
    'ge': 'Generic.Emph',
    'gr': 'Generic.Error',
    'gh': 'Generic.Heading',
    'gi': 'Generic.Inserted',
    'go': 'Generic.Output',
    'gp': 'Generic.Prompt',
    'gs': 'Generic.Strong',
    'gu': 'Generic.Subheading',
    'gt': 'Generic.Traceback',
    'x': 'Error',
    'err': 'Error',
    'w': 'Whitespace',
    '': 'Token',
}


def highlight_with_inline_styles(code, lexer):
    """Highlight code and return HTML with inline styles."""
    formatter = HtmlFormatter(nowrap=True, cssclass='')
    highlighted = highlight(code, lexer, formatter)
    
    style_map = {}
    for abbrev, full_name in PYGMENTS_ABBREV_MAP.items():
        parts = full_name.split('.')
        token_type = Token
        for part in parts:
            if part:
                token_type = getattr(token_type, part, None)
                if token_type is None:
                    break
        if token_type and token_type in PYGMENTS_STYLES:
            color_match = re.search(r'color:([^;]+)', PYGMENTS_STYLES[token_type])
            if color_match:
                style_map[abbrev] = color_match.group(1)
    
    def replace_span(match):
        token_abbrev = match.group(1)
        content = match.group(2)
        
        if token_abbrev in style_map:
            return f'<span style="color:{style_map[token_abbrev]};">{content}</span>'
        return f'<span>{content}</span>'
    
    result = re.sub(r'<span class="([^"]+)">([^<]*)</span>', replace_span, highlighted)
    result = re.sub(r'<span class="([^"]+)">([^<]*)</span>', replace_span, result)
    
    return result


class WeChatRenderer(mistune.HTMLRenderer):
    """Renderer that produces WeChat-compatible HTML from Markdown."""
    
    def __init__(self):
        super().__init__()
        self._code_blocks: List[str] = []
    
    def block_code(self, code: str, info: str = None, **attrs) -> str:
        """Render code block with syntax highlighting using inline styles."""
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
            highlighted = highlight_with_inline_styles(code, lexer)
        except:
            highlighted = f'<code style="color:#24292e;">{html_escape(code)}</code>'
        
        highlighted = highlighted.strip()
        uid = f'code-{len(self._code_blocks)}'
        self._code_blocks.append(highlighted)
        
        placeholder = f'<code style="background:#f6f8fa;padding:2px 6px;border-radius:3px;font-family:monospace;font-size:13px;overflow:hidden;">{html_escape(code[:50])}...</code>'
        return f'<pre style="background:#f6f8fa;border-radius:6px;padding:15px;overflow-x:auto;margin:15px 0;font-family:monospace;font-size:13px;line-height:1.5;white-space:pre-wrap;word-break:break-all;">{highlighted}</pre>\n'
    
    def render_image(self, src: str, alt: str = '', title: str = None, **attrs) -> str:
        """Render image with WeChat-compatible attributes."""
        alt_attr = f' alt="{html_escape(alt)}"' if alt else ''
        title_attr = f' title="{html_escape(title)}"' if title else ''
        return f'<img src="{html_escape(src)}"{alt_attr}{title_attr} style="max-width:100%;height:auto;display:block;margin:10px 0;"/>\n'
    
    def render_link(self, link: str, text: str = None, title: str = None, **attrs) -> str:
        """Render link with WeChat-compatible format."""
        text = text or link
        title_attr = f' title="{html_escape(title)}"' if title else ''
        return f'<a href="{html_escape(link)}"{title_attr} style="color:#576b95;text-decoration:none;">{text}</a>'
    
    def render_quote(self, text: str, **attrs) -> str:
        """Render blockquote with WeChat styling."""
        return f'<blockquote style="border-left:3px solid #e5e5e5;padding:5px 10px;margin:10px 0;color:#666;background:#f9f9f9;">{text}</blockquote>\n'
    
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
    
    def codespan(self, text: str) -> str:
        """Render inline code with styling."""
        return f'<code style="background:#f6f8fa;padding:2px 6px;border-radius:3px;font-family:monospace;font-size:13px;color:#e83e8c;">{html_escape(text)}</code>'
    
    def get_code_blocks(self) -> List[str]:
        """Get all code blocks for separate rendering."""
        return self._code_blocks.copy()
    
    def reset(self):
        """Reset internal state."""
        self._code_blocks = []


def create_latex_plugin():
    """Create a LaTeX math plugin for mistune."""
    def latex_block(md, text, level, info):
        return f'<div style="text-align:center;margin:15px 0;padding:10px;background:#f9f9f9;border-radius:4px;font-size:16px;">{text}</div>\n'
    
    def latex_inline(md, text):
        return f'<span style="font-size:16px;padding:0 4px;">{text}</span>'
    
    def parse_latex_block(block):
        pattern = re.compile(r'\$\$(.+?)\$\$', re.DOTALL)
        def replace(match):
            content = match.group(1).strip()
            return f'\n\n latex_block_start {content} latex_block_end \n\n'
        return pattern.sub(replace, block)
    
    def parse_latex_inline(inline):
        pattern = re.compile(r'\$(.+?)\$', re.DOTALL)
        def replace(match):
            content = match.group(1).strip()
            return f' latex_inline_start {content} latex_inline_end '
        return pattern.sub(replace, inline)
    
    class LatexInlineGrammar:
        inline_math = re.compile(r'\$\$(.+?)\$\$|\$(.+?)\$')
    
    class LatexInlineRenderer:
        def latex_math(self, text, info=None):
            if text.startswith('$') and text.endswith('$'):
                content = text[2:-2].strip()
                return f'<span style="font-size:16px;padding:0 4px;">{content}</span>'
            return f'<span style="font-size:16px;padding:0 4px;">{text}</span>'
    
    from mistune.renderers import Renderer
    from mistune.core import BlockState, InlineState
    
    return latex_block, latex_inline


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
        
        markdown_text = process_latex(markdown_text)
        
        renderer = WeChatRenderer()
        md = mistune.create_markdown(
            renderer=renderer,
            plugins=['strikethrough', 'table']
        )
        
        html = md(markdown_text)
        
        html = post_process_latex(html)
        
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


LATEX_BLOCK_PATTERN = re.compile(r'<p>\s*latex_block_start(.+?)latex_block_end\s*</p>', re.DOTALL)
LATEX_INLINE_PATTERN = re.compile(r'latex_inline_start(.+?)latex_inline_end')


def process_latex(text):
    """Process LaTeX delimiters before markdown parsing."""
    text = LATEX_BLOCK_PATTERN.sub(lambda m: f'<p>$${m.group(1).strip()}$$</p>', text)
    text = LATEX_INLINE_PATTERN.sub(lambda m: f'${m.group(1).strip()}$', text)
    return text


def post_process_latex(text):
    """Convert LaTeX markers to final HTML."""
    def latex_block_replace(match):
        content = match.group(1).strip()
        return f'<div style="text-align:center;margin:15px 0;padding:15px;background:#f9f9f9;border-radius:8px;font-size:16px;line-height:1.8;font-family:Times New Roman,serif;">{content}</div>'
    
    def latex_inline_replace(match):
        content = match.group(1).strip()
        return f'<span style="font-size:16px;padding:0 2px;font-family:Times New Roman,serif;">{content}</span>'
    
    text = re.sub(r'<p>\s*\$\$(.+?)\$\$\s*</p>', latex_block_replace, text, flags=re.DOTALL)
    text = re.sub(r'\$\$(.+?)\$\$', latex_block_replace, text, flags=re.DOTALL)
    text = re.sub(r'\$(.+?)\$', latex_inline_replace, text)
    
    text = re.sub(r'<p>\s*latex_block_start(.+?)latex_block_end\s*</p>', 
                  lambda m: f'<p>$${m.group(1).strip()}$$</p>', text, flags=re.DOTALL)
    text = re.sub(r'latex_block_start(.+?)latex_block_end', 
                  lambda m: f'$${m.group(1).strip()}$$', text)
    text = re.sub(r'latex_inline_start(.+?)latex_inline_end', 
                  lambda m: f'${m.group(1).strip()}$', text)
    
    return text


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return html_escape(text)


def clean_html_for_wechat(html: str) -> str:
    """
    Clean HTML to be WeChat-compatible.
    Removes unsupported tags and attributes.
    """
    allowed_tags = WECHAT_SAFE_TAGS
    
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
            border-radius: 6px;
            padding: 15px;
            overflow-x: auto;
            margin: 15px 0;
            font-family: "SF Mono", Consolas, Monaco, monospace;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        code {{
            background: #f6f8fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "SF Mono", Consolas, Monaco, monospace;
            font-size: 13px;
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
