# Xie

一行命令把 Markdown 转成微信公众号可用的 HTML。支持命令行、Python 库、桌面 GUI 和网页版。

## 解决的问题

用 Markdown 写完文章，想发到微信公众号，还得手动转 HTML？微信公众号只支持部分 HTML 标签，普通转换器输出的代码粘贴过去格式全乱。

Xie 自动处理这些兼容性问题，输出的是微信公众号编辑器能正确解析的 HTML，复制粘贴即可。

## 快速上手

```bash
# 安装
pip install xie

# 转换文件
xie input.md -o output.html

# 管道输入
echo "# 你好" | xie
```

## 安装方式

```bash
# 从 PyPI 安装
pip install xie

# 带上 GUI 和网页支持
pip install xie[all]

# 从源码安装
git clone https://github.com/cycleuser/xie.git
cd xie
pip install -e .
```

## 三种使用方式

### 命令行

```bash
# 基本转换
xie 文章.md -o 文章.html

# 生成完整文档（含标题、作者、样式）
xie 文章.md --standalone --title "我的文章" --author "张三" -o 文章.html

# JSON 格式输出
xie 文章.md --json > result.json
```

### Python 库

```python
from xie import convert

result = convert("# 你好\n\n这是**粗体**文本", standalone=True)
if result.success:
    print(result.html)
```

### 图形界面或网页

```bash
# 启动桌面 GUI
xie gui

# 启动网页服务
xie web --port 5000
```

网页版在 http://localhost:5000 打开，左边写 Markdown，右边实时预览微信公众号效果，点"复制到微信"直接获取可粘贴的 HTML。

## 功能特点

支持标准 Markdown 语法：标题、粗体、斜体、链接、图片、代码块、表格、引用、列表。

另外还支持：

- **代码高亮**：基于 Pygments，支持 100+ 编程语言，颜色以内联样式输出，不依赖外部 CSS
- **LaTeX 数学公式**：`$行内$` 和 `$$块级$$` 语法
- **微信公众号样式**：链接、图片、代码块都做了微信风格的适配

## 支持的语法

```
# 标题           **粗体**        *斜体*        ~~删除线~~
[链接](地址)    ![图片](地址)   `行内代码`    ```语言
> 引用           - 无序列表      1. 有序列表    | 表格 |
$行内公式$      $$块级公式$$
```

## 微信兼容说明

微信公众号对 HTML 有限制，Xie 只输出微信支持的标签和样式：

- 所有样式都是内联属性（无 `<style>` 标签或 CSS 类）
- 链接颜色默认为微信蓝 (#576b95)
- 图片自适应宽度
- 代码块使用内联颜色，不依赖外部样式表

## 环境要求

- Python 3.8+
- mistune（Markdown 解析）
- Pygments（代码高亮）

可选依赖：PySide6（桌面 GUI）、Flask（网页服务）

## 开源协议

GPLv3
