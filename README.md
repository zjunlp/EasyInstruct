# EasyInstruct

![](https://img.shields.io/badge/version-v0.0.2-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
![](https://img.shields.io/github/last-commit/zjunlp/EasyInstruct?color=green) 
![](https://img.shields.io/badge/PRs-Welcome-red) 


## Overview

EasyInstruct is a Python package for instructing Large Language Models(LLM) like GPT-3 in your research experiments. It is designed to be easy to use and easy to extend.


## Installation

**Installation using PyPI:**
```
pip install easyinstruct==0.0.2 -i https://pypi.org/simple
```

**Installation for local development:**
```
git clone https://github.com/zjunlp/EasyInstruct
cd EasyInstruct
pip install -e .
```

## Docs

### BasePrompt

BasePrompt is the base class for all prompts. To inject custom behavior you can subclass them and override the following methods:

- `build_prompt` - Build a prompt from a given input.
- `parse_response` - Parse the response from the response of LLM API.

#### Constructor

`__init__(self)`

**Parameters**

None.

**Example**

```python
from easyinstruct import BasePrompt
prompts = BasePrompt()
```

#### build_prompt

`build_prompt(self, prompt: str)`

**Description**

Build a prompt from a given string input.

**Parameters**

- `prompt` (str): The prompt string.

**Example**

```python
prompts.build_prompt("Give me three names of cats.")
```

#### get_openai_result

`get_openai_result(self, engine = "gpt-3.5-turbo", system_message: Optional[str] = "You are a helpful assistant.", temperature: Optional[float] = 0, max_tokens: Optional[int] = 64, top_p: Optional[float] = 1.0, n: Optional[int] = 1, frequency_penalty: Optional[float] = 0.0, presence_penalty: Optional[float] = 0.0)`

**Description**

Get the response from OpenAI API.

**Parameters**

- `engine` (str): The OpenAI engine to use for the API call. Defaults to "gpt-3.5-turbo". Available engines include "text-davinci-003", "text-davinci-002", "code-davinci-002", "gpt-3.5-turbo", "gpt-3.5-turbo-0301".
- `system_message` (str): System messages provided to ChatGPT. Defaults to "You are a helpful assistant.".
- `temperature` (float): What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Defaults to 0.
- `max_tokens` (int): The maximum number of tokens to generate in the completion. Defaults to 64.
- `top_p` (float): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. Defaults to 1.0.
- `n` (int): The number of completions to generate for each prompt. Defaults to 1.
- `frequency_penalty` (float): Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Defaults to 0.0.
- `presence_penalty` (float): Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Defaults to 0.0.

**Example**

```python
prompts.get_openai_result(engine = "gpt-3.5-turbo-0301")
```

#### get_google_result

Reserved. Waiting for Google to release their API.

#### get_baidu_result

Reserved. Waiting for Baidu to release their API.

#### get_anthropic_result

Reserved. Waiting for Anthropic to release their API.

#### parse_response

Implemented in subclasses.

### ICLPrompt

#### build_prompt

`build_prompt(self, prompt: str, in_context_examples: List[Dict] = None, n_shots: int = 2)`

**Description**

Build a prompt from a given string input and a list of in-context examples.

**Parameters**

- `prompt` (str): The prompt string.
- `in_context_examples` (List[Dict]): A list of in-context examples. Defaults to None.
- `n_shots` (int): The number of in-context examples to use. Defaults to 2.

**Example**

```python
from easyinstruct import ICLPrompt
prompts = ICLPrompt()
prompts.build_prompt("Identify the animals mentioned in the sentences.", in_context_examples = [{"text": "The cat is on the mat.", "label": "cat"}, {"text": "The dog is on the rug.", "label": "dog"}], n_shots = 2)
```

### CoTPrompt

#### FewshotCoTPrompt

##### build_prompt

`build_prompt(self, prompt: str, in_context_examples: List[Dict] = None, n_shots: int = 2)`

**Description**

Build a prompt from a given string input and a list of in-context examples.

**Parameters**

- `prompt` (str): The prompt string.
- `in_context_examples` (List[Dict]): A list of in-context examples. Defaults to None.
- `n_shots` (int): The number of in-context examples to use. Defaults to 2.

**Example**

```python
from easyinstruct import FewshotCoTPrompt

question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"
in_context_examples = [{"question": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?", 
                        "answer": "Weng earns 12/60 = $<<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = $<<0.2*50=10>>10.\n#### 10"}]

fewshot_prompts = FewshotCoTPrompt()
fewshot_prompts.build_prompt(question, 
                             in_context_examples = in_context_examples, 
                             n_shots = 1)
```

#### ZeroshotCoTPrompt

##### build_prompt

`build_prompt(self, prompt: str)`

**Description**

Build a prompt from a given string input.

**Parameters**

- `prompt` (str): The prompt string.

**Example**

```python
from easyinstruct import FewshotCoTPrompt

question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"

zeroshot_prompts = ZeroshotCoTPrompt()
zeroshot_prompts.build_prompt(question)
```

### IndexPrompt

> Class for retrieving from an index and concat the retrieved context information with the query input, to get the result from LLM.  The class is implemented based on `llama_index`.
>
> NOTE: the class only supports `SimpleVectorIndex` and `KGIndex` right now.

#### Constructor

`__init__(self, index_name="simple_vector_index", index_path=None)`

**Parameters**

* `index_name` (str): The type of index you want to build or load, should be in one of ["simple_vector_index", "kg_index" ].
* `index_path` (str): The path to your saved index file, default to be None. If provided, the index will be loaded during initializaion.

**Example**

```python
from easyinstruct.prompts import IndexPrompt
simple_index = IndexPrompt("simple_vector_index")
```

#### build_index

`build_index(self, data_path,  llm_model_name="text-davinci-002", chunk_size_limit=512, max_triplets_per_chunk=5)`

**Description**

Build a index on your custom data.

**Parameters**

* `data_path` (str): The document data path.
* `llm_model_name` (str): Large language model type to predict triplets from raw text. If not provided,  will use the default setting "text-dacinci-002" for prediction.
* `chunk_size_limit` (int): Chunk size limit. Default is 512 (4096 max input size).
* `max_triplets_per_chunk` (int): Triplets number limit. Default is 5.

**Returns**

* `List[Document]`: A list of documents. `Document` is a class from llama_index.

#### load_from_disk

`load_from_disk(self, index_path)`

Load index from saved path

**Parameters**

* `index_path` (str): The path to your saved index.

#### save_to_disk

`save_to_disk(self, save_path)`

**Description**

Save index to local path

**Parameters**

* `save_path` (str): The path to save your index.

#### query

`query(self, prompt)`

**Description**

Query for ChatGPT/GPT3. Retrieve from built index, and concat the retrieved knowledge with the input prompt.

**Parameters**

* `prompt` (str): your input question.

**Returns**

* `dict` : A response dict from LLM.

#### Examples

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

### IEPrompt

- In the Named Entity Recognition (ner) task, `text_input` parameter is the prediction text; `domain` is the domain of the prediction text, which can be empty; `label` is the entity label set, which can also be empty. 

- In the Relation Extraction (re) task, `text_input` parameter is the text; `domain` indicates the domain to which the text belongs, and it can be empty; `labels` is the set of relationship type labels. If there is no custom label set, this parameter can be empty; `head_entity` and `tail_entity` are the head entity and tail entity of the relationship to be predicted, respectively; `head_type` and `tail_type` are the types of the head and tail entities to be predicted in the relationship.

- In the Event Extraction (ee) task, `text_input` parameter is the prediction text; `domain` is the domain of the prediction text, which can also be empty. 

- In the Relational Triple Extraction (rte) task, `text_input` parameter is the prediction text; `domain` is the domain of the prediction text, which can also be empty.

- The specific meanings of other parameters are as follows:
  - `task` parameter is used to specify the task type, where `ner` represents named entity recognition task, `re` represents relation extraction task, `ee` represents event extraction task, and `rte` represents triple extraction task;
  - `language` indicates the language of the task, where `en` represents English extraction tasks, and `ch` represents Chinese extraction tasks;
  - `engine` indicates the name of the large model used, which should be consistent with the model name specified by the OpenAI API;
  - `api_key` is the user's API key;
  - `zero_shot` indicates whether zero-shot setting is used. When it is set to `True`, only the instruction prompt model is used for information extraction, and when it is set to `False`, in-context form is used for information extraction;
  - `instruction` parameter is used to specify the user-defined prompt instruction, and the default instruction is used when it is empty;
  - `data_path` indicates the directory where in-context examples are stored, and the default is the `data` folder.

Below are input and output examples for different tasks:

| Task |                            Input                             |                            Output                            |
| :--: | :----------------------------------------------------------: | :----------------------------------------------------------: |
| NER  | Japan began the defence of their Asian Cup title with a lucky 2-1 win against Syria in a Group C championship match on Friday. | [{'E': 'Country', 'W': 'Japan'}, {'E': 'Country', 'W': 'Syria'}, {'E': 'Competition', 'W': 'Asian Cup'}, {'E': 'Competition', 'W': 'Group C championship'}] |
|  RE  | The Dutch newspaper Brabants Dagblad said the boy was probably from Tilburg in the southern Netherlands and that he had been on safari in South Africa with his mother Trudy , 41, father Patrick, 40, and brother Enzo, 11. |                           parents                            |
|  EE  | In Baghdad, a cameraman died when an American tank fired on the Palestine Hotel. | event_list: [ event_type: [arguments: [role: "cameraman", argument: "Baghdad"], [role: "American tank", argument: "Palestine Hotel"]] ] |
| RTE  |    The most common audits were about waste and recycling.    | [['audit', 'type', 'waste'], ['audit', 'type', 'recycling']] |

### MMPrompt

TODO

See [docs](docs) folder for detailed documentation of the package.


## Contributors

<a href="https://github.com/zjunlp/EasyInstruct/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=zjunlp/EasyInstruct" />
</a>