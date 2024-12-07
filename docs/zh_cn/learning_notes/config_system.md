# OpenCompass 配置系统详解

## 1. 从一个简单的评测说起

### 1.1 最简单的评测脚本
让我们先看一个最基础的评测脚本 `demo_eval.py`：

```python
def main():
    # 直接在代码中硬编码配置
    model_cfg = dict(
        type='HuggingFace',
        path='/path/to/model',
        tokenizer_path='/path/to/tokenizer'
    )
    dataset_cfg = dict(
        type='GSM8KDataset',
        path='data/gsm8k'
    )
    # ... 评测逻辑
```

### 1.2 遇到的问题
当我们需要评测不同模型或数据集时，这种硬编码方式会带来以下问题：
1. 需要频繁修改代码
2. 配置难以复用
3. 不便于版本控制
4. 难以进行批量实验

## 2. 配置系统的解决方案

### 2.1 使用配置文件
```python
# configs/eval_tiny_demo.py
# 将配置移到单独的配置文件
models = [
    dict(
        type='HuggingFace',
        path='/path/to/model',
        tokenizer_path='/path/to/tokenizer'
    )
]

datasets = [
    dict(
        type='GSM8KDataset',
        path='data/gsm8k'
    )
]
```

### 2.2 配置的加载
```python
# opencompass/run.py
from mmengine.config import Config

def main():
    # 从文件加载配置
    cfg = Config.fromfile('configs/eval_tiny_demo.py')
    # 现在可以通过cfg优雅地访问所有配置
    model_cfg = cfg.models[0]
    dataset_cfg = cfg.datasets[0]
```

## 3. 配置系统的进阶特性

### 3.1 配置继承
当我们需要评测多个相似的模型时：
```python
# configs/models/base_model.py
# 基础模型配置
base_model = dict(
    type='HuggingFace',
    tokenizer_kwargs=dict(trust_remote_code=True),
    max_out_len=100,
    batch_size=1
)

# 特定模型继承基础配置
internlm_model = {
    **base_model,
    'path': 'internlm/internlm-chat-7b',
    'tokenizer_path': 'internlm/internlm-chat-7b'
}
```

### 3.2 动态修改
在实验过程中经常需要调整参数，OpenCompass 提供了多种方式来动态修改配置：

1. 使用命令行参数
```bash
# 修改模型参数
python run.py configs/eval_tiny_demo.py \
    --batch-size 4 \
    --max-seq-len 2048 \
    --hf-num-gpus 1  # 注意：使用 hf-num-gpus 而不是 num-gpus

# 修改模型路径
python run.py configs/eval_tiny_demo.py \
    --hf-path /path/to/model \
    --tokenizer-path /path/to/tokenizer

# 更多高级参数
python run.py configs/eval_tiny_demo.py \
    --hf-num-gpus 1 \
    --max-out-len 2048 \
    --min-out-len 1 \
    --temperature 0.7 \
    --top-p 0.8
```

2. 通过环境变量
```bash
# 设置环境变量来修改配置
export OPENCOMPASS_BATCH_SIZE=4
export OPENCOMPASS_HF_NUM_GPUS=1  # 注意：使用 HF_NUM_GPUS
python run.py configs/eval_tiny_demo.py
```

3. 在配置文件中使用变量
```python
# configs/eval_dynamic.py
import os

batch_size = int(os.getenv('BATCH_SIZE', '1'))
hf_num_gpus = int(os.getenv('HF_NUM_GPUS', '1'))  # 注意：使用 HF_NUM_GPUS
models = [
    dict(
        type='HuggingFace',
        path='internlm/internlm-chat-7b',
        batch_size=batch_size,
        num_gpus=hf_num_gpus  # 在配置中使用
    )
]
```

OpenCompass 支持的���要命令行参数包括：
- `--models`: 指定要评测的模型
- `--datasets`: 指定要使用的数据集
- `--batch-size`: 批处理大小
- `--max-seq-len`: 最大序列长度
- `--hf-num-gpus`: HuggingFace 模型使用的 GPU 数量
- `--hf-path`: HuggingFace 模型路径
- `--tokenizer-path`: 分词器路径
- `--work-dir`: 工作目录
- `--max-out-len`: 最大输出长度
- `--min-out-len`: 最小输出长度
- `--temperature`: 采样温度
- `--top-p`: Top-p 采样参数
- 更多参数可以通过 `python run.py --help` 查看
## 4. 实际应用案例

### 4.1 评测不同模型
```python
# configs/eval_multiple_models.py
from .models.internlm import internlm_model
from .models.llama import llama_model

models = [
    internlm_model,
    llama_model
]
```

### 4.2 组合不同数据集
```python
# configs/eval_comprehensive.py
from .datasets.gsm8k import gsm8k_datasets
from .datasets.humaneval import humaneval_datasets

datasets = [
    *gsm8k_datasets,    # 数学能力评测
    *humaneval_datasets # 编程能力评测
]
```

## 5. 最佳实践与注意事项

### 5.1 配置文件组织

```bash
configs/
├── models/
│   ├── internlm/
│   │   └── internlm_chat_7b.py
│   └── llama/
│       └── llama2_7b.py
├── datasets/
│   ├── gsm8k/
│   └── humaneval/
└── eval_tiny_demo.py
```

### 5.2 调试技巧

```python
# 打印完整配置
print(cfg.pretty_text)

# 检查特定配置
print(f"评测模型: {cfg.models[0].path}")
print(f"评测数据集: {cfg.datasets[0].path}")
```

## 6. 常见问题

### Q1: 如何确认配置是否正确加载？
```python
# 在运行评测前打印关键配置
print(f"将评测以下模型:")
for model in cfg.models:
    print(f"- {model.path}")
```

### Q2: 配置文件修改后不生效？
- 检查Python缓存文件
- 确认修改的是正确的配置文件
- 验证配置继承关系

## 7. 参考资料

- [MMEngine配置系统文档](https://mmengine.readthedocs.io/zh_CN/latest/advanced_tutorials/config.html)
- [OpenCompass配置示例](https://github.com/open-compass/opencompass/tree/main/configs)



```
