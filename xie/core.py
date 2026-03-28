"""
Core conversion module for Markdown to WeChat Public Account HTML.
"""
import re
import os
import tempfile
import base64
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


ONEDARK_COLORS = {
    'comment': '#5c6370',
    'keyword': '#c678dd',
    'operator': '#56b6c2',
    'punctuation': '#abb2bf',
    'string': '#98c379',
    'number': '#d19a66',
    'function': '#61aeee',
    'class': '#e6c07b',
    'variable': '#e06c75',
    'constant': '#d19a66',
    'attribute': '#d19a66',
    'tag': '#e06c75',
    'name': '#e06c75',
    'builtin': '#e6c07b',
    'type': '#e5c07b',
    'literal': '#56b6c2',
    'entity': '#56b6c2',
    'rx': '#98c379',
    'symbol': '#56b6c2',
    'error': '#e06c75',
    'deprecated': '#5c6370',
    'generic': '#abb2bf',
    'heading': '#61aeee',
    'strong': '#e06c75',
    'emphasis': '#c678dd',
    'deleted': '#e06c75',
    'inserted': '#98c379',
    'changed': '#e5c07b',
}


def get_token_color(token_type):
    """Get color for a token type hierarchy."""
    while token_type:
        type_str = str(token_type)
        for key, color in ONEDARK_COLORS.items():
            if key in type_str.lower():
                return color
        token_type = token_type.parent
    return '#abb2bf'


class WeChatCodeFormatter(HtmlFormatter):
    """Custom formatter that outputs inline styles with actual colors for WeChat."""
    
    def __init__(self, **options):
        options['nowrap'] = True
        options['linenos'] = False
        super().__init__(**options)
    
    def format(self, tokensource, outfile):
        """Format tokens and output inline styles."""
        for ttype, value in tokensource:
            while ttype not in self.style and ttype.parent:
                ttype = ttype.parent
            
            if ttype in self.style:
                style = self.style[ttype]
                color = style['color'] if style.get('color') else get_token_color(ttype)
            else:
                color = get_token_color(ttype)
            
            if value.strip():
                escaped = html_escape(value)
                outfile.write(f'<span style="color:{color};">{escaped}</span>')
            else:
                outfile.write(html_escape(value))


WECHAT_SAFE_TAGS = {
    'section', 'header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'b', 'em', 'i', 'u', 's', 'strike', 'del',
    'p', 'br', 'span', 'a', 'img', 'blockquote', 'pre', 'code',
    'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'ruby', 'rt', 'sup', 'sub', 'section'
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


class WeChatRenderer(mistune.HTMLRenderer):
    """Renderer that produces WeChat-compatible HTML from Markdown."""
    
    def __init__(self):
        super().__init__()
        self._code_blocks: List[str] = []
    
    def block_code(self, code: str, info: str = None, **attrs) -> str:
        """Render code block with syntax highlighting and WeChat-compatible styling."""
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
            formatter = WeChatCodeFormatter()
            highlighted = highlight(code, lexer, formatter)
        except:
            highlighted = html_escape(code)
        
        uid = f'code-{len(self._code_blocks)}'
        self._code_blocks.append(highlighted)
        
        styled_pre = (
            f'<pre class="custom" style="'
            f'border-radius:5px;'
            f'box-shadow:rgba(0,0,0,0.55) 0px 2px 10px;'
            f'margin:10px 0;'
            f'overflow-x:auto;'
            f'">'
            f'<span style="display:block;background:url(https://files.mdnice.com/user/3441/876cad08-0422-409d-bb5a-08afec5da8ee.svg);height:30px;width:100%;background-size:40px;background-repeat:no-repeat;background-color:#282c34;margin-bottom:-7px;border-radius:5px;background-position:10px 10px;"></span>'
            f'<code class="hljs" style="'
            f'overflow-x:auto;'
            f'padding:16px;'
            f'color:#abb2bf;'
            f'padding-top:15px;'
            f'background:#282c34;'
            f'border-radius:5px;'
            f'display:-webkit-box;'
            f'font-family:Consolas,Monaco,Menlo,monospace;'
            f'font-size:12px;'
            f'line-height:1.5;'
            f'">'
            f'{highlighted}'
            f'</code>'
            f'</pre>'
        )
        
        placeholder = f'<code class="code-block" data-id="{uid}"></code>'
        return f'{styled_pre}\n'
    
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
    
    def block_quote(self, text: str, **attrs) -> str:
        """Render blockquote with WeChat styling like mdnice."""
        return f'<blockquote style="border-left:3px solid rgba(0,0,0,0.4);padding:10px 10px 10px 20px;margin:10px 0;background:rgba(0,0,0,0.05);">{text}</blockquote>\n'
    
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
        return f'<code style="background:#f0f0f0;padding:2px 4px;border-radius:3px;font-family:Consolas,Monaco,Menlo,monospace;font-size:13px;color:#1e6bb8;">{html_escape(text)}</code>'
    
    def get_code_blocks(self) -> List[str]:
        """Get all code blocks for separate rendering."""
        return self._code_blocks.copy()
    
    def reset(self):
        """Reset internal state."""
        self._code_blocks = []


def render_latex_to_katex(latex: str, display: bool = True) -> Optional[str]:
    """
    Render LaTeX formula to HTML using KaTeX.
    Returns HTML string with inline styles, or None if rendering fails.
    Strips MathML wrapper for WeChat compatibility (WeChat doesn't support MathML).
    """
    try:
        import subprocess
        import json
        import os
        
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        katex_path = os.path.join(pkg_dir, 'node_modules', 'katex')
        
        node_script = f'''
const katex = require('{katex_path}');
const html = katex.renderToString({json.dumps(latex)}, {{
    displayMode: {str(display).lower()},
    throwOnError: false,
    trust: true,
    strict: false
}});
// Strip MathML wrapper - WeChat doesn't support <math> tags
// Keep only the visual katex-html content
const mathmlMatch = html.match(/<span class="katex-mathml">.*?<\\/span>/s);
let visualHtml = html;
if (mathmlMatch) {{
    // Remove the MathML span but keep the rest
    visualHtml = html.replace(/<span class="katex-mathml">.*?<\\/span>/s, '');
}}
// Also remove the aria-hidden attribute
visualHtml = visualHtml.replace(/ aria-hidden="true"/g, '');
console.log(visualHtml);
'''
        
        result = subprocess.run(
            ['node', '-e', node_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            print(f"KaTeX error: {result.stderr}")
            return None
    except Exception as e:
        print(f"KaTeX exception: {e}")
        return None


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


import io

LATEX_BLOCK_PATTERN = re.compile(r'<p>\s*latex_block_start(.+?)latex_block_end\s*</p>', re.DOTALL)
LATEX_INLINE_PATTERN = re.compile(r'latex_inline_start(.+?)latex_inline_end')


def process_latex(text):
    """Process LaTeX delimiters before markdown parsing."""
    text = LATEX_BLOCK_PATTERN.sub(lambda m: f'<p>$${m.group(1).strip()}$$</p>', text)
    text = LATEX_INLINE_PATTERN.sub(lambda m: f'${m.group(1).strip()}$', text)
    return text


def post_process_latex(text):
    """Convert LaTeX markers to final HTML with KaTeX rendered content."""
    def latex_block_replace(match):
        content = match.group(1).strip()
        katex_html = render_latex_to_katex(content, display=True)
        if katex_html:
            return f'<div style="text-align:center;margin:10px 0;">{katex_html}</div>'
        return f'<p style="text-align:center;font-family:serif;">{content}</p>'
    
    def latex_inline_replace(match):
        content = match.group(1).strip()
        katex_html = render_latex_to_katex(content, display=False)
        if katex_html:
            return katex_html
        return f'<span style="font-family:serif;">{content}</span>'
    
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
</head>
<body>
    <h1 style="text-align:center;font-size:24px;font-weight:bold;margin:20px 0;">{escape_html(title)}</h1>
    {author_html}
    <div>
        {content}
    </div>
</body>
</html>'''
    
    return doc


def create_wechat_copy_html(title: str, content: str, author: str = None) -> str:
    """
    Create WeChat-compatible HTML specifically for copying to clipboard.
    Preserves inline styles and code blocks that WeChat supports.
    Simplifies KaTeX HTML for better WeChat compatibility.
    """
    content = simplify_katex_for_wechat(content)
    
    author_html = f'<p style="text-align:right;color:#999;font-size:14px;">文/{author or ""}</p>' if author else ''
    
    html = f'''<div>
<h1 style="font-size:24px;font-weight:bold;text-align:center;margin:16px 0;">{escape_html(title)}</h1>
{author_html}
<div>
{content}
</div>
</div>'''
    
    return html


def simplify_katex_for_wechat(html: str) -> str:
    """
    Simplify KaTeX HTML for WeChat compatibility.
    Removes complex CSS, keeps essential structure and SVG elements.
    """
    import re
    
    katex_display_pattern = re.compile(r'<span class="katex-display">(<span class="katex">.*?</span>)</span>', re.DOTALL)
    html = katex_display_pattern.sub(r'\1', html)
    
    katex_pattern = re.compile(r'<span class="katex">(<span class="katex-html">.*?</span>)</span>', re.DOTALL)
    html = katex_pattern.sub(r'\1', html)
    
    html = re.sub(r' style="[^"]*"', '', html)
    
    html = re.sub(r'<span class="(strut|pstrut|mspace|mord|mbin|mrel|mpunct|mn|mo|mi|text|vlist-t|vlist-r|vlist-s|mopen|mclose|nulldelimiter|frac-line|hide-tail)[^"]*"></span>', '', html)
    html = re.sub(r'<span class="(sizing|mtight|msupsub|svg-align|displaystyle|small|large-ops|normal-size)[^"]*">(.*?)</span>', r'\2', html, flags=re.DOTALL)
    
    html = re.sub(r'<span class="[^"]*">(<[^>]+>)</span>', r'\1', html)
    
    html = re.sub(r'\s+', ' ', html)
    html = re.sub(r'> <', '><', html)
    
    return html
