import os
import json

class BaseGenerator:
    def __init__(self, 
                 target_dir: str = "data/generations/"
                 ):
        self.target_dir = target_dir
        os.makedirs(self.target_dir, exist_ok=True)

    def load_data_from_file(self, data_path: str):
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"File not found: {data_path}")
        
        data = [json.loads(l) for l in open(data_path, "r")]
        return data

    def generate(self):
        raise NotImplementedError
