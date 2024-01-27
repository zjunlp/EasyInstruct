import os
import json


class BaseGenerator:
    def __init__(
        self,
        target_dir: str = "data/generations/",
        data_format: str = "alpaca",
    ):
        self.target_dir = target_dir
        os.makedirs(self.target_dir, exist_ok=True)
        self.data_format = data_format

    def load_data_from_file(self, data_path: str):
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"File not found: {data_path}")

        data = [json.loads(l) for l in open(data_path, "r")]
        return data

    def dump_data_to_file(self, data: list, data_path: str):
        with open(data_path, "w") as f:
            for d in data:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")

    def generate(self):
        raise NotImplementedError
