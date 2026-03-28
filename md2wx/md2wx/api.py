"""
Unified Python API for md2wx.
"""
from dataclasses import dataclass
from typing import Any, Optional

from md2wx.core import (
    convert_markdown_to_wechat,
    create_wechat_html_document,
    ToolResult as _ToolResult,
    escape_html,
    clean_html_for_wechat,
)


@dataclass
class ToolResult:
    """Unified result type for API functions."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }

    @property
    def html(self) -> Optional[str]:
        if self.success and self.data:
            return self.data.get('html')
        return None

    @property
    def code_blocks(self) -> list:
        if self.success and self.data:
            return self.data.get('code_blocks', [])
        return []

    @property
    def error_message(self) -> Optional[str]:
        return self.error


def convert(
    markdown: str,
    standalone: bool = False,
    title: str = "Untitled",
    author: str = None
) -> ToolResult:
    """
    Convert Markdown to WeChat-compatible HTML.
    
    Args:
        markdown: Input markdown string
        standalone: If True, wrap output in complete HTML document
        title: Document title (for standalone mode)
        author: Document author (for standalone mode)
        
    Returns:
        ToolResult with converted HTML and metadata
        
    Example:
        >>> result = convert("# Hello\\n\\nThis is **bold** text")
        >>> if result.success:
        ...     print(result.html)
    """
    result = convert_markdown_to_wechat(markdown)
    
    if not result.success:
        return ToolResult(
            success=False,
            error=result.error
        )
    
    html_content = result.data['html']
    
    if standalone:
        html_content = create_wechat_html_document(
            title=title,
            content=html_content,
            author=author
        )
    
    return ToolResult(
        success=True,
        data={
            'html': html_content,
            'code_blocks': result.data['code_blocks'],
        },
        metadata=result.metadata
    )


def get_version() -> str:
    """Get the current version of md2wx."""
    from md2wx import __version__
    return __version__


__all__ = [
    "ToolResult",
    "convert",
    "escape_html",
    "clean_html_for_wechat",
    "get_version",
]
