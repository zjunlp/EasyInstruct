import os
import json


class BaseSelector:
    def __init__(
        self,
        source_dir: str = "data/generations/",
        target_dir: str = "data/selections/",
        source_file_path: str = "generated_instances.jsonl",
        target_file_path: str = "selected_instructions.jsonl",
    ):
        self.source_dir = source_dir
        self.target_dir = target_dir
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.target_dir, exist_ok=True)
        self.source_file_path = os.path.join(self.source_dir, source_file_path)
        self.target_file_path = os.path.join(self.target_dir, target_file_path)
        self.data = None

    def load_data_from_file(self):
        data_path = self.source_file_path
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"File not found: {data_path}")

        data = [json.loads(l) for l in open(data_path, "r")]
        self.data = data
        return data

    def dump_data_to_file(self):
        data_path = self.target_file_path
        with open(data_path, "w") as f:
            for d in self.data:
                f.write(json.dumps(d) + "\n")

    def __process__(self, data):
        raise NotImplementedError

    def process(self):
        self.load_data_from_file()
        self.data = self.__process__(self.data)
        self.dump_data_to_file()
        return self.data
