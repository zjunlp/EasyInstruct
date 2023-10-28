from transformers import AutoTokenizer


class BaseEngine:
    def __init__(self, pretrained_model_name_or_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path)

    def inference(self, text):
        raise NotImplementedError
