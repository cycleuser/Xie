"""
Command-line interface for xie.
"""
import argparse
import sys
import json
from pathlib import Path

from xie import __version__
from xie.core import (
    convert_markdown_to_wechat,
    create_wechat_html_document,
    ToolResult,
)


def convert_handler(args):
    """Handle conversion arguments."""
    if not args.input:
        if sys.stdin.isatty():
            print("Error: No input provided. Provide a file path or pipe input.", file=sys.stderr)
            sys.exit(1)
        args.input = sys.stdin.read()
    
    if args.verbose and not args.quiet:
        print(f"[xie] Processing input ({len(args.input)} chars)...")
    
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
        print(f"[xie] Output length: {len(output)} chars")
        print(f"[xie] Code blocks: {result.metadata.get('code_blocks_count', 0)}")


def gui_handler(args):
    """Launch GUI interface."""
    from xie.gui import main as gui_main
    gui_main()


def web_handler(args):
    """Start web server."""
    from xie.app import run_server
    run_server(host=args.host, port=args.port, debug=args.debug)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="xie",
        description="Convert Markdown to WeChat Public Account HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"xie {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    convert_parser = subparsers.add_parser("convert", help="Convert markdown to HTML")
    convert_parser.add_argument(
        "input",
        nargs="?",
        help="Input markdown file or markdown text"
    )
    convert_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    convert_parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )
    convert_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON"
    )
    convert_parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress output"
    )
    convert_parser.add_argument(
        "--title",
        default="Untitled",
        help="Document title (default: 'Untitled')"
    )
    convert_parser.add_argument(
        "--author",
        help="Document author"
    )
    convert_parser.add_argument(
        "--standalone",
        action="store_true",
        help="Create standalone HTML document with styles"
    )
    convert_parser.set_defaults(handler=convert_handler)
    
    subparsers.add_parser("gui", help="Launch GUI interface").set_defaults(handler=gui_handler)
    
    web_parser = subparsers.add_parser("web", help="Start web server")
    web_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    web_parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind to (default: 5000)"
    )
    web_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    web_parser.set_defaults(handler=web_handler)
    
    args = parser.parse_args()
    
    if args.command is None:
        if sys.stdin.isatty():
            parser.print_help()
            sys.exit(0)
        args.input = sys.stdin.read()
        args.verbose = False
        args.quiet = False
        args.output = None
        args.json_output = False
        args.title = "Untitled"
        args.author = None
        args.standalone = False
        args.handler = convert_handler
    
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()
        sys.exit(0)


def run_as_module():
    """Run as python -m xie."""
    main()


if __name__ == "__main__":
    main()
