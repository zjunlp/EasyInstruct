import openai
from typing import Optional

from easyinstruct.utils import API_NAME_DICT
from easyinstruct.utils import get_openai_key

class BasePrompt:
    """Base class for all prompts."""

    def __init__(self):
        self.prompt = None
        self.response = None

    def build_prompt(self, prompt: str):
        self.prompt = prompt
        return self.prompt
    
    def get_openai_result(self, 
                          engine = "gpt-3.5-turbo",
                          system_message: Optional[str] = "You are a helpful assistant.",
                          temperature: Optional[float] = 0, 
                          max_tokens: Optional[int] = 64, 
                          top_p: Optional[float] = 1.0, 
                          n: Optional[int] = 1,
                          frequency_penalty: Optional[float] = 0.0, 
                          presence_penalty: Optional[float] = 0.0
                          ):
        openai.api_key = get_openai_key()

        if engine in API_NAME_DICT["openai"]["gpt3"]:
            response = openai.Completion.create(
                model = engine,
                prompt = self.prompt,
                temperature = temperature,
                max_tokens = max_tokens,
                top_p = top_p,
                n = n,
                frequency_penalty = frequency_penalty,
                presence_penalty = presence_penalty,
            )

        elif engine in API_NAME_DICT["openai"]["chatgpt"]:
            response = openai.ChatCompletion.create(
                model = engine,
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": self.prompt}
                ],
                temperature = temperature,
                max_tokens = max_tokens,
                top_p = top_p,
                n = n,
                frequency_penalty = frequency_penalty,
                presence_penalty = presence_penalty,
            )

        else:
            print("[ERROR] Engine {engine} not found!".format(engine=engine))
            print("Available engines are as follows:")
            print(API_NAME_DICT["openai"])
            response = None
        
        self.response = response

        return response
    
    def get_google_result(self):
        raise NotImplementedError
    
    def get_baidu_result(self):
        raise NotImplementedError
    
    def get_anthropic_result(self):
        raise NotImplementedError
    
    def parse_response(self):
        raise NotImplementedError