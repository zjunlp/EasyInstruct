import torch
import transformers

from .base_engine import BaseEngine


class Llama2Engine(BaseEngine):
    """Class for llama2 engine"""

    def __init__(
        self,
        pretrained_model_name_or_path: str = "meta-llama/Llama-2-7b",
    ):
        super().__init__(pretrained_model_name_or_path)
        self.pipline = transformers.pipeline(
            "text-generation",
            model=pretrained_model_name_or_path,
            torch_dtype=torch.float16,
            device_map="auto",
        )

    def inference(self, text, **kwargs):
        sequences = self.pipline(
            text,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
            max_length=200,
        )

        return sequences[0]["generated_text"]
