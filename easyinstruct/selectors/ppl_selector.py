from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from .base_selector import BaseSelector


class PPLSelector(BaseSelector):
    def __init__(
        self,
        source_dir: str = "data/generations/",
        target_dir: str = "data/selections/",
        source_file_path: str = "generated_instances.jsonl",
        target_file_path: str = "selected_instructions.jsonl",
        threshold: float = 200,
        model_name: str = "gpt2",
        device: str = "cuda",
    ):
        super(PPLSelector, self).__init__(
            source_dir, target_dir, source_file_path, target_file_path
        )
        self.threshold = threshold
        self.model_name = model_name
        self.device = device

    def __process__(self, data):
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)

        selected_data = []
        for i in tqdm(range(0, len(data))):
            input_text = data[i]["instruction"]
            encodings = tokenizer(input_text, return_tensors="pt")
            max_length = model.config.n_positions
            stride = 512
            seq_len = encodings.input_ids.size(1)

            nlls = []
            prev_end_loc = 0
            for begin_loc in range(0, seq_len, stride):
                end_loc = min(begin_loc + max_length, seq_len)
                trg_len = (
                    end_loc - prev_end_loc
                )  # may be different from stride on last loop
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
            ppl_score = ppl.item()

            if ppl > self.threshold:
                continue
            # if not isinstance(data[i], dict):
            #         data[i] = {}
            # data[i]["ppl_score"] = ppl_score
            selected_data.append(data[i])

        return selected_data
