from tqdm import tqdm

from .base_selector import BaseSelector


class Deduplicator(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
    ):
        super(Deduplicator, self).__init__(
            source_file_path, target_dir, target_file_name
        )

    def __process__(self, data):
        selected_data = []

        for d in tqdm(data):
            if self.data_format == "self_instruct":
                instances = d["instances"]
                for instance in instances:
                    # if input and output are the same, we will not use such instances
                    if instance["input"] == instance["output"]:
                        instances.remove(instance)
                        continue
                    # if output is empty, we will not use such instances
                    if instance["output"] == "":
                        instances.remove(instance)
                        continue
                    # if input or output ends with a colon, these are usually imcomplete generation. We will not use such instances
                    if instance["input"].strip().endswith(":") or instance[
                        "output"
                    ].strip().endswith(":"):
                        instances.remove(instance)

                if len(instances) == 0:
                    continue

                # if the instances have same non-empty input, but different output, we will not use such instances
                same_input_diff_output = False
                for i in range(1, len(instances)):
                    for j in range(0, i):
                        if instances[i]["input"] == "":
                            continue
                        if (
                            instances[i]["input"] == instances[j]["input"]
                            and instances[i]["output"] != instances[j]["output"]
                        ):
                            same_input_diff_output = True
                            break

                # not use duplicate instances
                if same_input_diff_output:
                    continue

            elif self.data_format == "alpaca":
                if (
                    d["input"] == d["output"]
                    or d["output"] == ""
                    or d["input"].strip().endswith(":")
                    or d["output"].strip().endswith(":")
                ):
                    continue

            elif self.data_format == "alpaca_wo_input":
                if d["output"] == "" or d["output"].strip().endswith(":"):
                    continue

            else:
                raise ValueError("Unknown data format")

            selected_data.append(d)

        return selected_data
