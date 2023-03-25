# BasePrompt

BasePrompt is the base class for all prompts. To inject custom behavior you can subclass them and override the following methods:

- `build_prompt` - Build a prompt from a given input.
- `parse_response` - Parse the response from the response of LLM API.

## Constructor

`__init__(self)`

**Parameters**

None.

**Example**

```python
from easyinstruct import BasePrompt
prompts = BasePrompt()
```

## build_prompt

`build_prompt(self, prompt: str)`

**Description**

Build a prompt from a given string input.

**Parameters**

- `prompt` (str): The prompt string.

**Example**

```python
prompts.build_prompt("Give me three names of cats.")
```

## get_openai_response

`get_openai_result(self, engine = "gpt-3.5-turbo", system_message: Optional[str] = "You are a helpful assistant.", temperature: Optional[float] = 0, max_tokens: Optional[int] = 64, top_p: Optional[float] = 1.0, n: Optional[int] = 1, frequency_penalty: Optional[float] = 0.0, presence_penalty: Optional[float] = 0.0)`

**Description**

Get the response from OpenAI API.

**Parameters**

- `engine` (str): The OpenAI engine to use for the API call. Defaults to "gpt-3.5-turbo". Available engines include "text-davinci-003", "text-davinci-002", "code-davinci-002", "gpt-3.5-turbo", "gpt-3.5-turbo-0301".
- `system_message` (str): System messages provided to ChatGPT. Defaults to "You are a helpful assistant.".
- `temperature` (float): What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Defaults to 0.
- `max_tokens` (int): The maximum number of tokens to generate in the completion. Defaults to 64.
- `top_p` (float): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. Defaults to 1.0.
- `n` (int): The number of completions to generate for each prompt. Defaults to 1.
- `frequency_penalty` (float): Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Defaults to 0.0.
- `presence_penalty` (float): Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Defaults to 0.0.

**Example**

```python
prompts.get_openai_result(engine = "gpt-3.5-turbo-0301")
```

## get_google_response

Reserved. Waiting for Google to release their API.

## get_baidu_response

Reserved. Waiting for Baidu to release their API.

## get_anthropic_response

Reserved. Waiting for Anthropic to release their API.

## parse_response

Implemented in subclasses.