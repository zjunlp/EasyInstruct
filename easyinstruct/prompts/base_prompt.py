from openai import OpenAI
import anthropic
import cohere
from typing import Optional, Union, List

from easyinstruct.utils.api import API_NAME_DICT
from easyinstruct.utils.api import get_openai_key, get_anthropic_key, get_cohere_key
from easyinstruct.engines import BaseEngine


class BasePrompt:
    """Base class for all prompts."""

    def __init__(self):
        self.prompt = None
        self.response = None
        self.output = None

    def build_prompt(self, prompt: str):
        self.prompt = prompt
        return self.prompt

    def get_openai_result(
        self,
        engine="gpt-3.5-turbo",
        system_message: Optional[Union[str, List]] = "You are a helpful assistant.",
        temperature: Optional[float] = 0,
        max_tokens: Optional[int] = 1024,
        top_p: Optional[float] = 1.0,
        n: Optional[int] = 1,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
    ):
        client = OpenAI()
        self.engine = engine
        if engine in API_NAME_DICT["openai"]["gpt-3"]:
            response = client.completions.create(
                model=engine,
                prompt=self.prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                n=n,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
            )
            output = response.choices[0].text.strip()

        elif (
            engine in API_NAME_DICT["openai"]["gpt-3.5"]
            or engine in API_NAME_DICT["openai"]["gpt-4"]
        ):
            if isinstance(system_message, str):
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": self.prompt},
                ]
            elif isinstance(system_message, list):
                messages = system_message
            else:
                raise ValueError(
                    "system_message should be either a string or a list of strings."
                )

            response = client.chat.completions.create(
                model=engine,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                n=n,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
            )
            output = response.choices[0].message.content.strip()

        else:
            print("[ERROR] Engine {engine} not found!".format(engine=engine))
            print("Available engines are as follows:")
            print(API_NAME_DICT["openai"])
            response = None
            output = None

        self.response = response
        self.output = output

        return self.output

    def get_anthropic_result(
        self,
        engine="claude-2",
        max_tokens_to_sample: Optional[int] = 1024,
        stop_sequences: List[str] = [anthropic.HUMAN_PROMPT],
        temperature: Optional[float] = 1,
        top_k: Optional[int] = -1,
        top_p: Optional[float] = -1,
    ):
        client = anthropic.Anthropic(api_key=get_anthropic_key())

        if (
            engine in API_NAME_DICT["anthropic"]["claude"]
            or engine in API_NAME_DICT["anthropic"]["claude-instant"]
        ):
            response = client.completions.create(
                prompt=f"{anthropic.HUMAN_PROMPT} {self.prompt} {anthropic.AI_PROMPT}",
                model=engine,
                max_tokens_to_sample=max_tokens_to_sample,
                stop_sequences=stop_sequences,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
            )
            output = response.completion.strip()

        else:
            print("[ERROR] Engine {engine} not found!".format(engine=engine))
            print("Available engines are as follows:")
            print(API_NAME_DICT["anthropic"])
            response = None
            output = None

        self.response = response
        self.output = output

        return self.output

    def get_cohere_result(
        self,
        engine="command",
        max_tokens: Optional[int] = 1024,
        temperature: Optional[float] = 0.75,
        k: Optional[int] = 0,
        p: Optional[float] = 0.75,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
    ):
        co = cohere.Client(get_cohere_key())

        if engine in API_NAME_DICT["cohere"]:
            response = co.generate(
                prompt=self.prompt,
                model=engine,
                max_tokens=max_tokens,
                temperature=temperature,
                k=k,
                p=p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
            )
            output = response.generations[0].text.strip()

        else:
            print("[ERROR] Engine {engine} not found!".format(engine=engine))
            print("Available engines are as follows:")
            print(API_NAME_DICT["cohere"])
            response = None
            output = None

        self.response = response
        self.output = output

        return self.output

    def get_engine_result(self, engine: BaseEngine, **kwargs):
        self.output = engine.inference(self.prompt, **kwargs)
        return self.output

    def parse_response(self):
        raise NotImplementedError
