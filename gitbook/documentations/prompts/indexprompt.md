# IndexPrompt

> `IndexPrompt` is the class for retrieving from an index and concat the retrieved context information with the query input, to get the result from LLM.  The class is implemented based on `llama_index`.

> NOTE: the class only supports `SimpleVectorIndex` and `KGIndex` right now.

**Constructor**

```python
__init__(self, index_name="simple_vector_index", index_path=None)
```

**Parameters**

* `index_name` (str): The type of index you want to build or load, should be in one of \["simple\_vector\_index", "kg\_index" ].
* `index_path` (str): The path to your saved index file, default to be None. If provided, the index will be loaded during initializaion.

**Example**

```python
from easyinstruct.prompts import IndexPrompt
simple_index = IndexPrompt("simple_vector_index")
```

**build\_index**

```python
build_index(
    self, 
    data_path, 
    llm_model_name="text-davinci-002", 
    chunk_size_limit=512, 
    max_triplets_per_chunk=5
)
```

**Description**

Build a index on your custom data.

**Parameters**

* `data_path` (str): The document data path.
* `llm_model_name` (str): Large language model type to predict triplets from raw text. If not provided, will use the default setting "text-dacinci-002" for prediction.
* `chunk_size_limit` (int): Chunk size limit. Default is 512 (4096 max input size).
* `max_triplets_per_chunk` (int): Triplets number limit. Default is 5.

**Returns**

* `List[Document]`: A list of documents. `Document` is a class from llama\_index.

**load\_from\_disk**

```python
load_from_disk(self, index_path)
```

Load index from saved path

**Parameters**

* `index_path` (str): The path to your saved index.

**save\_to\_disk**

```python
save_to_disk(self, save_path)
```

**Description**

Save index to local path

**Parameters**

* `save_path` (str): The path to save your index.

**query**

```python
query(self, prompt)
```

**Description**

Query for ChatGPT/GPT3. Retrieve from built index, and concat the retrieved knowledge with the input prompt.

**Parameters**

* `prompt` (str): your input question.

**Returns**

* `dict` : A response dict from LLM.

**Examples**

```python
from easyinstruct.prompts import IndexPrompt
from easyinstruct.utils import set_openai_key

# set your own API-KEY
set_openai_key("YOUR-KEY")

# example for building a simple_vector_index
simple_index = IndexPrompt("simple_vector_index")
_ = simple_index.build_index("./data", chunk_size_limit=500) # return the documents
response = simple_index.query("Where is A.E Dimitra Efxeinoupolis club?")
print(response)
simple_index.save_to_disk("./index/simple_index.json")

# example for building a kg_index
kg_index = IndexPrompt("kg_index")
_ = kg_index.build_index("./data", llm_model_name="text-davinci-002", max_triplets_per_chunk=5, chunk_size_limit=512)
response = kg_index.query("Where is A.E Dimitra Efxeinoupolis club?")
kg_index.save_to_disk("./index/kg_index.json")
print(response)

# example for loading a kg_index from local file
kg_load_index = IndexPrompt("kg_index", "./index/kg_index.json")
response = kg_load_index.query("Where is A.E Dimitra Efxeinoupolis club?")
print(response)
```
