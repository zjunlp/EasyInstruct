# MMPrompt

> `MMPrompt` is the class for multimodal prompt, supporting input an image and question LLMs. We are now supporting two types of image encoding methods which are ASCII and caption.

**Constructor**

```python
__init__(self, resize=224)
```

**Parameters**

* `resize`(str): The size of the transformed image.

**Example**

```python
from easyinstruct import MMPrompt
mm_prompts = MMPrompt(resize=32)
```

**build\_prompt**

```python
build_prompt(self, 
    prompt: str,
    img_path: str,
    encode_format: str='ASCII',
    scale: float=10,
)
```

**Description**

Build a prompt from a given Image path and a question prompt.

**Parameters**

* `prompt` (str): The prompt string.
* `img_path` (str): The path of the input image.
* `encode_format` (str): The format to encode the input image. `ASCII` or `caption`.
* `scale` (float): Controll the encoding granularity in `ASCII` encoding format.


**Example**

```python
# ASCII
mm_prompts = MMPrompt(resize=24)
mm_prompts.build_prompt(prompt='What is the image about?',
                        img_path='',    # the image path
                        encode_format='ASCII',
                        scale=10
                    )
print(mm_prompts.get_openai_result(engine="text-davinci-003"))

# Caption
mm_prompts.build_prompt(prompt='What is the image about?',
                        img_path='',    # the image path
                        encode_format='caption'
                    )

print(mm_prompts.get_openai_result(engine="text-davinci-003"))
```
