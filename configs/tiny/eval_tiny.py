from mmengine.config import read_base

with read_base():
    # 使用最基础的数据集配置
    from opencompass.configs.datasets.demo.demo_gsm8k_base_gen import gsm8k_datasets
    # 使用较小的模型配置
    from opencompass.configs.models.hf_internlm.hf_internlm2_1_8b import models as hf_internlm2_1_8b_models

# 只使用一个数据集和一个模型进行测试
datasets = [gsm8k_datasets[0]]  # 只使用第一个GSM8K数据集配置

# 修改模型配置以使用CPU
model_cfg = hf_internlm2_1_8b_models[0].copy()
model_cfg['model_kwargs'] = {'device_map': 'cpu'}  # 强制使用CPU
models = [model_cfg]

# 使用简化版运行器
runner = dict(
    type='TinyRunner',
    max_num_workers=1,
    task_type='generation'
) 