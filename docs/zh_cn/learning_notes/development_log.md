# Brainstorm & Git Commits   


本篇文档用于记录学习过程头脑风暴, 以及 git 操作记录. 方便后续回顾.


## 2024-12-09

### 1. 重构框架设计文档

1. 重构了框架设计文档 (`docs/zh_cn/learning_notes/framework_design.md`)：
   - 添加了项目背景和动机说明
   - 优化了文档结构，使其更具故事性和连贯性
   - 增加了实际案例和代码示例
   - 补充了实践经验和最佳实践
   - 展望了未来发展方向

2. 文档改进：
   - 参考英文文档 (`docs/en/user_guides/framework_overview.md`) 的结构
   - 增强了文档的可读性和实用性
   - 添加了更多具体示例和实践经验


```bash
git add docs/zh_cn/learning_notes/framework_design.md
git commit -m "docs: update framework design document"
```

### 2. 编译bug

大胆搞一个新分钟 doc, 出问题直接删除, 不要犹豫, **速度永远第一位**

```bash
git add . && git commit -m "docs: add doc development guide"
```




## 2024-12-08


### 1. 添加代码能力评测教程

```bash
git add docs/zh_cn/learning_notes/code_eval_tutorial.md
git commit -m "docs: add code evaluation tutorial"
```

### 2. 添加 api 模型评测教程

- 添加了 `mini_code_eval_deepseek.py` 示例脚本，展示如何使用 API 模型进行代码能力评测
- 使用 OpenAI SDK 调用 Deepseek API，提供了完整的代码生成和验证流程
- 包含了错误处理、环境变量配置等最佳实践
- 脚本位 `docs/zh_cn/learning_notes/scripts/` 目录下

提交更改：
```bash
git add docs/zh_cn/learning_notes/scripts/mini_code_eval_deepseek.py
git add docs/zh_cn/learning_notes/development_log.md
git commit -m "docs: add API model evaluation example with Deepseek"
```

### 3. API 模型数据能力评测

在开发 API 模型评测功能时，我们经历了以下几个阶段：

1. 初始尝试
   - 最初尝试修改 `eval_code_passk.py` 来评估 API 模型的代码能力
   - 遇到了文件位置和路径问题
   - 参考 `eval_api_qwen.py` 调整了配置结构

2. 简化方案
   - 决定放弃复杂的代码评测，转向简单的数学数据集评测
   - 参考 `eval_tiny_demo.py` 的简洁配置方式
   - 使用 GSM8K 数据集作为测试数据

3. 关键问题解决
   - API 认证问题：从使用环境变量 `${DEEPSEEK_API_KEY}` 改为直接使用 API key
   - 配置简化：只保留必要的配置项，提高可读性
   - 正确引入 `DeepseekAPI` 类：从 `opencompass.models.deepseek_api` 导入

4. 最终配置
```python
from mmengine.config import read_base
from opencompass.models.deepseek_api import DeepseekAPI

with read_base():
    from opencompass.configs.datasets.gsm8k.gsm8k_gen_tiny import gsm8k_datasets

models = [
    dict(
        type=DeepseekAPI,
        abbr='deepseek-chat',
        path='deepseek-chat',
        key='your-api-key',  # 直接使用 API key
        url='https://api.deepseek.com/chat/completions',
        query_per_second=2,
        max_seq_len=2048,
        retry=2,
        max_out_len=100,
        batch_size=1,
        system_prompt='You are a helpful math expert. Solve problems step by step.',
    )
]

gsm8k_datasets[0]['reader_cfg']['test_range'] = '[0:5]'
gsm8k_datasets[0]['abbr'] = 'tiny_gsm8k'

datasets = gsm8k_datasets
work_dir = 'outputs/api_deepseek_math/'
```

5. 经验总结
   - 配置文件应该保持简单明了，避免不必要的复杂性
   - API 认证最好使用直接的方式，避免环境变量解析可能带来的问题
   - 参考现有的简单示例（如 `eval_tiny_demo.py`）往往比从复杂配置开始更有效
   - 正确的导入路径和类引用对于避免运行时错误很重要

提交更改：
```bash
git add docs/zh_cn/learning_notes/development_log.md
git commit -m "docs: add API model evaluation development summary"
```


## 2024-12-07

### 1. 添加配置系统文档
```bash
git add docs/zh_cn/learning_notes/config_system.md
git commit -m "docs: add comprehensive guide for OpenCompass config system"
```
- 添加了配置系统详解文档
- 修复了 --num-gpus 参数问题

### 2. 添加开发日志
```bash
git add docs/zh_cn/index.rst docs/zh_cn/learning_notes/development_log.md
git commit -m "docs: add development log to track git operations"
```
- 创建开发日志文档
- 将开发日志加入到文档索引

### 3. API 调用 vpn 问题

我需要云端的机器访问本地的vpn when call for openai api model, 

详细解决方案请参考: [SSH 隧道代理方案](./ssh_tunnel_proxy.md)


## Brainstorm

下一步搞什么鬼呢？我想一下啊。api 模型的评测, 多模态模型的评测?

我需要云端的机器访问本地的vpn when call for openai api model, 

我连接云端服务器的命令是这个:
ssh -p 44773 root@ssh.intern-ai.org.cn -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null

然后运行脚本 @eval_api_demo.py ,  请注意，并不是云端的所有的流量都用本地的vpn访问，只是运行这一个脚本的时候，临时性的使用本地的vpn。