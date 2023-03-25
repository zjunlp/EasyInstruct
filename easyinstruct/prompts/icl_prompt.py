from typing import Dict, List
from .base_prompt import BasePrompt

class ICLPrompt(BasePrompt):
    """Class for in-context learning prompt"""

    def __init__(self):
        super().__init__()

    def build_prompt(self, 
                     prompt: str,
                     in_context_examples: List[Dict] = None,
                     n_shots: int = 2
                     ):
                
        n_shots = min(len(in_context_examples), n_shots)

        context = ""
        for example in in_context_examples[:n_shots]:
            for key, value in example.items():
                context += key + ": " + value + "\n\n"

        self.prompt = context + prompt
        return self.prompt

