import os
import json


class BaseSelector:
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
    ):
        self.source_file_path = source_file_path
        os.makedirs(target_dir, exist_ok=True)
        self.target_file_path = os.path.join(target_dir, target_file_name)
        self.data = None

    def load_data_from_file(self):
        data_path = self.source_file_path
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"File not found: {data_path}")

        if data_path.endswith(".jsonl"):
            data = [json.loads(l) for l in open(data_path, "r")]
        elif data_path.endswith(".json"):
            data = json.load(open(data_path, "r"))
        else:
            raise ValueError("Unknown file format")
        
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
