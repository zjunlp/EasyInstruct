# Llama2Engine

> `Llama2Engine` is the class for local Llama2 model. Llama 2 is a collection of pretrained and fine-tuned generative text models ranging in scale from 7 billion to 70 billion parameters. This is the engine for the 7B pretrained model.

> We load the model weights from Huggingface, see [here](https://huggingface.co/meta-llama/Llama-2-7b) for more details. You can also load the model weights from your local disk.

**Example**

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
