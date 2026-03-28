"""
Web interface for xie using Flask.
"""
from flask import Flask, render_template, jsonify, request

from xie.core import convert_markdown_to_wechat, create_wechat_html_document


app = Flask(__name__, template_folder='templates')


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.json
    
    if not data or 'markdown' not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'markdown' field in request body"
        }), 400
    
    markdown_text = data['markdown']
    standalone = data.get('standalone', False)
    title = data.get('title', 'Untitled')
    author = data.get('author')
    
    result = convert_markdown_to_wechat(markdown_text)
    
    if not result.success:
        return jsonify({
            "success": False,
            "error": result.error
        }), 500
    
    html_content = result.data['html']
    
    if standalone:
        html_content = create_wechat_html_document(
            title=title,
            content=html_content,
            author=author
        )
    
    return jsonify({
        "success": True,
        "html": html_content,
        "code_blocks": result.data['code_blocks'],
        "metadata": result.metadata
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "xie"})


def run_server(host="127.0.0.1", port=5000, debug=False):
    """Run the Flask server."""
    print(f"Starting Xie server at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)
