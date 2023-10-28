# EvolInstructGenerator

> `EvolInstructGenerator` is the class for the instruction generation method of EvolInstruct. See [WizardLM: Empowering Large Language Models to Follow Complex Instructions](http://arxiv.org/abs/2304.12244) for more details.

**Example**

```python
from easyinstruct import EvolInstructGenerator
from easyinstruct.utils.api import set_openai_key

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Declare a generator class
generator = EvolInstructGenerator(num_instructions_to_generate=10)

# Step3: Generate evolution data
generator.generate()
```
