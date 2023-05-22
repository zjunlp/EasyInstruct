# BasePrompt

> `BasePrompt` is the base class for all prompts.Currently we support building prompts to instruct LLM by calling LLM API service of OpenAI (GPT-3, ChatGPT) and Anthropic (Claude). We will support more available LLM products such as Llama in the future.

> You can also easily inherit this base class to customize your own prompt class. Just override the `build_prompt` method and `parse_response` method.

**Constructor**

`__init__(self)`

**Parameters**

None.

**Example**

```python
from easyinstruct import BasePrompt
prompts = BasePrompt()
```

**build\_prompt**

`build_prompt(self, prompt: str)`

**Description**

Build a prompt from a given string input.

**Parameters**

* `prompt` (str): The prompt string.

**Example**

```python
prompts.build_prompt("Give me three names of cats.")
```

**get\_openai\_result**

```python
get_openai_result(
    self, 
    engine = "gpt-3.5-turbo", 
    system_message:   Optional[str] = "You are a helpful assistant.", 
    temperature: Optional[float] = 0,
    max_tokens: Optional[int] = 64,
    top_p: Optional[float] = 1.0, 
    n: Optional[int] = 1, 
    frequency_penalty: Optional[float] = 0.0, 
    presence_penalty: Optional[float] = 0.0
)
```

**Description**

Get the response from OpenAI API.

**Parameters**

* `engine` (str): The OpenAI engine to use for the API call. Defaults to "gpt-3.5-turbo". Available engines include "text-davinci-003", "text-davinci-002", "code-davinci-002", "gpt-3.5-turbo", "gpt-3.5-turbo-0301".
* `system_message` (str): System messages provided to ChatGPT. Defaults to "You are a helpful assistant.".
* `temperature` (float): What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Defaults to 0.
* `max_tokens` (int): The maximum number of tokens to generate in the completion. Defaults to 1024.
* `top_p` (float): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. Defaults to 1.0.
* `n` (int): The number of completions to generate for each prompt. Defaults to 1.
* `frequency_penalty` (float): Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Defaults to 0.0.
* `presence_penalty` (float): Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Defaults to 0.0.

**Example**

```python
prompts.get_openai_result(engine = "gpt-3.5-turbo")
```

**get\_anthropic\_result**

```python
get_anthropic_result(
    self, 
    engine = "claude-v1",
    max_tokens_to_sample: Optional[int] = 1024,
    stop_sequences: List[str] = [anthropic.HUMAN_PROMPT],
    temperature: Optional[float] = 1,
    top_k: Optional[int] = -1,
    top_p: Optional[float] = -1
)
```

**Description**

Get the response from Anthropic API.

**Parameters**

* `engine` (str): The Anthropic engine to use for the API call. Defaults to "claude-v1". Available engines include "claude-v1", "claude-v1.0", "claude-v1.2", "claude-v1.3", "claude-instant-v1", "claude-instant-v1.0".
* `max_token_to_sample` (int): A maximum number of tokens to generate before stopping. Defaults to 1024.
* `stop_sequences` (List\[str]): A list of strings upon which to stop generating. You probably want `["\n\nHuman:"]`, as that's the cue for the next turn in the dialog agent.
* `temperature` (float): Amount of randomness injected into the response. Ranges from 0 to 1. Use temp closer to 0 for analytical / multiple choice, and temp closer to 1 for creative and generative tasks. Defaults to 1.
* `top_k` (int): Only sample from the top K options for each subsequent token. Used to remove "long tail" low probability responses. Defaults to -1, which disables it.
* `top_p` (float): Does nucleus sampling, in which we compute the cumulative distribution over all the options for each subsequent token in decreasing probability order and cut it off once it reaches a particular probability specified by `top_p`. Defaults to -1, which disables it. Note that you should either alter `temperature` or `top_p`, but not both.

**Example**

```python
prompts.get_anthropic_result(engine="claude-v1.2")
```

**get\_google\_result**

Reserved. Waiting for Google to release their API.

**get\_baidu\_result**

Reserved. Waiting for Baidu to release their API.

**parse\_response**

Implemented in subclasses.
