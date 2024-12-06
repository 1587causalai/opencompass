from opencompass.openicl.icl_prompt_template import PromptTemplate
from opencompass.openicl.icl_retriever import ZeroRetriever
from opencompass.openicl.icl_inferencer import GenInferencer
from opencompass.datasets import GSM8KDataset, gsm8k_postprocess, gsm8k_dataset_postprocess, Gsm8kEvaluator
import os

# ===== Reader配置 =====
# 定义如何读取数据集中的字段
# input_columns: 指定哪些列作为模型输入，这里只使用'question'列
# output_column: 指定哪一列作为标准答案，这里使用'answer'列
gsm8k_reader_cfg = dict(input_columns=['question'], output_column='answer')

# ===== 推理配置 =====
gsm8k_infer_cfg = dict(
    # 1. 提示词模板配置：定义如何构造发送给模型的提示
    prompt_template=dict(
        type=PromptTemplate,
        template=dict(
            round=[
                # 示例问题：用于few-shot学习
                # role='HUMAN': 表示这是输入的问题
                dict(role='HUMAN', prompt="Question: Mark's basketball team...\nLet's think step by step\nAnswer:"),
                # role='BOT': 表示这是期望的回答格式
                dict(role='BOT', prompt="Mark's team scores...\nThe answer is 201\n"),
                # 实际测试问题的模板：{question}会被实际问题替换
                dict(role='HUMAN', prompt="Question: {question}\nLet's think step by step\nAnswer:"),
            ],
        )),
    
    # 2. 检索器配置：定义如何选择示例
    # ZeroRetriever: 表示不进行动态示例检索，使用固定示例
    retriever=dict(type=ZeroRetriever),
    
    # 3. 推理器配置：控制生成过程
    # GenInferencer: 用于生成式任务的推理器
    # max_out_len: 限制模型最大输出长度为512个token
    inferencer=dict(type=GenInferencer, max_out_len=512))

# ===== 评估配置 =====
gsm8k_eval_cfg = dict(
    # 1. 评估器：定义如何计算评估指标
    # Gsm8kEvaluator: 专门用于GSM8K数据集的评估器，计算准确率
    evaluator=dict(type=Gsm8kEvaluator),
    
    # 2. 预测后处理：处理模型的原始输出
    # gsm8k_postprocess: 从模型输出中提取最终数值答案
    pred_postprocessor=dict(type=gsm8k_postprocess),
    
    # 3. 数据集后处理：处理数据集中的标准答案
    # gsm8k_dataset_postprocess: 确保标准答案格式统一
    dataset_postprocessor=dict(type=gsm8k_dataset_postprocess)
)

# 指定数据集路径
data_path = '/root/opencompass/data/gsm8k'

# ===== 完整数据集配置 =====
gsm8k_datasets = [
    dict(
        abbr='gsm8k',              # 数据集简称
        type=GSM8KDataset,         # 使用的数据集类
        path=data_path,            # 数据集路径
        reader_cfg=gsm8k_reader_cfg,  # 读取配置
        infer_cfg=gsm8k_infer_cfg,    # 推理配置
        eval_cfg=gsm8k_eval_cfg        # 评估配置
    )
]

