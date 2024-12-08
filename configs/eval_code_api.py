from mmengine.config import read_base
from opencompass.models import OpenAISDK

# API配置
deepseek_url = 'https://api.deepseek.com/v1'  # API服务地址

# 模型配置
models = [
    dict(
        # 基础信息
        type='OpenAISDK',  # 注意这里改成字符串
        path='deepseek-chat',  # 请求服务的模型名
        # 读取自己申请的APIkey
        key='${DEEPSEEK_API_KEY}',  # API key
        openai_api_base=deepseek_url,  # 服务地址
        # 生成配置
        rpm_verbose=True,  # 是否打印请求速率
        query_per_second=0.5,  # 服务请求速率
        max_out_len=1024,  # 最大输出长度
        max_seq_len=4096,  # 最大输入长度
        temperature=0.8,  # 生成温度
        batch_size=1,  # 批处理大小
        retry=3,  # 重试次数
    )
]

# 数据集配置
with read_base():
    from opencompass.configs.datasets.humaneval.humaneval_passk_gen_8e312c import humaneval_datasets

# 每个数据集只取前2个样本进行评测
for d in humaneval_datasets:
    d['abbr'] = 'demo_' + d['abbr']
    d['reader_cfg']['test_range'] = '[0:2]'  # 这里每个数据集只取2个样本，方便快速评测

datasets = humaneval_datasets

# 工作目录
work_dir = "outputs/api_eval"


# 参考文档 https://github.com/InternLM/Tutorial/tree/camp4/docs/L1/Evaluation