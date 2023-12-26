# CodeSelector

> `CodeSelector` is the class for selecting code instruction samples based on the Complexity-Impacted Reasoning Score (CIRS), which combines structural and logical attributes, to measure the correlation between code and reasoning abilities. See [When Do Program-of-Thoughts Work for Reasoning?](https://arxiv.org/abs/2308.15452) for more details.

**Example**

```python
from easyinstruct import CodeSelector

# Step1: Specify your source file of code instructions
src_file = "data/code_example.json"

# Step2: Declare a code selecter class
selector = CodeSelector(
    source_file_path=src_file, 
    target_dir="data/selections/",
    manually_partion_data=True,
    min_boundary = 0.125,
    max_boundary = 0.5,
    automatically_partion_data = True,
    k_means_cluster_number = 2,
    )

# Step3: Process the code instructions
selector.process()
```
