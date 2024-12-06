import json
import os
import re
from os import environ

from datasets import Dataset, DatasetDict

from opencompass.openicl import BaseEvaluator
from opencompass.registry import LOAD_DATASET, TEXT_POSTPROCESSORS
from opencompass.utils import get_data_path

from .base import BaseDataset

# ===== 数据集加载部分 =====
@LOAD_DATASET.register_module()  # 注册到数据集加载器，使其可以通过配置文件动态调用
class GSM8KDataset(BaseDataset):
    """GSM8K数据集加载类
    
    继承自BaseDataset，实现了数据集的加载逻辑。支持从本地文件系统或ModelScope加载数据。
    数据格式为jsonl，每行包含question和answer字段。
    """

    @staticmethod
    def load(path):
        """加载数据集
        
        Args:
            path: 数据集路径，可以是本地路径或ModelScope数据集名称
            
        Returns:
            DatasetDict: 包含train和test两个split的数据集
        """
        # 获取实际的数据路径（处理环境变量等）
        path = get_data_path(path)
        
        # 如果设置了从ModelScope加���数据
        if environ.get('DATASET_SOURCE') == 'ModelScope':
            from modelscope import MsDataset
            dataset = MsDataset.load(dataset_name=path)
        # 否则从本地文件系统加载
        else:
            datasets = {}
            # 分别加载训练集和测试集
            for split in ['train', 'test']:
                split_path = os.path.join(path, split + '.jsonl')
                dataset = []
                # 读取jsonl文件
                with open(split_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = json.loads(line.strip())
                        dataset.append(line)
                # 转换为HuggingFace Dataset格式
                datasets[split] = Dataset.from_list(dataset)
            dataset = DatasetDict(datasets)
        return dataset


# ===== 后处理部分 =====
@TEXT_POSTPROCESSORS.register_module('gsm8k_dataset')  # 注册到文本后处理器
def gsm8k_dataset_postprocess(text: str) -> str:
    """处理数据集中的标准答案
    
    从标准答案文本中提取最终数值。标准答案格式为："#### 数值"
    
    Args:
        text: 原始答案文本
        
    Returns:
        str: 提取出的数值答案
    """
    # 分割并提取数值部分，移除逗号
    return text.split('#### ')[1].replace(',', '')


@TEXT_POSTPROCESSORS.register_module('gsm8k')  # 注册到文本后处理器
def gsm8k_postprocess(text: str) -> str:
    """处理模型输出的答案
    
    从模型生成的文本中提取最后一个数值作为答案。
    
    Args:
        text: 模型生成的文本
        
    Returns:
        str: 提取出的数值答案，如果没有找到数值则返回'NULL'
    """
    # 只取Question前的部分（避免处理到提示词模板）
    text = text.split('Question:')[0]
    # 查找所有数值（支持整数、小数、负数）
    numbers = re.findall(r'\-?\d+\.\d+|\-?\d+', text)
    if not numbers:
        return 'NULL'
    # 返回最后一个数值
    return numbers[-1]


# ===== 评估器部分 =====
class Gsm8kEvaluator(BaseEvaluator):
    """GSM8K评估器
    
    实现了答案比较和准确率计算的逻辑。
    """
    
    def is_equal(self, pred, refer):
        """比较预测值和参考答案是否相等
        
        支持字符串完全匹配和浮点数近似匹配（误差<1e-6）
        
        Args:
            pred: 预测值
            refer: 参考答案
            
        Returns:
            bool: 是否相等
        """
        try:
            # 尝试进行数值比较
            if pred == refer or abs(float(pred) - int(refer)) < 1e-6:
                return True
        except Exception:
            pass
        return False

    def score(self, predictions, references):
        """计算评估分数
        
        计算准确率并返回详细的评估信息
        
        Args:
            predictions: 预测值列表
            references: 参考答案列表
            
        Returns:
            dict: 包含准确率和详细信息的字典
        """
        # 检查预测值和参考答案数量是否一致
        if len(predictions) != len(references):
            return {
                'error': 'predictions and references have different length'
            }
        
        correct = 0
        count = 0
        details = []
        # 逐个比较预测值和参考答案
        for i, j in zip(predictions, references):
            detail = {'pred': i, 'answer': j, 'correct': False}
            count += 1
            if self.is_equal(i, j):
                correct += 1
                detail['correct'] = True
            details.append(detail)
        
        # 返回准确率和详细信息
        result = {'accuracy': 100 * correct / count, 'details': details}
        return result


# ===== Agent评估器部分 =====
class Gsm8kAgentEvaluator(BaseEvaluator):
    """GSM8K Agent评估器
    
    这个评估器专门用于评估使用工具（如Python解释器）的AI模型。
    与普通评估器不同，它不仅关注最终答案，还会评估整个解题过程。
    
    举例来说，对于问题"小明有5个苹果，吃掉2个，又买了3个，现在有几个苹果？"：
    - 普通模型直接给出答案：6
    - 使用工具的模型会展示计算过程：
        1. 使用计算器：5 - 2 = 3 (剩余苹果)
        2. 使用计算器：3 + 3 = 6 (最终苹果)
    
    评估维度包括：
    1. follow_acc: 最终答案的正确率
    2. reasoning_acc: 推理过程的正确率
    3. code_acc: 代码执行的成功率
    4. action_pct: 工具使用的比例
    
    这些详细的评估指标有助于我们理解模型的解题能力和工具使用能力。
    
    Args:
        action: 用于捕获内部预测的动作名称，默认为'PythonInterpreter'
    """

    def __init__(self, action: str = 'PythonInterpreter'):
        self.action = action

    def is_equal(self, pred, refer):
        """比较最终答案是否相等
        
        Args:
            pred: 预测值
            refer: 参考答案
            
        Returns:
            bool: 是否相等
        """
        try:
            if pred == refer or abs(float(pred) - int(refer)) < 1e-6:
                return True
        except Exception:
            pass
        return False

    def soft_equal(self, pred, refer, step):
        """比较中间步骤的结果是否正确
        
        检查模型在使用工具时的中间计算结果是否正确。
        
        Args:
            pred: 预测值
            refer: 参考答案
            step: 计算步骤信息
            
        Returns:
            bool: 中间步骤是否正确
        """
        try:
            soft_pred = step['result']['text']
            if abs(float(soft_pred) - int(refer)) < 1e-6:
                return True
        except Exception:
            pass
        return False

    def get_action(self, step):
        """获取指定类型的工具使用步骤
        
        从解题步骤中找出使用特定工具（如计算器）的步骤。
        
        Args:
            step: 解题步骤列表
            
        Returns:
            dict: 工具使用的步骤信息
        """
        for s in step[::-1]:  # 从后向前查找
            if s['type'] == self.action:
                return s

    def score(self, predictions, references, steps):
        """计算多维度的评估分数
        
        不仅评估最终答案，还会评估整个解题过程的各个方面。
        
        评估指标说明：
        - follow_acc: 直接推理或最终答案的正确率
        - reasoning_acc: 推理过程（包括中间步骤）的正确率
        - code_acc: 工具使用（如代码执行）的成功率
        - action_pct: 解题过程中使用工具的比例
        
        Args:
            predictions: 预测值列表
            references: 参考答案列表
            steps: 解题步骤列表
            
        Returns:
            dict: 包含多个评估指标的字典
        """
        if len(predictions) != len(references):
            return {'error': 'preds and refrs have different length'}

        # 各种计数器
        row_reasoning_scope = 0  # 直接推理正确的数量
        action_scope = 0         # 使用工具的数量
        code_scope = 0          # 代码执行成功的数量
        reasoning_scope = 0      # 推理过程正确的数量
        final_scope = 0         # 最终答案正确的数量
        total = len(references)

        # 逐个评估每个样本
        for pred, refer, step in zip(predictions, references, steps):
            # 如果最终答案正确
            if self.is_equal(pred, refer):
                if self.get_action(step):  # 使用了工具
                    final_scope += 1
                else:  # 直接推理
                    row_reasoning_scope += 1
            else:  # 最终答案错误
                s = self.get_action(step)
                if s:  # 使用了工具
                    action_scope += 1
                    if not s['errmsg']:  # 代码执行成功
                        code_scope += 1
                        # 检查中间结果是否正确
                        reasoning_scope += self.soft_equal(pred, refer, s)

        # 计算各项指标
        result = dict(
            follow_acc=100 * (row_reasoning_scope + final_scope) / total,
            reasoning_acc=100 *
            (reasoning_scope + final_scope + row_reasoning_scope) / total,
            code_acc=100 * (code_scope + final_scope) / total,
            action_pct=100 * (action_scope + final_scope) / total,
        )
        return result
