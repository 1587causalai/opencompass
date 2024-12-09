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

# 本地运行使用此命令
sphinx-autobuild . _build/html --port 8000 --open-browser

# 在远程服务器上运行需使用此命令（允许远程访问）
sphinx-autobuild . _build/html --port 8000 --host 0.0.0.0
```

这种方法的优势：
- 自动检测文件变化并重新构建
- 自动刷新浏览器页面
- 提供本地服务器，可以通过 http://localhost:8000 访问
- 支持多设备预览（同一局域网内可访问）

如果遇到 `locale.Error: unsupported locale setting` 错误，可以通过设置以下环境变量解决：

```bash
export LC_ALL=C.UTF-8 && export LANG=C.UTF-8
```

如果是云端服务器, 可能需要端口转发:

```bash
# 在本地终端执行以下命令进行端口转发
ssh -L 8000:localhost:8000 -p 44773 root@ssh.intern-ai.org.cn -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
```

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
   - 交叉引用链接是否正确（使用相对路径）

2. 如果预览服务器启动失败：
   - 检查端口是否被占用
   - 确认是否安装了所需依赖
   - 检查 Python 环境是否正确

3. 常见警告处理：
   - `myst.xref_missing`: 检查交叉引用链接是否正确，确保目标文件和锚点存在
   - 使用相对路径而不是绝对路径进行文档内链接
   - 确保引用的文件名和路径大小写正确
   - 对于外部链接，使用完整的 URL（包含 http:// 或 https://）