import pandas as pd
from tqdm import tqdm
from pandarallel import pandarallel

from .base_selector import BaseSelector


class LengthSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
        min_instruction_length: int = 3,
        max_instruction_length: int = 150,
        min_response_length: int = 1,
        max_response_length: int = 350,
        score_only: bool = False,
    ):
        super(LengthSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )
        self.min_instruction_length = min_instruction_length
        self.max_instruction_length = max_instruction_length
        self.min_response_length = min_response_length
        self.max_response_length = max_response_length
        self.score_only = score_only
        
    def get_instance_length(self, instance):
        return len(instance[0]["output"].split())

    def __process__(self, data):
        tqdm.pandas()
        df = pd.DataFrame(data)
        if df.shape[0] > 15000:
            pandarallel.initialize()
            df["instruction_length"] = df["instruction"].parallel_apply(
                lambda x: len(x.split())
            )
            if self.data_format == "self_instruct":
                df["output_length"] = df["instances"].parallel_apply(lambda x: self.get_instance_length(x))
            elif self.data_format == "alpaca" or self.data_format == "alpaca_wo_input":
                df["output_length"] = df["output"].parallel_apply(lambda x: len(x.split()))
            else:
                raise ValueError("Unknown data format")
        else:
            df["instruction_length"] = df["instruction"].progress_apply(
                lambda x: len(x.split())
            )
            if self.data_format == "self_instruct":
                df["output_length"] = df["instances"].progress_apply(lambda x: self.get_instance_length(x))
            elif self.data_format == "alpaca" or self.data_format == "alpaca_wo_input":
                df["output_length"] = df["output"].progress_apply(lambda x: len(x.split()))
            else:
                raise ValueError("Unknown data format")

        if self.score_only:
            data = df.to_dict(orient="records")
        else:
            selected_data = df[
                (df["instruction_length"] >= self.min_instruction_length)
                & (df["instruction_length"] <= self.max_instruction_length)
                & (df["output_length"] >= self.min_response_length)
                & (df["output_length"] <= self.max_response_length)
            ].to_dict(orient="records")

        return data if self.score_only else selected_data
