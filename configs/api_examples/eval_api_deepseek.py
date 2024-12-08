from mmengine.config import read_base
from opencompass.models.deepseek_api import DeepseekAPI

with read_base():
    from opencompass.configs.datasets.gsm8k.gsm8k_gen_tiny import gsm8k_datasets

# 定义API模型配置
models = [
    dict(
        type=DeepseekAPI,
        abbr='deepseek-chat',
        path='deepseek-chat',
        key='sk-9653102b56844f7c9aadbcbf5975551c',
        url='https://api.deepseek.com/chat/completions',
        query_per_second=2,
        max_seq_len=2048,
        retry=2,
        max_out_len=100,
        batch_size=1,
        system_prompt='You are a helpful math expert. Solve problems step by step.',
    )
]

# 只使用GSM8K数据集的前5个样本进行测试
gsm8k_datasets[0]['reader_cfg']['test_range'] = '[0:5]'
gsm8k_datasets[0]['abbr'] = 'tiny_gsm8k'  # 修改数据集简称

# 组合数据集
datasets = gsm8k_datasets

# 工作目录
work_dir = 'outputs/api_deepseek_math/' 