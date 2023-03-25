from .base_prompt import BasePrompt
from .icl_prompt import ICLPrompt

class FewshotCoTPrompt(ICLPrompt):
    """Class for few-shot Chain-of-Thoughts prompt"""

    def __init__(self):
        super().__init__()
        

class ZeroshotCoTPrompt(BasePrompt):
    """Class for zero-shot Chain-of-Thoughts prompt"""

    def __init__(self):
        super().__init__()

    def build_prompt(self, prompt: str):
        self.prompt = prompt + "Let's think step by step."
        return self.prompt