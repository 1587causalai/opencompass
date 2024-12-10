from typing import List

from opencompass.registry import RUNNERS
from opencompass.tasks.base import BaseTask
from opencompass.utils import build_dataset_from_cfg, build_model_from_cfg

@RUNNERS.register_module()
class TinyRunner:
    """A simplified runner for basic evaluation tasks."""
    
    def __init__(self, max_num_workers: int = 1, task_type: str = 'generation'):
        self.max_num_workers = max_num_workers
        self.task_type = task_type

    def __call__(self, tasks: List[dict]) -> List[BaseTask]:
        """Run the evaluation tasks.
        
        Args:
            tasks: List of task configs
            
        Returns:
            List of completed tasks
        """
        completed_tasks = []
        for task in tasks:
            model = build_model_from_cfg(task.model)
            dataset = build_dataset_from_cfg(task.dataset)
            task_instance = self._create_task(model, dataset)
            task_instance.run()
            completed_tasks.append(task_instance)
        return completed_tasks

    def _create_task(self, model, dataset) -> BaseTask:
        """Create a task based on model and dataset."""
        task_cfg = dict(
            type=self.task_type,
            model=model,
            dataset=dataset,
        )
        return BaseTask.build(task_cfg) 