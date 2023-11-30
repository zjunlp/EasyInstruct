# BaseGenerator

> `BaseGenerator` is the base class for all generators.

> You can also easily inherit this base class to customize your own generator class. Just override the `__init__` and `generate` method.

#### **Constructor**

```python
__init__(self, target_dir: str = "data/generations/")
```

**Parameters**

* `target_dir` (str): The specified directory to store the generated instruction files.&#x20;
