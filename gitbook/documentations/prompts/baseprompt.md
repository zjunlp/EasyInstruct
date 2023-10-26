# BasePrompt

> `BasePrompt` is the base class for all prompts. Currently we support building prompts to instruct LLM by calling LLM API service of OpenAI (GPT-3, ChatGPT), Anthropic (Claude) and Cohere (Command) or by requesting locally deployed LLM like Llama2, ChatGLM2, etc. We will support more available LLM products in the future.

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

* `engine` (str): The OpenAI engine to use for the API call. Defaults to "gpt-3.5-turbo". Available engines include "text-davinci-003", "text-davinci-002", "gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613", "gpt-4", "gpt-4-0613", "gpt-4-0314".
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
    engine = "claude-2",
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

* `engine` (str): The Anthropic engine to use for the API call. Defaults to "claude-2". Available engines include "claude-2", "claude-2.0", "claude-instant-1", "claude-instant-1.2".
* `max_token_to_sample` (int): A maximum number of tokens to generate before stopping. Defaults to 1024.
* `stop_sequences` (List\[str]): A list of strings upon which to stop generating. You probably want `["\n\nHuman:"]`, as that's the cue for the next turn in the dialog agent.
* `temperature` (float): Amount of randomness injected into the response. Ranges from 0 to 1. Use temp closer to 0 for analytical / multiple choice, and temp closer to 1 for creative and generative tasks. Defaults to 1.
* `top_k` (int): Only sample from the top K options for each subsequent token. Used to remove "long tail" low probability responses. Defaults to -1, which disables it.
* `top_p` (float): Does nucleus sampling, in which we compute the cumulative distribution over all the options for each subsequent token in decreasing probability order and cut it off once it reaches a particular probability specified by `top_p`. Defaults to -1, which disables it. Note that you should either alter `temperature` or `top_p`, but not both.

**Example**

```python
prompts.get_anthropic_result(engine="claude-2")
```

**get\_cohere\_result**

```python
get_cohere_result(
    self, 
    engine = "command",
    max_tokens: Optional[int] = 1024,
    temperature: Optional[float] = 0.75,
    k: Optional[int] = 0,
    p: Optional[float] = 0.75,
    frequency_penalty: Optional[float] = 0.0,
    presence_penalty: Optional[float] = 0.0,
)
```

**Description**

Get the response from Anthropic API.

**Parameters**

* `engine` (str): The Cohere engine to use for the API call. Defaults to "command". Available engines include "command", "command-nightly", "command-light", "command-light-nightly".
* `max_tokens` (int): The maximum number of tokens the model will generate as part of the response. Defaults to 1024.
* `temperature` (float): A non-negative float that tunes the degree of randomness in generation. Lower temperatures mean less random generations. See [Temperature](https://docs.cohere.com/temperature-wiki) for more details. Defaults to 0.75.
* `k` (int): Ensures only the top `k` most likely tokens are considered for generation at each step. Defaults to 0, min value of 0, max value of 500.
* `p` (float): Ensures that only the most likely tokens, with total probability mass of `p`, are considered for generation at each step. If both `k` and `p` are enabled, `p` acts after `k`.\
  Defaults to 0.75, min value of 0.01, max value of 0.99.
* `frequency_penalty` (float): Used to reduce repetitiveness of generated tokens. The higher the value, the stronger a penalty is applied to previously present tokens, proportional to how many times they have already appeared in the prompt or prior generation.
* `presence_penalty` (float):  Can be used to reduce repetitiveness of generated tokens. Similar to `frequency_penalty`, except that this penalty is applied equally to all tokens that have already appeared, regardless of their exact frequencies. Defaults to 0.0, min value of 0.0, max value of 1.0.

**Example**

```python
prompts.get_cohere_result(engine="command")
```

**get\_engine\_result**

```python
get_engine_result(
    self, 
    engine: BaseEngine,
    **kwargs,
)
```

**Description**

Get the response from locally deployed LLM engine.

**Parameters**

* `engine` (BaseEngine): Instance of BaseEngine and all its subclasses. See [engines](../engines/ "mention") for more details.

**Example**

```python
engine = Llama2Engine()
prompts.get_engine_result(engine = engine)
```

**parse\_response**

Implemented in subclasses.
