"""
GUI interface for xie using PySide6.
"""
import sys
import re
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QGroupBox, QFileDialog, QMessageBox,
    QCheckBox, QSplitter, QStatusBar, QToolBar, QFontComboBox
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QTextCursor

from xie.core import (
    convert_markdown_to_wechat,
    create_wechat_html_document,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xie - Markdown to WeChat")
        self.setMinimumSize(1200, 800)
        self.last_html_content = ""

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.create_toolbar()

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 0)

        settings_bar = QWidget()
        settings_bar.setFixedHeight(50)
        settings_layout = QHBoxLayout(settings_bar)
        settings_layout.setContentsMargins(0, 5, 0, 5)

        settings_layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Document title")
        self.title_edit.setText("Untitled")
        self.title_edit.setFixedWidth(200)
        settings_layout.addWidget(self.title_edit)

        settings_layout.addWidget(QLabel("Author:"))
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Author (optional)")
        self.author_edit.setFixedWidth(150)
        settings_layout.addWidget(self.author_edit)

        settings_layout.addStretch()

        self.convert_btn = QPushButton("🔄 Convert")
        self.convert_btn.setFixedSize(120, 35)
        self.convert_btn.clicked.connect(self.convert_markdown)
        settings_layout.addWidget(self.convert_btn)

        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setFixedSize(100, 35)
        self.clear_btn.clicked.connect(self.clear_all)
        settings_layout.addWidget(self.clear_btn)

        content_layout.addWidget(settings_bar)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = self.create_editor_panel()
        right_panel = self.create_preview_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        content_layout.addWidget(splitter, 1)

        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(30)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(QLabel("Markdown → WeChat HTML"))
        main_layout.addWidget(self.status_bar)

        self.input_text.textChanged.connect(self.on_input_changed)

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setFixedHeight(45)
        toolbar.setMovable(False)

        title_label = QLabel("  Xie  ")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #667eea;")
        toolbar.addWidget(title_label)

        toolbar.addSeparator()

        self.copy_wechat_btn = QPushButton("📋 Copy for WeChat")
        self.copy_wechat_btn.setFixedSize(150, 32)
        self.copy_wechat_btn.setEnabled(False)
        self.copy_wechat_btn.clicked.connect(self.copy_for_wechat)
        toolbar.addWidget(self.copy_wechat_btn)

        self.show_html_btn = QPushButton("代码 Show HTML")
        self.show_html_btn.setFixedSize(130, 32)
        self.show_html_btn.setCheckable(True)
        self.show_html_btn.clicked.connect(self.toggle_html_view)
        toolbar.addWidget(self.show_html_btn)

        toolbar.addSeparator()

        self.load_btn = QPushButton("📂 Open")
        self.load_btn.setFixedSize(100, 32)
        self.load_btn.clicked.connect(self.load_file)
        toolbar.addWidget(self.load_btn)

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setFixedSize(100, 32)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_html)
        toolbar.addWidget(self.save_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self.char_count_label = QLabel("0 chars")
        self.char_count_label.setStyleSheet("color: #888; font-size: 12px;")
        toolbar.addWidget(self.char_count_label)

        toolbar.addSpacing(20)

        self.code_block_label = QLabel("0 code blocks")
        self.code_block_label.setStyleSheet("color: #888; font-size: 12px;")
        toolbar.addWidget(self.code_block_label)

        self.addToolBar(toolbar)

    def create_editor_panel(self):
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background: #fff;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("📝 Markdown Editor")
        header.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                padding: 12px 15px;
                font-weight: bold;
                font-size: 14px;
                border-bottom: 1px solid #e5e5e5;
            }
        """)
        header.setFixedHeight(45)
        layout.addWidget(header)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("# Start writing your markdown here...\n\nSupported syntax:\n- **bold** or __bold__\n- *italic* or _italic_\n- ~~strikethrough~~\n- [link](url)\n- ![image](url)\n- ```code blocks```\n- > blockquotes\n- - unordered lists\n- 1. ordered lists\n- | tables | are | supported |")
        self.input_text.setFont(QFont("SF Mono", 13))
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 15px;
                background: #fefefe;
            }
            QTextEdit:focus {
                background: #fff;
            }
        """)
        layout.addWidget(self.input_text)

        return panel

    def create_preview_panel(self):
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background: #fff;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("👁️ Live Preview")
        header.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                padding: 12px 15px;
                font-weight: bold;
                font-size: 14px;
                border-bottom: 1px solid #e5e5e5;
            }
        """)
        header.setFixedHeight(45)
        layout.addWidget(header)

        self.preview_browser = QTextEdit()
        self.preview_browser.setReadOnly(True)
        self.preview_browser.setOpenExternalLinks(True)
        self.preview_browser.setPlaceholderText("Converted WeChat-compatible HTML preview will appear here...")
        self.preview_browser.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 20px;
                background: #fafafa;
            }
        """)
        layout.addWidget(self.preview_browser)

        self.html_browser = QTextEdit()
        self.html_browser.setReadOnly(True)
        self.html_browser.setFont(QFont("SF Mono", 11))
        self.html_browser.setVisible(False)
        self.html_browser.setPlaceholderText("HTML source code...")
        self.html_browser.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 15px;
                background: #2d2d2d;
                color: #f8f8f2;
            }
        """)
        layout.addWidget(self.html_browser)

        return panel

    def on_input_changed(self):
        text = self.input_text.toPlainText()
        self.char_count_label.setText(f"{len(text)} chars")

    def convert_to_wechat_html(self, html_content):
        """Convert full HTML document to WeChat-compatible inline-styled HTML."""
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
        if body_match:
            body_content = body_match.group(1)
        else:
            body_content = html_content

        body_content = re.sub(r'<h1[^>]*>', '<h1 style="text-align:center;font-size:24px;font-weight:bold;margin:20px 0;">', body_content)
        body_content = re.sub(r'<h2[^>]*>', '<h2 style="font-size:22px;font-weight:bold;margin:18px 0 10px;">', body_content)
        body_content = re.sub(r'<h3[^>]*>', '<h3 style="font-size:20px;font-weight:bold;margin:15px 0 8px;">', body_content)
        body_content = re.sub(r'<h4[^>]*>', '<h4 style="font-size:18px;font-weight:bold;margin:15px 0 8px;">', body_content)
        body_content = re.sub(r'<h5[^>]*>', '<h5 style="font-size:16px;font-weight:bold;margin:10px 0 5px;">', body_content)
        body_content = re.sub(r'<h6[^>]*>', '<h6 style="font-size:15px;font-weight:bold;margin:10px 0 5px;">', body_content)

        body_content = re.sub(r'<p[^>]*>', '<p style="margin:10px 0;line-height:1.8;">', body_content)
        body_content = re.sub(r'<a[^>]*>', '<a style="color:#576b95;text-decoration:none;">', body_content)
        body_content = re.sub(r'<blockquote[^>]*>', '<blockquote style="border-left:3px solid #e5e5e5;padding:5px 10px;margin:10px 0;color:#666;background:#f9f9f9;">', body_content)
        body_content = re.sub(r'<pre[^>]*>', '<pre style="background:#f6f8fa;border-radius:4px;padding:15px;overflow-x:auto;margin:10px 0;font-family:monospace;font-size:14px;line-height:1.5;">', body_content)
        body_content = re.sub(r'<code(?![^>]*class=)[^>]*>', '<code style="background:#f6f8fa;padding:2px 6px;border-radius:3px;font-family:monospace;font-size:13px;color:#e83e8c;">', body_content)
        body_content = re.sub(r'<img([^>]*)>', lambda m: '<img' + re.sub(r'\s*(style|width|height)="[^"]*"', '', m.group(1)) + ' style="max-width:100%;height:auto;display:block;margin:10px 0;"/>', body_content)

        body_content = re.sub(r'class="[^"]*"', '', body_content)
        body_content = re.sub(r'\s+', ' ', body_content)
        body_content = re.sub(r'>\s+<', '><', body_content)

        return body_content.strip()

    def convert_markdown(self):
        input_text = self.input_text.toPlainText().strip()

        if not input_text:
            QMessageBox.warning(self, "Warning", "Please enter some markdown text.")
            return

        result = convert_markdown_to_wechat(input_text)

        if not result.success:
            QMessageBox.critical(self, "Error", f"Conversion failed:\n{result.error}")
            return

        html_content = result.data['html']

        if self.title_edit.text() or self.author_edit.text():
            html_content = create_wechat_html_document(
                title=self.title_edit.text() or "Untitled",
                content=html_content,
                author=self.author_edit.text() or None
            )

        self.last_html_content = html_content
        self.wechat_html = self.convert_to_wechat_html(html_content)

        self.html_browser.setPlainText(self.wechat_html)
        self.preview_browser.setHtml(html_content)

        self.copy_wechat_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

        self.code_block_label.setText(f"{result.metadata.get('code_blocks_count', 0)} code blocks")
        self.status_label.setText("✓ Converted successfully")

    def toggle_html_view(self, checked):
        if checked:
            self.preview_browser.setVisible(False)
            self.html_browser.setVisible(True)
            self.show_html_btn.setText("👁️ Show Preview")
        else:
            self.preview_browser.setVisible(True)
            self.html_browser.setVisible(False)
            self.show_html_btn.setText("代码 Show HTML")

    def copy_for_wechat(self):
        if not self.wechat_html:
            QMessageBox.warning(self, "Warning", "Please convert markdown first.")
            return

        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()

        clipboard.setText(self.wechat_html)

        self.status_label.setText("✓ Copied! Paste directly into WeChat editor (Ctrl+V)")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))

    def clear_all(self):
        self.input_text.clear()
        self.title_edit.setText("Untitled")
        self.author_edit.clear()
        self.preview_browser.clear()
        self.html_browser.clear()
        self.last_html_content = ""
        self.wechat_html = ""
        self.copy_wechat_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.code_block_label.setText("0 code blocks")
        self.char_count_label.setText("0 chars")
        self.status_label.setText("Ready")

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )

        if file_path:
            try:
                content = Path(file_path).read_text(encoding='utf-8')
                self.input_text.setPlainText(content)
                self.title_edit.setText(Path(file_path).stem)
                self.status_label.setText(f"📂 Loaded: {Path(file_path).name}")
                QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def save_html(self):
        if not self.last_html_content:
            QMessageBox.warning(self, "Warning", "Please convert markdown first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save HTML File",
            "",
            "HTML Files (*.html);;All Files (*)"
        )

        if file_path:
            try:
                Path(file_path).write_text(self.last_html_content, encoding='utf-8')
                self.status_label.setText(f"✓ Saved: {Path(file_path).name}")
                QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def keyPressEvent(self, event):
        if (event.modifiers() == Qt.KeyboardModifier.ControlModifier or
            event.modifiers() == Qt.KeyboardModifier.MetaModifier) and \
            event.key() == Qt.Key.Key_Return:
            self.convert_markdown()
        else:
            super().keyPressEvent(event)


def main():
    from PySide6.QtWidgets import QSizePolicy
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, palette.Color(255, 255, 255))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
