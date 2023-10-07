from tqdm import tqdm

from .base_selector import BaseSelector

class Deduplicator(BaseSelector):
    def __init__(self):

        super().__init__()

    def __process__(self, data):
        for d in tqdm(data):
            filtered_instances = []
            for instance in instances:
                # if input and output are the same, we will not use such instances
                if instance[1] == instance[2]:
                    continue
                # if output is empty, we will not use such instances
                if instance[2] == "":
                    continue
                # if input or output ends with a colon, these are usually imcomplete generation. We will not use such instances
                if instance[1].strip().endswith(":") or instance[2].strip().endswith(":"):
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
