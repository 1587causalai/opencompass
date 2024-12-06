"""
演示脚本：展示大语言模型评测的核心流程
主要步骤：
1. 定义配置（模型和数据集配置）
2. 初始化模型
3. 加载数据集
4. 运行推理
5. 评估结果
"""

import os
import torch
import time
import warnings
from pprint import pprint

# 完全禁用所有警告
import warnings
warnings.filterwarnings('ignore')

def init_model(model_cfg):
    """初始化模型和分词器"""
    print("\n=== Step 2: 初始化模型 ===")
    t0 = time.time()
    
    print("开始导入必要的库...")
    t1 = time.time()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"库导入耗时: {time.time() - t1:.2f}秒")
    
    print("开始加载模型...")
    model = AutoModelForCausalLM.from_pretrained(
        model_cfg['path'],
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map='auto'
    )
    print(f"模型加载耗时: {time.time() - t0:.2f}秒")
    
    print("开始加载分词器...")
    t1 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(
        model_cfg['tokenizer_path'],
        trust_remote_code=True
    )
    print(f"分词器加载耗时: {time.time() - t1:.2f}秒")
    
    print(f"模型加载完成: {model_cfg['abbr']}")
    print(f"总耗时: {time.time() - t0:.2f}秒")
    return model, tokenizer

def load_dataset(dataset_cfg):
    """加载数据集"""
    print("\n=== Step 3: 加载数据集 ===")
    t0 = time.time()
    
    print("开始导入必要的库...")
    t1 = time.time()
    from opencompass.datasets.gsm8k import GSM8KDataset
    print(f"库导入耗时: {time.time() - t1:.2f}秒")
    
    print(f"加载数据集: {dataset_cfg['abbr']}")
    print(f"数据集路径: {dataset_cfg['path']}")
    print(f"测试范围: {dataset_cfg['reader_cfg']['test_range']}")
    
    # 创建数据集实例
    print("开始创建数据集实例...")
    t1 = time.time()
    dataset = GSM8KDataset(
        path=dataset_cfg['path'],
        reader_cfg=dataset_cfg['reader_cfg']
    )
    print(f"数据集实例创建耗时: {time.time() - t1:.2f}秒")
    
    # 获取测试集数据
    print("开始获取测试集数据...")
    t1 = time.time()
    test_data = dataset.test
    print(f"测试集获取耗时: {time.time() - t1:.2f}秒")
    print(f"样本数量: {len(test_data)}")
    print(f"数据集加载总耗时: {time.time() - t0:.2f}秒")
    
    return test_data

def run_inference(model, tokenizer, dataset):
    """运行推理"""
    print("\n=== Step 4: 运行推理 ===")
    predictions = []
    
    # Few-shot example
    example = {
        "question": "Mark's basketball team scores 25 2 pointers, 8 3 pointers and 10 free throws. Their opponents score double the 2 pointers but half the 3 pointers and free throws. What's the total number of points scored by both teams added together?",
        "answer": """Mark's team scores 25 2 pointers, meaning they scored 25*2= 50 points in 2 pointers.
His team also scores 8 3 pointers, meaning they scored 8*3= 24 points in 3 pointers
They scored 10 free throws, and free throws count as one point so they scored 10*1=10 points in free throws.
All together his team scored 50+24+10= 84 points
Mark's opponents scored double his team's number of 2 pointers, meaning they scored 50*2=100 points in 2 pointers.
His opponents scored half his team's number of 3 pointers, meaning they scored 24/2= 12 points in 3 pointers.
They also scored half Mark's team's points in free throws, meaning they scored 10/2=5 points in free throws.
All together Mark's opponents scored 100+12+5=117 points
The total score for the game is both team's scores added together, so it is 84+117=201 points
The answer is 201"""
    }
    
    for idx, sample in enumerate(dataset):
        print(f"\n处理样本 {idx + 1}:")
        print(f"问题: {sample['question']}")
        
        # 构造输入（包含示例）
        prompt = f"""Question: {example['question']}
Let's solve this step by step:
{example['answer']}

Question: {sample['question']}
Let's solve this step by step:
"""
        
        print(f"\n完整的 Prompt:")
        print("="*50)
        print(prompt)
        print("="*50)
        
        inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=True).to(model.device)
        prompt_length = len(tokenizer.decode(inputs['input_ids'][0]))
        
        # 生成答案
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=False,
            )
        
        # 只获取新生成的部分
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        print(f"模型回答:\n{response}")
        predictions.append(response)
    
    return predictions

def evaluate_results(predictions, dataset):
    """评估结果"""
    print("\n=== Step 5: 评估结果 ===")
    
    def extract_answer(text):
        """从文本中提取最终答案的数字"""
        import re
        # 首先尝试匹配 "The answer is X" 格式
        answer_pattern = r'The answer is[\s]*\$?\\?(?:boxed{)?(\d[\d,]*(?:\.\d+)?)}?\$?\.?$'
        match = re.search(answer_pattern, text, re.MULTILINE)
        if match:
            # 移除数字中的逗号
            return float(match.group(1).replace(',', ''))
            
        # 如果上面的模式没匹配到，则提取所有数字，取最后一个
        numbers = re.findall(r'-?\d[\d,]*(?:\.\d+)?', text)
        if numbers:
            return float(numbers[-1].replace(',', ''))
        return None

    def is_equal(pred, refer):
        """比较预测值和参考答案是否相等"""
        try:
            # 从预测答案中提取数字
            pred_num = extract_answer(pred)
            # 从参考答案中提取数字（在 #### 之后）
            refer_match = re.search(r'####\s*(\d+)', refer)
            if refer_match:
                refer_num = float(refer_match.group(1))
            else:
                # 如果没有 #### 格式，则提取所有数字取最后一个
                numbers = re.findall(r'-?\d[\d,]*(?:\.\d+)?', refer)
                refer_num = float(numbers[-1].replace(',', ''))
            
            if pred_num is not None and abs(pred_num - refer_num) < 1e-6:
                return True
        except Exception as e:
            print(f"警告：答案提取失败 - {str(e)}")
        return False
    
    # 计算准确率
    correct = 0
    total = len(predictions)
    
    for idx, (pred, true) in enumerate(zip(predictions, dataset)):
        print(f"\n样本 {idx + 1}:")
        print(f"预测答案: {pred}")
        print(f"正确答案: {true['answer']}")
        
        # 检查答案是否正确
        is_correct = is_equal(pred, true['answer'])
        print(f"是否正确: {'✓' if is_correct else '✗'}")
        
        # 显示提取到的数字（用于调试）
        pred_num = extract_answer(pred)
        print(f"提取的预测数字: {pred_num}")
        
        if is_correct:
            correct += 1
    
    # 打印总体准确率
    accuracy = (correct / total) * 100
    print(f"\n总体评估结果:")
    print(f"正确数: {correct}")
    print(f"总样本数: {total}")
    print(f"准确率: {accuracy:.2f}%")

def main():
    # === Step 1: 定义配置 ===
    print("\n=== Step 1: 定义配置 ===")
    t0 = time.time()
    
    # 模型配置
    model_cfg = dict(
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
    
    # 数据集配置
    dataset_cfg = dict(
        type='GSM8KDataset',
        abbr='tiny_gsm8k',
        path='/root/opencompass/data/gsm8k',
        reader_cfg=dict(
            input_columns=['question'],
            output_column='answer',
            test_split='test',
            test_range='[0:5]'  # 只使用前5个样本
        )
    )
    
    print("模型配置:")
    pprint(model_cfg)
    print("\n数据集配置:")
    pprint(dataset_cfg)
    print(f"配置定义耗时: {time.time() - t0:.2f}秒")
    
    # 执行评测流程
    model, tokenizer = init_model(model_cfg)
    dataset = load_dataset(dataset_cfg)
    predictions = run_inference(model, tokenizer, dataset)
    evaluate_results(predictions, dataset)

if __name__ == "__main__":
    main() 