# OpenCompass 代码能力评测教程

本教程将通过实践的方式，帮助你理解大语言模型代码能力的评测原理。我们将采用"由简入繁"的方式，先构建一个最小的评测样例，再逐步理解完整的评测系统。

## 一、评测原理速览

在开始动手之前，让我们先快速了解代码评测的核心概念：

1. **输入**: 编程问题（包含问题描述、函数签名等）
2. **输出**: 模型生成的代码实现
3. **验证**: 运行代码，检查是否通过测试用例
4. **指标**: 使用 pass@k 评估模型表现

## 二、从零开始的评测实践

### 1. 最小评测示例

让我们先创建一个最简单的评测脚本。为了方便快速实验，我们使用较小的本地模型。完整代码见 `scripts/mini_code_eval.py`，这里我们逐段解析其关键部分：

#### 1.1 模型初始化

```python
def init_model():
    """初始化模型和分词器"""
    # 使用较小的本地模型
    model_path = '/share/new_models/Shanghai_AI_Laboratory/internlm2_5-1_8b-chat'
    
    # 加载模型
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map='auto'
    )
    
    # 加载分词器
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )
    
    return model, tokenizer
```

这部分代码负责加载模型和分词器。我们选择了较小的本地模型以便快速实验。

#### 1.2 问题评测

```python
def evaluate_single_problem(model, tokenizer):
    """评测单个问题"""
    # 示例问题
    problem = '''
    写一个函数，计算两个数的最大公约数。
    函数签名: def gcd(a: int, b: int) -> int
    示例输入: gcd(12, 8)
    示例输出: 4
    '''
    
    # 构造提示词
    prompt = f"""请实现以下Python函数：\n{problem}\n请直接给出代码实现，不需要解释。\n答案："""
    
    # 生成多个答案
    predictions = []
    for i in range(3):
        outputs = model.generate(...)
        predictions.append(response)
    
    return predictions
```

这部分展示了如何构造问题和生成答案。关键点包括：
1. 清晰的问题描述
2. 完整的函数签名
3. 具体的示例
4. 多次生成尝试

#### 1.3 代码验证

```python
def verify_code(code, test_cases):
    """验证生成的代码"""
    try:
        # 执行代码
        namespace = {}
        exec(code, namespace)
        gcd_func = namespace['gcd']
        
        # 验证结果
        for inputs, expected in test_cases:
            if gcd_func(*inputs) != expected:
                return False
        return True
    except Exception as e:
        print(f"执行错误: {str(e)}")
        return False
```

这部分实现了代码验证功能：
1. 安全地执行生成的代码
2. 运行测试用例
3. 处理可能的错误

### 2. 运行评测

要运行这个示例，只需：

```bash
python scripts/mini_code_eval.py
```

你将看到类似这样的输出：
```
=== 初始化模型 ===
加载模型...
模型加载耗时: 5.23秒
加载分词器...
分词器加载耗时: 0.45秒

生成第 1 个答案...
生成耗时: 1.12秒

[生成的代码和验证结果]
```

### 3. 理解完整评测系统

通过前面的最小示例，我们已经掌握了代码评测的基本原理。现在让我们来看看 OpenCompass 的完整评测系统（eval_code_passk.py）是如何工作的。我们将通过对比最小示例来理解其中的设计思路。

#### 3.1 评测流程对比

我们的最小示例实现了一个简单直接的评测流程：
```python
def main():
    # 1. 加载模型
    model, tokenizer = init_model()
    
    # 2. 准备测试用例
    test_cases = [((12, 8), 4), ...]
    
    # 3. 运行评测
    predictions = evaluate_single_problem(model, tokenizer)
    
    # 4. 验证结果
    for code in predictions:
        verify_code(code, test_cases)
```

而在 eval_code_passk.py 中，这个流程被拆分为配置式的结构：
```python
# 1. 模型配置（对应 init_model）
models = [
    dict(
        type=HuggingFaceCausalLM,
        path='codellama/CodeLlama-7b-Python-hf',
        tokenizer_kwargs=dict(padding_side='left'),
        model_kwargs=dict(trust_remote_code=True),
        generation_kwargs=dict(
            num_return_sequences=10,  # 生成10个候选答案
            do_sample=True,
            temperature=0.8
        )
    )
]

# 2. 数据集配置（对应我们的 test_cases）
datasets = [
    humaneval_datasets,    # 标准的代码评测数据集
    mbpp_datasets         # 更多的测试数据
]

# 3. 推理配置（对应 evaluate_single_problem 和 verify_code）
infer = dict(
    partitioner=dict(type=SizePartitioner, max_task_size=300),
    runner=dict(
        type=LocalRunner,
        max_num_workers=16,
        task=dict(type=OpenICLInferTask))
)
```

#### 3.2 关键设计差异

1. **数据集处理**
   ```python
   # 最小示例：单个硬编码的问题
   problem = '''
   写一个函数，计算两个数的最大公约数。
   函数签名: def gcd(a: int, b: int) -> int
   '''
   
   # 完整系统：标准数据集接口
   from opencompass.configs.datasets.humaneval.humaneval_passk_gen_8e312c import humaneval_datasets
   datasets = [humaneval_datasets]  # 支持多个数据集
   ```
   - 完整系统使用标准数据集，便于公平对比
   - 支持多个数据集的组合评测
   - 数据集格式统一，便于扩展

2. **模型生成策略**
   ```python
   # 最小示例：简单的生成循环
   for i in range(3):
       outputs = model.generate(
           max_new_tokens=512,
           do_sample=True,
           temperature=0.8
       )
   
   # 完整系统：配置化的生成策略
   generation_kwargs=dict(
       num_return_sequences=10,  # 更多的候选答案
       do_sample=True,
       top_p=0.95,              # 更细致的采样控制
       temperature=0.8
   )
   ```
   - 完整系统提供更多生成参数的控制
   - 支持批量生成多个答案
   - 生成策略可以根据需求灵活配置

3. **并行评测支持**
   ```python
   # 最小示例：串行处理
   for code in predictions:
       verify_code(code, test_cases)
   
   # 完整系统：并行处理
   infer = dict(
       partitioner=dict(type=SizePartitioner, max_task_size=300),  # 分批处理
       runner=dict(type=LocalRunner, max_num_workers=16)           # 多进程执行
   )
   ```
   - 支持大规模并行评测
   - 自动任务分割和资源管理
   - 提高评测效率

#### 3.3 为什么需要这些改进？

1. **标准化**
   - 使用统一的数据集接口
   - 规范的评测流程
   - 可比较的评测结果

2. **可扩展性**
   - 易于添加新的数据集
   - 支持不同的模型接口
   - 灵活的评测配置

3. **效率提升**
   - 并行处理支持
   - 批量生成和评测
   - 资源利用优化

4. **实用功能**
   - 详细的评测报告
   - 多模型对比
   - 结果可视化

#### 3.4 实践建议

1. **循序渐进**
   - 先用最小示例理解基本原理
   - 再尝试完整系统的各项功能
   - 根据需求逐步添加配置

2. **配置调优**
   - 从默认配置开始
   - 根据资源情况调整并行参数
   - 针对具体任务优化生成策略

3. **结果分析**
   - 关注 pass@k 指标
   - 分析失败案例
   - 收集改进建议

[后续内容...]