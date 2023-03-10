import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

class PromptBase:
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
        if engine in ["text-davinci-003", "text-davinci-002", "code-davinci-002"]:
            response = openai.Completion.create(
                model = engine,
                prompt = self.prompt,
                temperature = temperature,
                max_tokens = max_tokens,
                top_p = top_p,
                frequency_penalty = frequency_penalty,
                presence_penalty = presence_penalty,
            )
        elif engine in ["gpt-3.5-turbo", "gpt-3.5-turbo-0301"]:
            response = openai.ChatCompletion.create(
                model = engine,
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": self.prompt}
                ]    
            )
        
        self.response = response

        return response