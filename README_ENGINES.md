# Engines

The `Engines` module standardizes the instruction execution process, enabling the execution of instruction prompts on specific locally deployed LLMs. You can choose the appropriate engine based on your specific needs.

#### BaseEngine

> `BaseEngine` is the base class for all engines. It's an alternative to the LLM API service which supports local deployment.

> You can also easily inherit this base class to customize your own engine class. Just override the `__init__` and `inference` method.

#### Llama2Engine

> `Llama2Engine` is the class for local Llama2 model. Llama 2 is a collection of pretrained and fine-tuned generative text models ranging in scale from 7 billion to 70 billion parameters. This is the engine for the 7B pretrained model. 

> We load the model weights from Huggingface, see [here](https://huggingface.co/meta-llama/Llama-2-7b) for more details. You can also load the model weights from your local disk.

<b>Example</b>

```python
from easyinstruct import BasePrompt
from easyinstruct import Llama2Engine

# Step1: Declare a prompt class
prompt = BasePrompt()

# Step2: Build a prompt
prompt.build_prompt("Give me three names of cats.")

# Step3: Declare a engine class
engine = Llama2Engine()

# Step4: Get the result from locally deployed LLM
prompt.get_engine_result(engine = engine)
```

#### ChatGLM2Engine

> `ChatGLM2Engine` is the class for local ChatGLM2 model. ChatGLM2-6B is the second-generation version of the open-source bilingual (Chinese-English) chat model ChatGLM-6B based on General Language Model (GLM) framework.

> We load the model weights from Huggingface, see [here](https://huggingface.co/THUDM/chatglm2-6b) for more details. You can also load the model weights from your local disk.

<details>
<summary><b>Example</b></summary>

```python
from easyinstruct import BasePrompt
from easyinstruct import ChatGLM2Engine

# Step1: Declare a prompt class
prompt = BasePrompt()

# Step2: Build a prompt
prompt.build_prompt("Give me three names of cats.")

# Step3: Declare a engine class
engine = ChatGLM2Engine()

# Step4: Get the result from locally deployed LLM
prompt.get_engine_result(engine = engine)
```
</details>