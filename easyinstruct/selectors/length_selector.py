from tqdm import tqdm

from .base_selector import BaseSelector


class LengthSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
        min_instruction_length: int = 3,
        max_instruction_length: int = 150,
        min_response_length: int = 3,
        max_response_length: int = 350,
    ):
        super(LengthSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )
        self.min_instruction_length = min_instruction_length
        self.max_instruction_length = max_instruction_length
        self.min_response_length = min_response_length
        self.max_response_length = max_response_length

    def __process__(self, data):
        for d in tqdm(data):
            if len(d["instruction"]) < self.min_instruction_length:
                data.remove(d)
                continue

            if len(d["instruction"]) > self.max_instruction_length:
                data.remove(d)
                continue

            instances = d["instances"]
            for instance in instances:
                if (
                    len(instance["output"]) < self.min_response_length
                    or len(instance["output"]) > self.max_response_length
                ):
                    instances.remove(instance)

            if len(instances) == 0:
                data.remove(d)

        return data
