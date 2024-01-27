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
        self.data_format = ""

    def check_data_format(self):
        if not isinstance(self.data, list):
            raise ValueError("Data should be a list of dict")

        if len(self.data) == 0:
            raise ValueError("Data should not be empty")

        if not isinstance(self.data[0], dict):
            raise ValueError("Data item should be a dict")

        alpaca_format_keys = ["instruction", "input", "output"]
        alpaca_format_wo_input_keys = ["instruction", "output"]
        self_instruct_format_keys = ["instruction", "instances"]
        data_keys_set = set(self.data[0].keys())
        if all([key in data_keys_set for key in alpaca_format_keys]):
            self.data_format = "alpaca"
        elif all([key in data_keys_set for key in alpaca_format_wo_input_keys]):
            self.data_format = "alpaca_wo_input"
        elif all([key in data_keys_set for key in self_instruct_format_keys]):
            self.data_format = "self_instruct"
        else:
            raise ValueError("Unknown data format")

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
        self.check_data_format()
        return data

    def dump_data_to_file(self):
        data_path = self.target_file_path
        with open(data_path, "w") as f:
            for d in self.data:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")

    def __process__(self, data):
        raise NotImplementedError

    def process(self):
        self.load_data_from_file()
        self.data = self.__process__(self.data)
        self.dump_data_to_file()
        return self.data
