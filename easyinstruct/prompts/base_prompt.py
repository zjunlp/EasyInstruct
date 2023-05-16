import openai
import anthropic
from typing import Optional, Union, List

from easyinstruct.utils.api import API_NAME_DICT
from easyinstruct.utils.api import get_openai_key, get_anthropic_key
from easyinstruct.engines import llama_engine

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
                          system_message: Optional[Union[str, List]] = "You are a helpful assistant.",
                          temperature: Optional[float] = 0, 
                          max_tokens: Optional[int] = 1024, 
                          top_p: Optional[float] = 1.0, 
                          n: Optional[int] = 1,
                          frequency_penalty: Optional[float] = 0.0, 
                          presence_penalty: Optional[float] = 0.0
                          ):
        openai.api_key = get_openai_key()
        self.engine = engine
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
            output = response["choices"][0]["text"].strip()

        elif engine in API_NAME_DICT["openai"]["chatgpt"]:
            if isinstance(system_message, str):
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": self.prompt}
                ]
            elif isinstance(system_message, list):
                messages = system_message
            else:
                raise ValueError("system_message should be either a string or a list of strings.")

            response = openai.ChatCompletion.create(
                model = engine,
                messages = messages,
                temperature = temperature,
                max_tokens = max_tokens,
                top_p = top_p,
                n = n,
                frequency_penalty = frequency_penalty,
                presence_penalty = presence_penalty,
            )
            output = response["choices"][0]["message"]["content"].strip()

        else:
            print("[ERROR] Engine {engine} not found!".format(engine=engine))
            print("Available engines are as follows:")
            print(API_NAME_DICT["openai"])
            response = None
            output = None
        
        self.response = response

        return output
    
    def get_google_result(self):
        raise NotImplementedError
    
    def get_baidu_result(self):
        raise NotImplementedError
    
    def get_anthropic_result(self, 
                             engine = "claude-v1",
                             max_tokens_to_sample: Optional[int] = 1024,
                             stop_sequences: List[str] = [anthropic.HUMAN_PROMPT],
                             temperature: Optional[float] = 1,
                             top_k: Optional[int] = -1,
                             top_p: Optional[float] = -1,
                             ):
        client = anthropic.Client(get_anthropic_key())

        if engine in API_NAME_DICT["anthropic"]["claude"] or engine in API_NAME_DICT["anthropic"]["claude-instant"]:
            response = client.completion(
                prompt = f"{anthropic.HUMAN_PROMPT} {self.prompt} {anthropic.AI_PROMPT}",
                model = engine,
                max_tokens_to_sample = max_tokens_to_sample,
                stop_sequences = stop_sequences,
                temperature = temperature,
                top_k = top_k,
                top_p = top_p
            )
            output = response["completion"].strip()

        else:
            print("[ERROR] Engine {engine} not found!".format(engine=engine))
            print("Available engines are as follows:")
            print(API_NAME_DICT["anthropic"])
            response = None
            output = None

        self.response = response
        return output

    def get_llama_result(self,engine:llama_engine,**kwargs):
        return engine(self.prompt,**kwargs)

    def parse_response(self):
        raise NotImplementedError