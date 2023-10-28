from transformers import AutoModel

from .base_engine import BaseEngine


class ChatGLM2Engine(BaseEngine):
    def __init__(
        self,
        pretrained_model_name_or_path: str = "THUDM/chatglm2-6b",
    ):
        super().__init__(pretrained_model_name_or_path)
        self.model = (
            AutoModel.from_pretrained(
                pretrained_model_name_or_path, trust_remote_code=True
            )
            .half()
            .cuda()
        )
        self.model = self.model.eval()

    def inference(self, text):
        response, history = self.model.chat(self.tokenizer, text, history=[])
        return response
