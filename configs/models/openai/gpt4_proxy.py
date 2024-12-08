# configs/models/openai/gpt4_proxy.py
from opencompass.models import OpenAI

api_meta_template = dict(round=[
    dict(role='HUMAN', api_role='HUMAN'),
    dict(role='BOT', api_role='BOT', generate=True),
])

models = [
    dict(
        abbr='GPT-4-proxy',
        type=OpenAI,
        path='gpt-4',
        key='your-api-key',  # 记得替换成实际的API key
        proxy=dict(
            http_proxy='socks5://127.0.0.1:7890',
            https_proxy='socks5://127.0.0.1:7890'
        ),
        meta_template=api_meta_template,
        query_per_second=1,
        max_out_len=2048,
        max_seq_len=2048,
        batch_size=1,
        temperature=0.0),
]