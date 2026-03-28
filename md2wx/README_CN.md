# Markdown 转微信公众号 HTML 转换器

一款命令行工具和 Python 库，用于将 Markdown 文档转换为微信公众号兼容的 HTML 格式。

## 项目背景

Markdown 因其简洁的语法和良好的可读性已成为技术文档和内容创作的事实标准。然而，微信公众号仅支持有限的 HTML 子集进行格式排版。这给使用 Markdown 写作但需要在微信发布的内容创作者带来了摩擦。

MD2WX 通过提供强大的转换管道来解决这个问题，将标准 Markdown 转换为微信兼容的 HTML。该工具处理微信 HTML 限制的各种复杂性，包括支持的标签、CSS 约束和代码块渲染。

本项目解决了以下实际需求：使用 Markdown 维护内容的技术作者、开发者和技术写作者需要将内容发布到微信公众号。通过自动化转换过程，MD2WX 节省了大量手动工作，并确保跨平台的一致格式。

## 应用场景

**技术文档发布**：使用 Markdown 编写 API 文档、教程或技术博客的开发人员，现在可以轻松地将它们发布到微信，而无需手动 HTML 转换。

**教育内容创作**：使用 Markdown 创建课程材料的教育工作者，可以通过微信公众账号进行分发，并保持正确的格式。

**软件产品公告**：产品团队可以在 Markdown 中维护发布说明和公告，并通过单个命令将其发布到微信。

**跨平台内容分发**：向多个平台（博客、Medium、GitHub）发布内容的创作者，可以使用相同的 Markdown 源为微信文章提供内容。

## 兼容硬件

MD2WX 是一款轻量级 Python 应用程序，硬件要求极低：

- **CPU**：任何现代 x86_64 或 ARM64 处理器
- **内存**：最低 256MB RAM；建议 512MB
- **存储**：安装空间小于 50MB
- **无需 GPU**：所有处理均基于 CPU

## 操作系统

MD2WX 支持所有主流操作系统：

- **macOS**：macOS 10.13 (High Sierra) 或更高版本
- **Linux**：Ubuntu 18.04+、Debian 10+、Fedora 30+ 以及其他带有 Python 3.8+ 的 Linux 发行版
- **Windows**：Windows 10 或更高版本（支持 WSL2 或原生 Python）

## 依赖环境

MD2WX 需要 Python 3.8 或更高版本。核心依赖包括：

- **Python**：>= 3.8
- **mistune**：>= 2.0.0（Markdown 解析器）
- **Pygments**：>= 2.14.0（代码块语法高亮）

可选依赖：

- **PySide6**：>= 6.4.0（GUI 界面）
- **Flask**：>= 2.3.0（Web 界面）
- **pytest**：>= 7.0.0（测试框架）

## 安装过程

### 从 PyPI 安装（推荐）

```bash
pip install md2wx
```

### 源码安装

```bash
git clone https://github.com/cycleuser/md2wx.git
cd md2wx
pip install -e .
```

### 安装所有依赖

```bash
pip install md2wx[all]
```

### 开发安装

```bash
git clone https://github.com/cycleuser/md2wx.git
cd md2wx
pip install -e .[dev]
```

## 使用方法

### 命令行界面

转换 Markdown 文件：

```bash
md2wx input.md -o output.html
```

从标准输入转换：

```bash
echo "# Hello World" | md2wx
```

创建带样式的独立 HTML：

```bash
md2wx input.md --standalone --title "我的文章" --author "张三" -o output.html
```

获取 JSON 格式输出用于程序调用：

```bash
md2wx input.md --json
```

详细输出模式：

```bash
md2wx -v input.md -o output.html
```

### Python API

```python
from md2wx import convert

result = convert("# 你好\n\n这是**粗体**文本", standalone=True)

if result.success:
    print(result.html)
else:
    print(f"错误: {result.error}")
```

### GUI 模式

启动图形界面：

```bash
md2wx gui
```

### Web 服务器模式

启动 Web 界面：

```bash
md2wx web --host 0.0.0.0 --port 5000
```

然后在浏览器中打开 http://localhost:5000。

## 运行截图

| GUI 界面 | Web 界面 |
|:--------:|:--------:|
| ![GUI](images/gui_placeholder.png) | ![Web](images/web_placeholder.png) |

## 命令行帮助

```
用法: md2wx [-h] [-V] [-v] [-o OUTPUT] [--json] [-q] [--title TITLE]
           [--author AUTHOR] [--standalone]
           [input]

将 Markdown 转换为微信公众号 HTML

位置参数:
  input                 输入的 Markdown 文件或文本

可选参数:
  -h, --help           显示此帮助信息并退出
  -V, --version        显示程序版本号并退出
  -v, --verbose        详细输出
  -o, --output         输出文件路径
  --json               JSON 格式输出
  -q, --quiet          抑制输出
  --title              文档标题（默认：'Untitled'）
  --author             文档作者
  --standalone         创建带样式的独立 HTML 文档
```

## 支持的 Markdown 特性

- 标题（h1-h6）
- 粗体、斜体、下划线、删除线
- 带正确微信样式的链接
- 带响应式尺寸的图片
- 带语法高亮的代码块
- 行内代码
- 微信兼容样式的引用块
- 有序和无序列表
- 带正确边框的表格
- 水平线

## 微信兼容性说明

MD2WX 生成的 HTML 符合微信的内容指南：

- 仅使用支持的 HTML 标签
- 应用微信兼容的内联样式
- 确保图片具有响应式宽度
- 为可读性格式化代码块
- 使用正确的链接颜色（#576b95）

## 授权协议

GPLv3。详见 [LICENSE](LICENSE)。
