# SelfInstructGenerator

> `SelfInstructGenerator` is the class for the instruction generation method of Self-Instruct. See [Self-Instruct: Aligning Language Model with Self Generated Instructions](http://arxiv.org/abs/2212.10560) for more details.

**Example**

```python
from easyinstruct import SelfInstructGenerator
from easyinstruct.utils.api import set_openai_key

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Declare a generator class
generator = SelfInstructGenerator(num_instructions_to_generate=10)

# Step3: Generate self-instruct data
generator.generate()
```
