# BacktranslationGenerator

> `BackTranslationGenerator` is the class for the instruction generation method of Instruction Backtranslation. See [Self-Alignment with Instruction Backtranslation](http://arxiv.org/abs/2308.06259) for more details.

**Example**

```python
from easyinstruct import BacktranslationGenerator
from easyinstruct.utils.api import set_openai_key

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Declare a generator class
generator = BacktranslationGenerator(num_instructions_to_generate=10)

# Step3: Generate backtranslation data
generator.generate()
```
