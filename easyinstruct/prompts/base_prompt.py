import openai
from easyinstruct.utils import API_NAME_DICT
from easyinstruct.utils import get_openai_key

class BasePrompt:
    """Base class for all prompts."""

    def __init__(self):
        self.prompt = None
        self.response = None

    def build_prompt(self, prompt):
        self.prompt = prompt
        return self.prompt
    
    def get_openai_result(self, 
                          engine="text-davinci-003", 
                          temperature=0, 
                          max_tokens=64, 
                          top_p=1.0, 
                          frequency_penalty=0.0, 
                          presence_penalty=0.0
                          ):
        openai.api_key = get_openai_key()

        if engine in API_NAME_DICT["gpt3"]:
            response = openai.Completion.create(
                model = engine,
                prompt = self.prompt,
                temperature = temperature,
                max_tokens = max_tokens,
                top_p = top_p,
                frequency_penalty = frequency_penalty,
                presence_penalty = presence_penalty,
            )
        elif engine in API_NAME_DICT["chatgpt"]:
            response = openai.ChatCompletion.create(
                model = engine,
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": self.prompt}
                ]    
            )
        else:
            print("[ERROR] Engine {engine} not found!".format(engine=engine))
            print("Available engines are as follows:")
            print(API_NAME_DICT)
            response = None
        
        self.response = response

        return response