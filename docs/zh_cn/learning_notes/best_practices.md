# OpenCompass 实用工具

## 下载数据集


```bash
# wget https://github.com/open-compass/opencompass/releases/download/0.1.1/OpenCompassData.zip
# 下载0.1.8数据集
wget https://github.com/open-compass/opencompass/releases/download/0.1.8.rc1/OpenCompassData-core-20231110.zip
unzip OpenCompassData-core-20231110.zip
```

## Prompt 调试工具

在评测过程中，我们经常需要检查和调试 prompt。OpenCompass 提供了便捷的 prompt 查看工具，可以帮助我们直观地了解模型实际接收到的输入内容。

### 使用方法

```bash
python tools/prompt_viewer.py CONFIG_PATH [-n] [-a] [-p PATTERN]
```

参数说明：
- `CONFIG_PATH`: 配置文件路径
- `-n`: 不进入交互模式，默认选择第一个模型和数据集
- `-a`: 查看所有模型和数据集组合的 prompt
- `-p PATTERN`: 使用正则表达式匹配数据集

### 实践案例

以下是一个查看 DeepSeek API 评测配置中 prompt 的示例：

```bash
python tools/prompt_viewer.py configs/api_examples/eval_api_deepseek.py
```

输出示例：
```
Number of tokens: 278
----------------------------------------------------------------------------------------------------
Sample prompt:
----------------------------------------------------------------------------------------------------
Question: Mark's basketball team scores 25 2 pointers, 8 3 pointers and 10 free throws...
Let's think step by step
Answer: ...
```

### 使用场景

1. **Prompt 调试**
   - 在评测前预览实际的 prompt 内容
   - 检查 prompt 格式是否符合预期
   - 验证 system prompt 是否正确设置

2. **Token 长度优化**
   - 查看 prompt 的 token 数量
   - 及时发现可能超出模型最大长度限制的情况

3. **模板验证**
   - 确认数据集模板是否正确应用
   - 检查思维链提示词是否按预期添加

### 最佳实践

1. 在启动大规模评测前，建议先使用 prompt_viewer 检查配置：
   ```bash
   # 查看单个数据集的 prompt
   python tools/prompt_viewer.py configs/your_config.py
   
   # 查看所有数据集的 prompt
   python tools/prompt_viewer.py configs/your_config.py -a
   ```

2. 对于新创建的数据集，使用此工具验证 prompt 模板：
   ```bash
   python tools/prompt_viewer.py configs/datasets/your_dataset/your_dataset_config.py
   ```

3. 在调试复杂的多模型评测时，使用 `-p` 参数筛选特定数据集：
   ```bash
   python tools/prompt_viewer.py configs/your_config.py -p "math|reasoning"
   ```



## 评测结果分析工具

在完成模型评测后，我们需要深入分析模型的表现。OpenCompass 提供了 Case Analyzer 工具，帮助我们查看详细的评测结果。

### 使用方法

```bash
python tools/case_analyzer.py CONFIG_PATH [-w WORK_DIR]
```

参数说明：
- `CONFIG_PATH`: 评测配置文件路径
- `-w WORK_DIR`: 评测结果所在的工作目录，默认为 './outputs/default'

### 实践案例

以下是分析 DeepSeek API 在 GSM8K 数据集上评测结果的示例：

```bash
# 运行评测
python run.py configs/api_examples/eval_api_deepseek.py

# 分析评测结果（使用实际的输出目录）
python tools/case_analyzer.py configs/api_examples/eval_api_deepseek.py -w outputs/api_deepseek_math/20241209_155513
```


## API 模型测试工具

在使用 API 模型进行评测之前，我们需要确保 API 配置正确且能正常工作。OpenCompass 提供了专门的 API 测试工具。

### 使用方法

```bash
python tools/test_api_model.py [CONFIG_PATH] -n
```

参数说明：
- `CONFIG_PATH`: API 模型配置文件路径
- `-n`: 非交互模式，直接执行测试

### 实践案例

让我们测试 DeepSeek API 配置是否正常工作：

```bash
# 测试 DeepSeek API 配置
python tools/test_api_model.py configs/api_examples/eval_api_deepseek.py -n
```



## List Configs

本工具可以列出或搜索所有可用的模型和数据集配置，且支持模糊搜索，便于结合 `run.py` 使用。

运行方式：

```bash
python tools/list_configs.py [PATTERN1] [PATTERN2] [...]
```

若运行时不加任何参数，则默认列出所有在 `configs/models` 和 `configs/dataset` 下的模型配置。

用户同样可以传入任意数量的参数，脚本会列出所有跟传入字符串相关的配置，支持模糊搜索及 * 号匹配。如下面的命令会列出所有跟 `mmlu` 和 `llama` 相关的配置：

```bash
python tools/list_configs.py mmlu llama
```