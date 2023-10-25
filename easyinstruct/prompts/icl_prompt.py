from typing import Union, Dict, List
from .base_prompt import BasePrompt


class ICLPrompt(BasePrompt):
    """Class for in-context learning prompt"""

    def __init__(self):
        super().__init__()

    def build_prompt(
        self,
        prompt: str,
        in_context_examples: List[Union[str, Dict]] = None,
        n_shots: int = 2,
    ):
        n_shots = min(len(in_context_examples), n_shots)

        context = ""
        for idx, example in enumerate(in_context_examples[:n_shots]):
            if isinstance(example, str):
                context += f"{idx+1}. {example}\n"
            elif isinstance(example, dict):
                context += f"{idx+1}."
                for key, value in example.items():
                    context += f" {key}: {value}"
                context += "\n"
            else:
                raise TypeError(
                    "in_context_examples must be a list of strings or dicts"
                )

        self.prompt = context + prompt
        print(self.prompt)
        return self.prompt
