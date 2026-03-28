"""
Xie - Markdown to WeChat Public Account HTML Converter

A tool for converting Markdown documents to WeChat-compatible HTML
that can be directly pasted into WeChat public account articles.
"""

__version__ = "1.0.0"
__author__ = "Author"
__email__ = "author@example.com"

from xie.core import (
    convert_markdown_to_wechat,
    create_wechat_html_document,
    ToolResult,
    escape_html,
    clean_html_for_wechat,
)

__all__ = [
    "convert_markdown_to_wechat",
    "create_wechat_html_document",
    "ToolResult",
    "escape_html",
    "clean_html_for_wechat",
    "__version__",
]
