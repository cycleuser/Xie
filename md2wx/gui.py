"""
GUI interface for md2wx using PySide6.
"""
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QGroupBox, QFileDialog, QMessageBox,
    QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt

from md2wx.core import (
    convert_markdown_to_wechat,
    create_wechat_html_document,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MD2WX - Markdown to WeChat HTML Converter")
        self.setMinimumSize(1000, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        title_group = QGroupBox("Document Settings")
        title_layout = QHBoxLayout(title_group)
        title_layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Document title")
        self.title_edit.setText("Untitled")
        title_layout.addWidget(self.title_edit)
        title_layout.addWidget(QLabel("Author:"))
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Author name (optional)")
        title_layout.addWidget(self.author_edit)
        self.standalone_cb = QCheckBox("Standalone HTML")
        self.standalone_cb.setChecked(True)
        title_layout.addWidget(self.standalone_cb)
        main_layout.addWidget(title_group)
        
        editor_group = QGroupBox("Editor")
        editor_layout = QHBoxLayout(editor_group)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste or type markdown here...\n\nSupported markdown:\n- Headers (h1-h6)\n- Bold, italic, underline, strikethrough\n- Links and images\n- Code blocks with syntax highlighting\n- Tables\n- Lists (ordered and unordered)\n- Blockquotes")
        self.input_text.setMinimumWidth(400)
        editor_layout.addWidget(self.input_text)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("WeChat-compatible HTML output will appear here...")
        self.output_text.setMinimumWidth(400)
        editor_layout.addWidget(self.output_text)
        
        main_layout.addWidget(editor_group, 1)
        
        button_group = QGroupBox()
        button_layout = QHBoxLayout(button_group)
        
        self.convert_btn = QPushButton("Convert to WeChat HTML")
        self.convert_btn.clicked.connect(self.convert_markdown)
        button_layout.addWidget(self.convert_btn)
        
        self.copy_btn = QPushButton("Copy HTML to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        button_layout.addWidget(self.copy_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)
        
        self.load_btn = QPushButton("Load Markdown File")
        self.load_btn.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("Save HTML")
        self.save_btn.clicked.connect(self.save_html)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(button_group)
        
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
    
    def convert_markdown(self):
        """Convert input markdown to WeChat HTML."""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            QMessageBox.warning(self, "Warning", "Please enter some markdown text.")
            return
        
        result = convert_markdown_to_wechat(input_text)
        
        if not result.success:
            QMessageBox.critical(self, "Error", f"Conversion failed:\n{result.error}")
            return
        
        html_content = result.data['html']
        
        if self.standalone_cb.isChecked():
            html_content = create_wechat_html_document(
                title=self.title_edit.text() or "Untitled",
                content=html_content,
                author=self.author_edit.text() or None
            )
        
        self.output_text.setPlainText(html_content)
        self.copy_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        
        self.status_label.setText(
            f"Converted successfully | Input: {result.metadata['input_length']} chars | "
            f"Output: {result.metadata['output_length']} chars | "
            f"Code blocks: {result.metadata.get('code_blocks_count', 0)}"
        )
    
    def copy_to_clipboard(self):
        """Copy output HTML to clipboard."""
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        self.status_label.setText("HTML copied to clipboard")
    
    def clear_all(self):
        """Clear all input and output."""
        self.input_text.clear()
        self.output_text.clear()
        self.title_edit.setText("Untitled")
        self.author_edit.clear()
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status_label.setText("Ready")
    
    def load_file(self):
        """Load markdown file."""
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
                self.status_label.setText(f"Loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def save_html(self):
        """Save HTML output to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save HTML File",
            "",
            "HTML Files (*.html);;All Files (*)"
        )
        
        if file_path:
            try:
                Path(file_path).write_text(
                    self.output_text.toPlainText(),
                    encoding='utf-8'
                )
                self.status_label.setText(f"Saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")


def main():
    """GUI entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
