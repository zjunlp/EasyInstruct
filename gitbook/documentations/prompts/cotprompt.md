# CoTPrompt

> Chain-of-Thought prompting is a recently developed prompting method, which encourages the LLM to explain its reasoning process when answering the prompt. This explanation of reasoning often leads to more accurate results. Specifically, we implement `FewshotCoTPrompt` and `ZeroshotCoTPrompt`.

**FewshotCoTPrompt**

> `FewshotCoTPrompt` is the class for few-shot Chain-of-Thought prompts. By showing the LLM some few shot exemplars where the reasoning process is explained in the exemplars, the LLM will also show the reasoning process when answering the prompt.

**build\_prompt**

```python
build_prompt(
    self, prompt: str, 
    in_context_examples: List[Dict] = None, 
    n_shots: int = 2
)
```

**Description**

Build a prompt from a given string input and a list of in-context examples.

**Parameters**

* `prompt` (str): The prompt string.
* `in_context_examples` (List\[Dict]): A list of in-context examples. Defaults to None.
* `n_shots` (int): The number of in-context examples to use. Defaults to 2.

**Example**

```python
from easyinstruct import FewshotCoTPrompt

question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"
in_context_examples = [{"question": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?", 
                        "answer": "Weng earns 12/60 = $<<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = $<<0.2*50=10>>10.\n#### 10"}]

fewshot_prompts = FewshotCoTPrompt()
fewshot_prompts.build_prompt(
    question, 
    in_context_examples = in_context_examples, 
    n_shots = 1yP
)
```

**ZeroshotCoTPrompt**

> `ZeroshotCoTPrompt` is the class for few-shot Chain-of-Thought prompts. LLMs are demonstrated to be zero-shot reasoners by simply adding "Let's think step by step" before each answer, which is refered as Zeroshot-CoT.

**build\_prompt**

```python
build_prompt(self, prompt: str)
```

**Description**

Build a prompt from a given string input.

**Parameters**

* `prompt` (str): The prompt string.

**Example**

```python
from easyinstruct import FewshotCoTPrompt

question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"

zeroshot_prompts = ZeroshotCoTPrompt()
zeroshot_prompts.build_prompt(question)
```
