from mmengine.config import read_base

with read_base():
    from opencompass.configs.datasets.gsm8k.gsm8k_gen_tiny import gsm8k_datasets

# 定义本地模型配置
models = [
    dict(
        type='HuggingFace',
        abbr='internlm2_5-1_8b-chat',
        path='/share/new_models/Shanghai_AI_Laboratory/internlm2_5-1_8b-chat',
        tokenizer_path='/share/new_models/Shanghai_AI_Laboratory/internlm2_5-1_8b-chat',
        model_kwargs=dict(
            trust_remote_code=True,
            torch_dtype='float16',
            device_map='auto'
        ),
        tokenizer_kwargs=dict(trust_remote_code=True),
        max_out_len=100,
        batch_size=1,
        run_cfg=dict(num_gpus=1),
    )
]

# 只使用GSM8K数据集的前5个样本进行测试
gsm8k_datasets[0]['reader_cfg']['test_range'] = '[0:5]'
gsm8k_datasets[0]['abbr'] = 'tiny_gsm8k'  # 修改数据集简称

# 组合数据集
datasets = gsm8k_datasets