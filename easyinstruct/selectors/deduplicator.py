from tqdm import tqdm

from .base_selector import BaseSelector

class Deduplicator(BaseSelector):
    def __init__(self, 
                 source_dir: str = "data/generations/",
                 target_dir: str = "data/selections/",
                 source_file_path: str = "generated_instances.jsonl",
                 target_file_path: str = "selected_instructions.jsonl"
        ):
        super(Deduplicator, self).__init__(source_dir, target_dir, source_file_path, target_file_path)

    def __process__(self, data):
        for d in tqdm(data):
            instances = d["instances"]
            filtered_instances = []
            for instance in instances:
                # if input and output are the same, we will not use such instances
                if instance["input"] == instance["output"]:
                    continue
                # if output is empty, we will not use such instances
                if instance["output"] == "":
                    continue
                # if input or output ends with a colon, these are usually imcomplete generation. We will not use such instances
                if instance["input"].strip().endswith(":") or instance["output"].strip().endswith(":"):
                    continue
                instances = filtered_instances

            # if the instances have same non-empty input, but different output, we will not use such instances
            same_input_diff_output = False
            for i in range(1, len(instances)):
                for j in range(0, i):
                    if instances[i][1] == "":
                        continue
                    if instances[i][1] == instances[j][1] and instances[i][2] != instances[j][2]:
                        same_input_diff_output = True
                        break
            
            # remove duplicate instances
            if same_input_diff_output or len(instances) == 0:
                data.remove(d)
                continue

        return data
