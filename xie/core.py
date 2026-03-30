"""
Core conversion module for Markdown to WeChat Public Account HTML.
Generates HTML compatible with WeChat public account editor, matching mdnice format.
"""
import re
import os
import subprocess
import json
from dataclasses import dataclass, field
from typing import Any, Optional, List
from html import escape as html_escape

import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter


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
                outfile.write(f'<span style="color:{color};line-height:26px;">{escaped}</span>')
            else:
                outfile.write(html_escape(value))


WECHAT_SAFE_TAGS = {
    'section', 'header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'b', 'em', 'i', 'u', 's', 'strike', 'del',
    'p', 'br', 'span', 'a', 'img', 'blockquote', 'pre', 'code',
    'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'ruby', 'rt', 'sup', 'sub', 'svg', 'path', 'g', 'rect'
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


DATA_TOOL_ATTR = 'data-tool="mdnice编辑器"'
WEBSITE_ATTR = 'data-website="https://www.mdnice.com"'
SECTION_WRAPPER_STYLE = (
    'margin-top:0px;margin-bottom:0px;margin-left:0px;margin-right:0px;'
    'padding-top:0px;padding-bottom:0px;padding-left:10px;padding-right:10px;'
    'background-attachment:scroll;background-clip:border-box;background-color:rgba(0,0,0,0);'
    'background-image:none;background-origin:padding-box;background-position-x:left;'
    'background-position-y:top;background-repeat:no-repeat;background-size:auto;'
    'width:auto;font-family:Optima,Microsoft YaHei,PingFangSC-regular,serif;'
    'font-size:16px;color:rgb(0,0,0);line-height:1.5em;word-spacing:0em;'
    'letter-spacing:0em;word-break:break-word;overflow-wrap:break-word;text-align:left;'
)


class WeChatRenderer(mistune.HTMLRenderer):
    """Renderer that produces WeChat-compatible HTML matching mdnice format."""
    
    def __init__(self):
        super().__init__()
        self._code_blocks: List[str] = []
    
    def _get_data_tool_attr(self) -> str:
        return DATA_TOOL_ATTR
    
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
        
        self._code_blocks.append(highlighted)
        
        return (
            f'<pre class="custom" {self._get_data_tool_attr()} style="'
            f'border-radius:5px;'
            f'box-shadow:rgba(0,0,0,0.55) 0px 2px 10px;'
            f'text-align:left;'
            f'margin-top:10px;margin-bottom:10px;margin-left:0px;margin-right:0px;'
            f'padding-top:0px;padding-bottom:0px;padding-left:0px;padding-right:0px;">'
            f'<span style="display:block;'
            f'background:url(https://files.mdnice.com/user/3441/876cad08-0422-409d-bb5a-08afec5da8ee.svg);'
            f'height:30px;width:100%;background-size:40px;background-repeat:no-repeat;'
            f'background-color:#282c34;margin-bottom:-7px;border-radius:5px;background-position:10px 10px;"></span>'
            f'<code class="hljs" style="'
            f'overflow-x:auto;'
            f'padding:16px;'
            f'color:#abb2bf;'
            f'padding-top:15px;'
            f'background:#282c34;'
            f'border-radius:5px;'
            f'display:-webkit-box;'
            f'font-family:Consolas,Monaco,Menlo,monospace;'
            f'font-size:12px;">{highlighted}<br></code></pre>\n'
        )
    
    def image(self, text: str = '', url: str = '', title: str = None) -> str:
        """Render image with WeChat-compatible attributes."""
        alt = text or ''
        alt_attr = f' alt="{html_escape(alt)}"' if alt else ''
        title_attr = f' title="{html_escape(title)}"' if title else ''
        return f'<img src="{html_escape(url)}"{alt_attr}{title_attr} style="max-width:100%;height:auto;"/>\n'
    
    def link(self, text: str = '', url: str = '', title: str = None) -> str:
        """Render link with WeChat-compatible format."""
        text = text or url
        title_attr = f' title="{html_escape(title)}"' if title else ''
        return f'<a href="{html_escape(url)}"{title_attr} style="color:#576b95;">{text}</a>'
    
    def block_quote(self, text: str, **attrs) -> str:
        """Render blockquote with WeChat styling like mdnice."""
        return (
            f'<blockquote class="custom-blockquote multiquote-1" {self._get_data_tool_attr()} style="'
            f'margin-top:20px;margin-bottom:20px;margin-left:0px;margin-right:0px;'
            f'padding-top:10px;padding-bottom:10px;padding-left:20px;padding-right:10px;'
            f'border-top-style:none;border-bottom-style:none;border-left-style:solid;border-right-style:none;'
            f'border-top-width:3px;border-bottom-width:3px;border-left-width:3px;border-right-width:3px;'
            f'border-top-color:rgba(0,0,0,0.4);border-bottom-color:rgba(0,0,0,0.4);'
            f'border-left-color:rgba(0,0,0,0.4);border-right-color:rgba(0,0,0,0.4);'
            f'border-top-left-radius:0px;border-top-right-radius:0px;'
            f'border-bottom-right-radius:0px;border-bottom-left-radius:0px;'
            f'background-attachment:scroll;background-clip:border-box;background-color:rgba(0,0,0,0.05);'
            f'background-image:none;background-origin:padding-box;background-position-x:left;'
            f'background-position-y:top;background-repeat:no-repeat;background-size:auto;'
            f'width:auto;height:auto;box-shadow:rgba(0,0,0,0) 0px 0px 0px 0px;'
            f'display:block;overflow-x:auto;overflow-y:auto;">'
            f'<span style="display:none;color:rgb(0,0,0);font-size:16px;line-height:1.5em;'
            f'letter-spacing:0em;text-align:left;font-weight:normal;"></span>\n{text}</blockquote>\n'
        )
    
    def paragraph(self, text: str, **attrs) -> str:
        """Render paragraph with mdnice-style inline CSS."""
        return (
            f'<p {self._get_data_tool_attr()} style="'
            f'color:rgb(0,0,0);font-size:16px;line-height:1.8em;letter-spacing:0em;'
            f'text-align:left;text-indent:0em;'
            f'margin-top:0px;margin-bottom:0px;margin-left:0px;margin-right:0px;'
            f'padding-top:8px;padding-bottom:8px;padding-left:0px;padding-right:0px;">{text}</p>\n'
        )
    
    def heading(self, text: str, level: int, **attrs) -> str:
        """Render heading with mdnice-style structure (prefix/content/suffix spans)."""
        sizes = {1: '24px', 2: '22px', 3: '20px', 4: '18px', 5: '16px', 6: '15px'}
        size = sizes.get(level, '16px')
        
        return (
            f'<h{level} {self._get_data_tool_attr()} style="'
            f'margin-top:30px;margin-bottom:15px;margin-left:0px;margin-right:0px;'
            f'padding-top:0px;padding-bottom:0px;padding-left:0px;padding-right:0px;display:block;">'
            f'<span class="prefix" style="display:none;"></span>'
            f'<span class="content" style="font-size:{size};color:rgb(0,0,0);'
            f'line-height:1.5em;letter-spacing:0em;text-align:left;font-weight:bold;display:block;">{text}</span>'
            f'<span class="suffix" style="display:none;"></span></h{level}>\n'
        )
    
    def list(self, text: str, ordered: bool = False, **attrs) -> str:
        """Render list with WeChat-compatible styling."""
        tag = 'ol' if ordered else 'ul'
        list_style = 'decimal' if ordered else 'disc'
        return (
            f'<{tag} {self._get_data_tool_attr()} style="'
            f'list-style-type:{list_style};'
            f'margin-top:8px;margin-bottom:8px;margin-left:0px;margin-right:0px;'
            f'padding-top:0px;padding-bottom:0px;padding-left:25px;padding-right:0px;'
            f'color:rgb(0,0,0);">{text}</{tag}>\n'
        )
    
    def list_item(self, text: str, **attrs) -> str:
        """Render list item with section wrapper."""
        return (
            f'<li><section style="'
            f'margin-top:5px;margin-bottom:5px;'
            f'color:rgb(1,1,1);font-size:16px;line-height:1.8em;'
            f'letter-spacing:0em;text-align:left;font-weight:normal;">{text}</section></li>'
        )
    
    def strong(self, text: str, **attrs) -> str:
        """Render strong text with full inline styles."""
        return (
            f'<strong style="color:rgb(0,0,0);font-weight:bold;'
            f'background-attachment:scroll;background-clip:border-box;background-color:rgba(0,0,0,0);'
            f'background-image:none;background-origin:padding-box;background-position-x:left;'
            f'background-position-y:top;background-repeat:no-repeat;background-size:auto;'
            f'width:auto;height:auto;margin-top:0px;margin-bottom:0px;margin-left:0px;margin-right:0px;'
            f'padding-top:0px;padding-bottom:0px;padding-left:0px;padding-right:0px;'
            f'border-top-style:none;border-bottom-style:none;border-left-style:none;border-right-style:none;'
            f'border-top-width:3px;border-bottom-width:3px;border-left-width:3px;border-right-width:3px;'
            f'border-top-color:rgba(0,0,0,0.4);border-bottom-color:rgba(0,0,0,0.4);'
            f'border-left-color:rgba(0,0,0,0.4);border-right-color:rgba(0,0,0,0.4);'
            f'border-top-left-radius:0px;border-top-right-radius:0px;'
            f'border-bottom-right-radius:0px;border-bottom-left-radius:0px;">{text}</strong>'
        )
    
    def emphasis(self, text: str, **attrs) -> str:
        """Render emphasized text."""
        return f'<em style="font-style:italic;color:rgb(0,0,0);">{text}</em>'
    
    def strikethrough(self, text: str, **attrs) -> str:
        """Render strikethrough text."""
        return f'<s style="text-decoration:line-through;color:rgb(0,0,0);">{text}</s>'
    
    def codespan(self, text: str) -> str:
        """Render inline code with styling."""
        return (
            f'<code style="background:#f0f0f0;padding:2px 4px;border-radius:3px;'
            f'font-family:Consolas,Monaco,Menlo,monospace;font-size:13px;color:#1e6bb8;">{html_escape(text)}</code>'
        )
    
    def table(self, text: str, **attrs) -> str:
        """Render table with WeChat-compatible styling."""
        return (
            f'<table {self._get_data_tool_attr()} style="'
            f'border-collapse:collapse;width:100%;margin:10px 0;">{text}</table>\n'
        )
    
    def table_head(self, text: str, **attrs) -> str:
        """Render table head."""
        return f'<thead>{text}</thead>\n'
    
    def table_body(self, text: str, **attrs) -> str:
        """Render table body."""
        return f'<tbody>{text}</tbody>\n'
    
    def table_row(self, text: str, **attrs) -> str:
        """Render table row."""
        return f'<tr>{text}</tr>\n'
    
    def table_cell(self, text: str, head: bool = False, **attrs) -> str:
        """Render table cell with borders."""
        tag = 'th' if head else 'td'
        align = attrs.get('align')
        align_style = f' text-align:{align};' if align else ''
        border_style = f'border:1px solid #e5e5e5;padding:8px;{align_style}'
        return f'<{tag} style="{border_style}">{text}</{tag}>\n'
    
    def get_code_blocks(self) -> List[str]:
        """Get all code blocks for separate rendering."""
        return self._code_blocks.copy()
    
    def reset(self):
        """Reset internal state."""
        self._code_blocks = []


def render_latex_to_svg(latex: str, display: bool = True) -> Optional[str]:
    """
    Render LaTeX formula to SVG using mathjax-node.
    Returns simplified SVG string for WeChat compatibility.
    """
    try:
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        mathjax_node_path = os.path.join(pkg_dir, 'node_modules', 'mathjax-node')
        
        latex_escaped = latex.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
        
        node_script = f'''
const mj = require('{mathjax_node_path}');
mj.typeset({{
    math: '{latex_escaped}',
    format: 'TeX',
    svg: true,
    display: {str(display).lower()}
}}, function(data) {{
    if (data.errors) {{
        console.log(JSON.stringify({{ error: data.errors.join(', ') }}));
    }} else {{
        console.log(JSON.stringify({{ svg: data.svg }}));
    }}
}});
'''
        
        result = subprocess.run(
            ['node', '-e', node_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout.strip())
                if 'error' in data:
                    print(f"MathJax error: {data['error']}")
                    return None
                svg_content = data.get('svg', '')
                
                svg_content = expand_svg_use_refs(svg_content)
                
                width_match = re.search(r'width="([^"]*)"', svg_content)
                height_match = re.search(r'height="([^"]*)"', svg_content)
                viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
                valign_match = re.search(r'vertical-align:\s*([^;"]*)', svg_content)
                
                if width_match:
                    width_val = width_match.group(1)
                    w_num = float(width_val.replace('ex', '').replace('em', '').replace('px', '') or '7.6')
                else:
                    w_num = 7.6
                
                if height_match:
                    height_val = height_match.group(1)
                    h_num = float(height_val.replace('ex', '').replace('em', '').replace('px', '') or '4.5')
                else:
                    h_num = 4.5
                
                valign = valign_match.group(1) if valign_match else '-1.5ex'
                viewbox = viewbox_match.group(1) if viewbox_match else '0 -1000 3500 2000'
                
                svg_content = re.sub(
                    r'<svg[^>]*>',
                    f'<svg style="vertical-align:{valign};width:{w_num:.3f}ex;height:{h_num:.3f}ex;max-width:300% !important;" xmlns="http://www.w3.org/2000/svg" role="img" focusable="false" viewBox="{viewbox}">',
                    svg_content
                )
                
                svg_content = re.sub(r'<title[^>]*>.*?</title>', '', svg_content, flags=re.DOTALL)
                svg_content = re.sub(r' aria-labelledby="[^"]*"', '', svg_content)
                svg_content = re.sub(r' xmlns:xlink="[^"]*"', '', svg_content)
                svg_content = re.sub(r'<defs[^>]*>.*?</defs>', '', svg_content, flags=re.DOTALL)
                svg_content = re.sub(r'\s+', ' ', svg_content)
                svg_content = re.sub(r'>\s+<', '><', svg_content)
                svg_content = re.sub(r'<\s+', '<', svg_content)
                svg_content = re.sub(r'\s+>', '>', svg_content)
                
                return svg_content
            except json.JSONDecodeError:
                print(f"JSON decode error: {result.stdout}")
                return None
        else:
            print(f"MathJax node error: {result.stderr}")
            return None
    except Exception as e:
        print(f"MathJax exception: {e}")
        return None


def expand_svg_use_refs(svg_content: str) -> str:
    """
    Expand <use xlink:href="#id"> references to inline SVG content.
    WeChat doesn't support xlink:href references.
    """
    defs = {}
    
    def_match = re.search(r'<defs[^>]*>(.*?)</defs>', svg_content, re.DOTALL)
    if def_match:
        defs_content = def_match.group(1)
        for path_match in re.finditer(r'<path[^>]*id="([^"]+)"[^>]*d="([^"]+)"[^>]*/?\s*>', defs_content):
            defs[path_match.group(1)] = path_match.group(2)
    
    def replace_use(match):
        use_tag = match.group(0)
        
        href_match = re.search(r'xlink:href="#([^"]+)"', use_tag)
        if not href_match:
            return use_tag
        
        ref_id = href_match.group(1)
        if ref_id not in defs:
            return use_tag
        
        path_d = defs[ref_id]
        
        transform_match = re.search(r'transform="([^"]*)"', use_tag)
        transform = transform_match.group(1) if transform_match else ''
        
        if transform:
            return f'<path d="{path_d}" transform="{transform}" fill="currentColor"/>'
        else:
            return f'<path d="{path_d}" fill="currentColor"/>'
    
    svg_content = re.sub(r'<use[^>]*xlink:href="[^"]*"[^>]*>.*?</use>', replace_use, svg_content, flags=re.DOTALL)
    svg_content = re.sub(r'<use[^>]*xlink:href="[^"]*"[^>]*/>', replace_use, svg_content)
    
    return svg_content


def render_latex_to_html(latex: str, display: bool = True) -> Optional[str]:
    """
    Render LaTeX formula to HTML using KaTeX.
    Returns KaTeX HTML output as-is for WeChat compatibility.
    """
    try:
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        katex_path = os.path.join(pkg_dir, 'node_modules', 'katex')
        
        latex_escaped = latex.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
        
        node_script = f'''
const katex = require('{katex_path}');
const html = katex.renderToString('{latex_escaped}', {{
    displayMode: {str(display).lower()},
    throwOnError: false,
    trust: true,
    strict: false,
    output: 'html'
}});
console.log(html);
'''
        
        result = subprocess.run(
            ['node', '-e', node_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            html_content = result.stdout.strip()
            return html_content
        else:
            print(f"KaTeX error: {result.stderr}")
            return None
    except Exception as e:
        print(f"KaTeX exception: {e}")
        return None
    except Exception as e:
        print(f"KaTeX exception: {e}")
        return None


def render_latex_simple(latex: str, display: bool = True) -> str:
    """
    Simple LaTeX rendering for WeChat - outputs formatted HTML without external dependencies.
    Uses unicode math symbols where possible.
    """
    processed = latex
    
    greek_letters = {
        '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ', '\\delta': 'δ',
        '\\epsilon': 'ε', '\\zeta': 'ζ', '\\eta': 'η', '\\theta': 'θ',
        '\\iota': 'ι', '\\kappa': 'κ', '\\lambda': 'λ', '\\mu': 'μ',
        '\\nu': 'ν', '\\xi': 'ξ', '\\omicron': 'ο', '\\pi': 'π',
        '\\rho': 'ρ', '\\sigma': 'σ', '\\tau': 'τ', '\\upsilon': 'υ',
        '\\phi': 'φ', '\\chi': 'χ', '\\psi': 'ψ', '\\omega': 'ω',
        '\\Alpha': 'Α', '\\Beta': 'Β', '\\Gamma': 'Γ', '\\Delta': 'Δ',
        '\\Epsilon': 'Ε', '\\Zeta': 'Ζ', '\\Eta': 'Η', '\\Theta': 'Θ',
        '\\Iota': 'Ι', '\\Kappa': 'Κ', '\\Lambda': 'Λ', '\\Mu': 'Μ',
        '\\Nu': 'Ν', '\\Xi': 'Ξ', '\\Omicron': 'Ο', '\\Pi': 'Π',
        '\\Rho': 'Ρ', '\\Sigma': 'Σ', '\\Tau': 'Τ', '\\Upsilon': 'Υ',
        '\\Phi': 'Φ', '\\Chi': 'Χ', '\\Psi': 'Ψ', '\\Omega': 'Ω',
    }
    
    for cmd, char in greek_letters.items():
        processed = processed.replace(cmd, char)
    
    processed = processed.replace('\\infty', '∞')
    processed = processed.replace('\\pm', '±')
    processed = processed.replace('\\cdot', '·')
    processed = processed.replace('\\times', '×')
    processed = processed.replace('\\div', '÷')
    processed = processed.replace('\\leq', '≤')
    processed = processed.replace('\\geq', '≥')
    processed = processed.replace('\\neq', '≠')
    processed = processed.replace('\\approx', '≈')
    processed = processed.replace('\\partial', '∂')
    processed = processed.replace('\\nabla', '∇')
    
    processed = re.sub(r'\\frac\s*\{([^}]+)\}\s*\{([^}]+)\}', 
                       r'<span style="display:inline-block;text-align:center;vertical-align:-50%;"><span style="display:block;border-bottom:1px solid currentColor;margin-bottom:1px;">\1</span><span style="display:block;">\2</span></span>', 
                       processed)
    
    processed = re.sub(r'\\sqrt\s*\{([^}]+)\}', r'√(\1)', processed)
    
    processed = re.sub(r'\\int[_]?(\{[^}]+\})?(\^[^{]+)?', 
                       lambda m: '∫' + (m.group(1)[1:-1] if m.group(1) else '') + (m.group(2)[1:] if m.group(2) else ''), 
                       processed)
    
    processed = re.sub(r'\\sum[_]?(\{[^}]+\})?(\^[^{]+)?', 
                       lambda m: 'Σ' + (m.group(1)[1:-1] if m.group(1) else '') + (m.group(2)[1:] if m.group(2) else ''), 
                       processed)
    
    processed = re.sub(r'\^{([^}]+)}', r'<sup>\1</sup>', processed)
    processed = re.sub(r'_{([^}]+)}', r'<sub>\1</sub>', processed)
    processed = re.sub(r'\^([a-zA-Z0-9])', r'<sup>\1</sup>', processed)
    processed = re.sub(r'_([a-zA-Z0-9])', r'<sub>\1</sub>', processed)
    
    processed = re.sub(r'\\[a-zA-Z]+', '', processed)
    
    return processed


def convert_markdown_to_wechat(markdown_text: str, **kwargs) -> ToolResult:
    """
    Convert Markdown text to WeChat Public Account compatible HTML.
    Output matches mdnice editor format with full inline styles.
    
    Args:
        markdown_text: Input markdown string
        **kwargs: Additional conversion options
            - wechat_compatible: bool, if True use simplified formula output for WeChat
        
    Returns:
        ToolResult with converted HTML and metadata
    """
    try:
        if not isinstance(markdown_text, str):
            return ToolResult(
                success=False,
                error="Input must be a string"
            )
        
        wechat_mode = kwargs.get('wechat_compatible', False)
        
        markdown_text = process_latex(markdown_text)
        
        renderer = WeChatRenderer()
        md = mistune.create_markdown(
            renderer=renderer,
            plugins=['strikethrough', 'table']
        )
        
        content_html = md(markdown_text)
        
        content_html = post_process_latex(content_html, wechat_mode=wechat_mode)
        
        html = wrap_with_section(content_html)
        
        code_blocks = renderer.get_code_blocks()
        
        metadata = {
            'code_blocks_count': len(code_blocks),
            'input_length': len(markdown_text),
            'output_length': len(html),
            'wechat_mode': wechat_mode,
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


def wrap_with_section(content: str) -> str:
    """Wrap content with mdnice-style section wrapper."""
    return (
        f'<section id="nice" {DATA_TOOL_ATTR} {WEBSITE_ATTR} style="{SECTION_WRAPPER_STYLE}">'
        f'{content}'
        f'</section>'
    )


def process_latex(text):
    """Process LaTeX delimiters before markdown parsing. Protects code blocks."""
    code_blocks = []
    
    def save_code(match):
        code_blocks.append(match.group(0))
        return f'\x00CODEBLOCK{len(code_blocks)-1}\x00'
    
    text = re.sub(r'```[\s\S]*?```', save_code, text)
    text = re.sub(r'`[^`]+`', save_code, text)
    
    text = re.sub(r'\$\$\s*([^$]+?)\s*\$\$', lambda m: f'LATEXBLOCKSTART{m.group(1).strip()}LATEXBLOCKEND', text, flags=re.DOTALL)
    text = re.sub(r'\$\s*([^$\n]+?)\s*\$', lambda m: f'latexinlinestart{m.group(1).strip()}latexinlineend', text)
    
    for i, code in enumerate(code_blocks):
        text = text.replace(f'\x00CODEBLOCK{i}\x00', code)
    
    return text


def post_process_latex(text, wechat_mode=False):
    """Convert LaTeX markers to final HTML with rendered formulas."""
    def latex_block_replace(match):
        content = match.group(1).strip()
        if wechat_mode:
            simple = render_latex_simple(content, display=True)
            return (
                f'<span style="display:block;text-align:center;font-family:serif;'
                f'color:rgb(0,0,0);font-size:16px;line-height:1.8em;margin:10px 0;">{simple}</span>\n'
            )
        svg = render_latex_to_svg(content, display=True)
        if svg:
            return (
                f'<span class="span-block-equation" style="cursor:pointer" {DATA_TOOL_ATTR}>'
                f'<section class="block-equation" data-formula="{html_escape(content)}" style="'
                f'text-align:center;overflow-x:auto;overflow-y:auto;display:block;">{svg}</section></span>\n'
            )
        simple = render_latex_simple(content, display=True)
        return (
            f'<span style="display:block;text-align:center;font-family:serif;'
            f'color:rgb(0,0,0);font-size:16px;line-height:1.8em;margin:10px 0;">{simple}</span>\n'
        )
    
    def latex_inline_replace(match):
        content = match.group(1).strip()
        if wechat_mode:
            simple = render_latex_simple(content, display=False)
            return f'<span style="font-family:serif;">{simple}</span>'
        svg = render_latex_to_svg(content, display=False)
        if svg:
            return f'<span class="span-inline-equation" style="cursor:pointer">{svg}</span>'
        simple = render_latex_simple(content, display=False)
        return f'<span style="font-family:serif;">{simple}</span>'
    
    text = re.sub(r'<p>\s*LATEXBLOCKSTART(.+?)LATEXBLOCKEND\s*</p>', latex_block_replace, text, flags=re.DOTALL)
    text = re.sub(r'LATEXBLOCKSTART(.+?)LATEXBLOCKEND', lambda m: latex_block_replace(m), text)
    text = re.sub(r'latexinlinestart(.+?)latexinlineend', latex_inline_replace, text)
    
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
                safe_attrs = re.sub(r'alt="[^"]*"', '', attrs)
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
    """
    author_html = f'<p style="text-align:right;color:#999;font-size:14px;">文/{author or ""}</p>' if author else ''
    
    html = f'''<div>
<h1 style="font-size:24px;font-weight:bold;text-align:center;margin:16px 0;">{escape_html(title)}</h1>
{author_html}
<div>
{content}
</div>
</div>'''
    
    return html