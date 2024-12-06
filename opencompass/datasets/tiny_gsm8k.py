import json
import os
import re
from datasets import Dataset, DatasetDict

from opencompass.registry import LOAD_DATASET, TEXT_POSTPROCESSORS
from opencompass.openicl import BaseEvaluator
from .base import BaseDataset

@LOAD_DATASET.register_module()
class TinyGSM8KDataset(BaseDataset):
    """A simplified version of GSM8K dataset for teaching purposes."""
    
    def __init__(self, path, reader_cfg):
        super().__init__(path, reader_cfg)
        
    def load(self, path):
        """Load dataset from jsonl file."""
        datasets = {}
        for split in ['train', 'test']:
            split_path = os.path.join(path, split + '.jsonl')
            dataset = []
            with open(split_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    dataset.append(data)
            datasets[split] = Dataset.from_list(dataset)
        return DatasetDict(datasets)

@TEXT_POSTPROCESSORS.register_module('tiny_gsm8k')
def tiny_gsm8k_postprocess(text: str) -> str:
    """Extract the final answer from model output."""
    # Find all numbers in the text
    numbers = re.findall(r'\-?\d+\.\d+|\-?\d+', text)
    if not numbers:
        return 'NULL'
    return numbers[-1]  # Return the last number as answer

class TinyGSM8KEvaluator(BaseEvaluator):
    """A simplified evaluator for GSM8K dataset."""
    
    def score(self, predictions, references):
        """Calculate accuracy score."""
        if len(predictions) != len(references):
            return {'error': 'predictions and references have different length'}
        
        correct = 0
        for pred, ref in zip(predictions, references):
            try:
                # Compare as float numbers
                if abs(float(pred) - float(ref)) < 1e-6:
                    correct += 1
            except:
                continue
                
        accuracy = 100 * correct / len(references)
        return {'accuracy': accuracy} 