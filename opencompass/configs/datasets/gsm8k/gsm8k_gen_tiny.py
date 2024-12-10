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
                dict(role='HUMAN', prompt="Question: Mark's basketball team scores 25 2 pointers, 8 3 pointers and 10 free throws. Their opponents score double the 2 pointers but half the 3 pointers and free throws. What's the total number of points scored by both teams added together?\nLet's think step by step\nAnswer:"),
                dict(role='BOT', prompt="Mark's team scores 25 2 pointers, meaning they scored 25*2= 50 points in 2 pointers.\nHis team also scores 8 3 pointers, meaning they scored 8*3= 24 points in 3 pointers\nThey scored 10 free throws, and free throws count as one point so they scored 10*1=10 points in free throws.\nAll together his team scored 50+24+10= 84 points\nMark's opponents scored double his team's number of 2 pointers, meaning they scored 50*2=100 points in 2 pointers.\nHis opponents scored half his team's number of 3 pointers, meaning they scored 24/2= 12 points in 3 pointers.\nThey also scored half Mark's team's points in free throws, meaning they scored 10/2=5 points in free throws.\nAll together Mark's opponents scored 100+12+5=117 points\nThe total score for the game is both team's scores added together, so it is 84+117=201 points\nThe answer is 201\n"),
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
# data_path = './data/gsm8k'

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 回溯到项目根目录（从 configs/datasets/gsm8k 回溯三级）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

# 构建到 data/gsm8k 的路径
data_path = os.path.join(project_root, 'data', 'gsm8k')

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

