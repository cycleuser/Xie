"""
Command-line interface for md2wx.
"""
import argparse
import sys
import json
from pathlib import Path

from md2wx.core import (
    convert_markdown_to_wechat,
    create_wechat_html_document,
    ToolResult,
)


__version__ = "1.0.0"


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="md2wx",
        description="Convert Markdown to WeChat Public Account HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  md2wx input.md -o output.html
  md2wx input.md --json
  md2wx "Hello **world**" -o output.html
  md2wx -v input.md -o output.html
        """
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"md2wx {__version__}"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress output"
    )
    parser.add_argument(
        "--title",
        default="Untitled",
        help="Document title (default: 'Untitled')"
    )
    parser.add_argument(
        "--author",
        help="Document author"
    )
    parser.add_argument(
        "--standalone",
        action="store_true",
        help="Create standalone HTML document with styles"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input markdown file or markdown text"
    )
    
    args = parser.parse_args()
    
    if not args.input:
        if sys.stdin.isatty():
            parser.print_help()
            sys.exit(0)
        args.input = sys.stdin.read()
    
    if args.verbose and not args.quiet:
        print(f"[md2wx] Processing input ({len(args.input)} chars)...")
    
    result = convert_markdown_to_wechat(args.input)
    
    if not result.success:
        if not args.quiet:
            print(f"Error: {result.error}", file=sys.stderr)
        sys.exit(1)
    
    html_content = result.data['html']
    
    if args.standalone:
        html_content = create_wechat_html_document(
            title=args.title,
            content=html_content,
            author=args.author
        )
    
    if args.json_output:
        output_data = {
            "success": True,
            "html": html_content,
            "code_blocks": result.data['code_blocks'],
            "metadata": result.metadata
        }
        output = json.dumps(output_data, indent=2, ensure_ascii=False)
    elif args.output:
        output = html_content
    else:
        output = html_content
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output, encoding='utf-8')
        if not args.quiet:
            print(f"Output written to {args.output}")
    else:
        print(output)
    
    if args.verbose and not args.quiet:
        print(f"[md2wx] Output length: {len(output)} chars")
        print(f"[md2wx] Code blocks: {result.metadata.get('code_blocks_count', 0)}")


def run_as_module():
    """Run as python -m md2wx."""
    main()


if __name__ == "__main__":
    main()
