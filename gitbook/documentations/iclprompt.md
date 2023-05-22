# ICLPrompt

> `ICLPrompt` is the class for in-context learning prompts. You can desgin a few task-specific examples as prompt for instructing LLM, and then LLM can quickly figures out how to perform well on that task.

**build\_prompt**

```python
build_prompt(
    self, 
    prompt: str, 
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
from easyinstruct import ICLPrompt
prompts = ICLPrompt()
prompts.build_prompt("Identify the animals mentioned in the sentences.", in_context_examples = [{"text": "The cat is on the mat.", "label": "cat"}, {"text": "The dog is on the rug.", "label": "dog"}], n_shots = 2)
```
