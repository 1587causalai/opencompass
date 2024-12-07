# OpenCompass 文档开发笔记

## 文档预览方法

在开发 OpenCompass 文档时，我们有多种方式来预览文档效果：

### 1. 基础预览方法

```bash
cd docs/zh_cn
make html
```

构建完成后，可以在 `_build/html` 目录下找到生成的网页文件，用浏览器打开 `index.html` 文件即可预览。

### 2. 实时预览方法（推荐）

使用 Sphinx 的自动重载服务器，可以实现文件修改后自动重新构建和预览：

```bash
cd docs/zh_cn
sphinx-autobuild . _build/html --port 8000 --open-browser
```

这种方法的优势：
- 自动检测文件变化并重新构建
- 自动刷新浏览器页面
- 提供本地服务器，可以通过 http://localhost:8000 访问
- 支持多设备预览（同一局域网内可访问）

### 3. VS Code 插件方法

如果你使用 VS Code 编辑器，可以安装以下插件来增强文档开发体验：
- `reStructuredText` 插件：提供 rst 文件的语法高亮和预览
- `Markdown All in One`：提供 markdown 文件的增强编辑功能
- `Markdown Preview Enhanced`：提供实时预览功能

## 文档开发最佳实践

1. 使用实时预览功能进行开发，可以立即看到修改效果
2. 在提交前使用 `make html` 进行完整构建，确保没有错误
3. 检查生成的文档中的链接是否正确
4. 确保文档风格统一，遵循项目的文档规范

## 常见问题解决

1. 如果遇到构建错误，检查：
   - 文件格式是否正确（rst/md）
   - 文件编码是否为 UTF-8
   - 图片路径是否正确
   - 是否有未闭合的标签

2. 如果预览服务器启动失败：
   - 检查端口是否被占用
   - 确认是否安装了所需依赖
   - 检查 Python 环境是否正确 