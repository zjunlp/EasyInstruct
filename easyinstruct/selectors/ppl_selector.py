import torch
import pandas as pd
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from .base_selector import BaseSelector


class PPLSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
        threshold: float = 200,
        model_name: str = "gpt2",
        device: str = "cuda",
        score_only: bool = False,
    ):
        super(PPLSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )
        self.threshold = threshold
        self.model_name = model_name
        self.device = device
        self.score_only = score_only

    def ppl(self, input, tokenizer, model):
        if self.data_format == "self_instruct":
            input_text = input[0]["output"]
        elif self.data_format == "alpaca" or self.data_format == "alpaca_wo_input":
            input_text = input
        else:
            raise ValueError("Unknown data format")

        encodings = tokenizer(input_text, return_tensors="pt")
        max_length = model.config.n_positions
        stride = 512
        seq_len = encodings.input_ids.size(1)

        nlls = []
        prev_end_loc = 0
        for begin_loc in range(0, seq_len, stride):
            end_loc = min(begin_loc + max_length, seq_len)
            trg_len = end_loc - prev_end_loc
            input_ids = encodings.input_ids[:, begin_loc:end_loc].to(self.device)
            target_ids = input_ids.clone()
            target_ids[:, :-trg_len] = -100

            with torch.no_grad():
                outputs = model(input_ids, labels=target_ids)

                # loss is calculated using CrossEntropyLoss which averages over valid labels
                # N.B. the model only calculates loss over trg_len - 1 labels, because it internally shifts the labels
                # to the left by 1.
                neg_log_likelihood = outputs.loss

            nlls.append(neg_log_likelihood)

            prev_end_loc = end_loc
            if end_loc == seq_len:
                break

        ppl = torch.exp(torch.stack(nlls).mean())
        return ppl.item()

    def __process__(self, data):
        print(f"Loading tokenizer from {self.model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        print(f"Loading model from {self.model_name}...")
        model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)

        tqdm.pandas()
        df = pd.DataFrame(data)
        if self.data_format == "self_instruct":
            df["ppl_score"] = df["instances"].progress_apply(
                lambda x: self.ppl(x, tokenizer, model)
            )
        elif self.data_format == "alpaca" or self.data_format == "alpaca_wo_input":
            df["ppl_score"] = df["output"].progress_apply(
                lambda x: self.ppl(x, tokenizer, model)
            )
        else:
            raise ValueError("Unknown data format")

        if self.score_only:
            data = df.to_dict(orient="records")
        else:
            selected_data = df[df["ppl_score"] <= self.threshold].to_dict(
                orient="records"
            )

        return data if self.score_only else selected_data
