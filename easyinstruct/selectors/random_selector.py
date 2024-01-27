import random

from .base_selector import BaseSelector


class RandomSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
        num_instructions_to_sample: int = 100,
        seed: int = 42,
    ):
        super(RandomSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )
        self.num_instructions_to_sample = num_instructions_to_sample
        random.seed(seed)

    def __process__(self, data):
        if len(data) < self.num_instructions_to_sample:
            return data
        else:
            return random.sample(data, self.num_instructions_to_sample)
