# ChatGLM2Engine

> `ChatGLM2Engine` is the class for local ChatGLM2 model. ChatGLM2-6B is the second-generation version of the open-source bilingual (Chinese-English) chat model ChatGLM-6B based on General Language Model (GLM) framework.

> We load the model weights from Huggingface, see [here](https://huggingface.co/THUDM/chatglm2-6b) for more details. You can also load the model weights from your local disk.

**Example**

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
