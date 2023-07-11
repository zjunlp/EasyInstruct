<div align="center">

<img src="figs/EasyInstruct.png" width="600px">

**An Easy-to-use Framework to Instruct Large Language Models.**

---

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#installation">Installation</a> •
  <a href="#use-easyinstruct">How To Use</a> •
  <a href="https://zjunlp.gitbook.io/easyinstruct/">Docs</a> •
  <a href="#citation">Citation</a> •
  <a href="#contributors">Contributors</a>
</p>

![](https://img.shields.io/badge/version-v0.0.5-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
![](https://img.shields.io/github/last-commit/zjunlp/EasyInstruct?color=green) 
![](https://img.shields.io/badge/PRs-Welcome-red) 

</div>


## 🔔News

- **2023-7-12 We release [EasyEdit](https://github.com/zjunlp/EasyEdit), an easy-to-use framework to edit Large Language Models.**
- **2023-5-23 We release version 0.0.5, removing requirement of llama-cpp-python.**
- **2023-5-16 We release version 0.0.4, fixing some problems.**
<details>
<summary><b>Previous news</b></summary>
  
- **2023-4-21 We release version 0.0.3. Check out our [documentations](https://zjunlp.gitbook.io/easyinstruct/documentations) for more details!**
- **2023-3-25 We release version 0.0.2, suporting IndexPrompt, MMPrompt, IEPrompt and more LLMs**
- **2023-3-13 We release version 0.0.1, supporting in-context learning, chain-of-thought with ChatGPT.**
  
</details>

---


## 🌟Overview

EasyInstruct is a Python package for instructing Large Language Models (LLM) like GPT-3, Llama, ChatGLM in your research experiments. It is designed to be easy to use and easy to extend.

[KnowLM](https://github.com/zjunlp/KnowLM) | [Falcon](https://github.com/falconry/falcon) | [Alpaca](https://github.com/tatsu-lab/stanford_alpaca) | [ChatGLM](https://github.com/THUDM/ChatGLM-6B) | [Chinese-LLaMA-Alpaca](https://github.com/ymcui/Chinese-LLaMA-Alpaca) | [MOSS](https://github.com/OpenLMLab/MOSS) | [Baize](https://github.com/project-baize/baize-chatbot) | [Vicuna](https://github.com/lm-sys/FastChat) | [BenTsao](https://github.com/SCIR-HI/Huatuo-Llama-Med-Chinese) | [Linly](https://github.com/CVI-SZU/Linly) | [ChatYuan](https://github.com/clue-ai/ChatYuan) | [Dolly](https://github.com/databrickslabs/dolly) | [MPT](https://github.com/mosaicml/llm-foundry) | [HuatuoGPT](https://github.com/FreedomIntelligence/HuatuoGPT) | [BayLing](https://github.com/ictnlp/BayLing)| [BELLE](https://github.com/LianjiaTech/BELLE) | [ChatGPT](https://chat.openai.com/)  

---

## 🔧Installation

**Installation using PyPI:**
```
pip install easyinstruct -i https://pypi.org/simple
```

**Installation for local development:**
```
git clone https://github.com/zjunlp/EasyInstruct
cd EasyInstruct
pip install -e .
```

---

## 📌Use EasyInstruct

Please refer to our [documentations](https://zjunlp.gitbook.io/easyinstruct/documentations) for more details.

### BasePrompt

> `BasePrompt` is the base class for all prompts.Currently we support building prompts to instruct LLM by calling LLM API service of OpenAI (GPT-3, ChatGPT) and Anthropic (Claude). 

> You can also easily inherit this base class to customize your own prompt class. Just override the `build_prompt` method and `parse_response` method.

**Example**

```python
from easyinstruct import BasePrompt
from easyinstruct.utils.api import set_openai_key

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Declare a prompt class
prompt = BasePrompt()

# Step3: Build a prompt
prompt.build_prompt("Give me three names of cats.")

# Step4: Get the result from LLM API service
prompt.get_openai_result(engine = "gpt-3.5-turbo")
```


### ICLPrompt

> `ICLPrompt` is the class for in-context learning prompts. You can desgin a few task-specific examples as prompt for instructing LLM, and then LLM can quickly figures out how to perform well on that task.

**Example**

```python
from easyinstruct import ICLPrompt
from easyinstruct.utils.api import set_openai_key

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Declare a prompt class
prompt = ICLPrompt()

# Step3: Desgin a few task-specific examples
in_context_examples = [{"text": "The cat is on the mat.", "label": "cat"}, {"text": "The dog is on the rug.", "label": "dog"}]

# Step4: Build a prompt from the examples
prompt.build_prompt("Identify the animals mentioned in the sentences.", in_context_examples, n_shots=2)

# Step5: Get the result from LLM API service
prompt.get_openai_result(engine="gpt-3.5-turbo")
```


### CoTPrompt

> Chain-of-Thought prompting is a recently developed prompting method, which encourages the LLM to explain its reasoning process when answering the prompt. This explanation of reasoning often leads to more accurate results. Specifically, we implement `FewshotCoTPrompt` and `ZeroshotCoTPrompt`.

#### FewshotCoTPrompt

> `FewshotCoTPrompt` is the class for few-shot Chain-of-Thought prompts. By showing the LLM some few shot exemplars where the reasoning process is explained in the exemplars, the LLM will also show the reasoning process when answering the prompt.

**Example**

```python
from easyinstruct import FewshotCoTPrompt
from easyinstruct.utils.api import set_openai_key

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Declare a prompt class
fewshot_prompt = FewshotCoTPrompt()

# Step3: Desgin a few Chain-of-Thought exemplars
in_context_examples = [{"question": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?", 
                        "answer": "Weng earns 12/60 = $<<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = $<<0.2*50=10>>10.\n#### 10"}]

# Step4: Build a prompt from the Chain-of-Thought exemplars
question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"
fewshot_prompt.build_prompt(question,  in_context_examples, n_shots=1)

# Step5: Get the result from LLM API service
fewshot_prompt.get_openai_result(engine="gpt-3.5-turbo")
```

#### ZeroshotCoTPrompt

> `ZeroshotCoTPrompt` is the class for few-shot Chain-of-Thought prompts. LLMs are demonstrated to be zero-shot reasoners by simply adding "Let's think step by step" before each answer, which is refered as Zeroshot-CoT.

**Example**

```python
from easyinstruct import FewshotCoTPrompt
from easyinstruct.utils.api import set_openai_key

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Declare a prompt class
zeroshot_prompt = ZeroshotCoTPrompt()

# Step3: Build a prompt
question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"
zeroshot_prompt.build_prompt(question)

# Step4: Get the result from LLM API service
zeroshot_prompt.get_openai_result(engine="gpt-3.5-turbo")
```


### IndexPrompt

> `IndexPrompt` is the class for retrieving from an index and concat the retrieved context information with the query input, to get the result from LLM.  The class is implemented based on `llama_index`.

> NOTE: the class only supports `SimpleVectorIndex` and `KGIndex` right now.

**Example**

```python
from easyinstruct import IndexPrompt
from easyinstruct.utils.api import set_openai_key

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Build a simple_vector_index
simple_index = IndexPrompt("simple_vector_index")
_ = simple_index.build_index("./data", chunk_size_limit=500) # return the documents
response = simple_index.query("Where is A.E Dimitra Efxeinoupolis club?")
print(response)
simple_index.save_to_disk("./index/simple_index.json")

# Step3: Build a kg_index
kg_index = IndexPrompt("kg_index")
kg_index.build_index("./data", llm_model_name="text-davinci-002", max_triplets_per_chunk=5, chunk_size_limit=512)

# Step4: Query the index
response = kg_index.query("Where is A.E Dimitra Efxeinoupolis club?")
kg_index.save_to_disk("./index/kg_index.json")
```

### IEPrompt

> `IEPrompt` is the class for information extraction prompt. We are now supporting Named Entity Recognition (ner), Relation Extraction (re), Event Extraction (ee), Relational Triple Extraction (rte) and Data Augmentation (da) for re.

**Example**

(Please see [Deepke llm](https://github.com/zjunlp/DeepKE/tree/main/example/llm) for more details)

```python
import os
import json
import hydra
from hydra import utils
import logging
from easyinstruct import IEPrompt
from .preprocess import prepare_examples

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg):

    cfg.cwd = utils.get_original_cwd()

    text = cfg.text_input

    if not cfg.api_key:
        raise ValueError("Need an API Key.")
    if cfg.engine not in ["text-davinci-003", "text-curie-001", "text-babbage-001", "text-ada-001"]:
        raise ValueError("The OpenAI model is not supported now.")

    os.environ['OPENAI_API_KEY'] = cfg.api_key

    ie_prompter = IEPrompt(cfg.task)

    examples = None
    if not cfg.zero_shot:
        examples = prepare_examples(cfg.data_path, cfg.task, cfg.language)

    if cfg.task == 're':
        ie_prompter.build_prompt(
            prompt=text,
            head_entity=cfg.head_entity,
            head_type=cfg.head_type,
            tail_entity=cfg.tail_entity,
            tail_type=cfg.tail_type,
            language=cfg.language,
            instruction=cfg.instruction,
            in_context=not cfg.zero_shot,
            domain=cfg.domain,
            labels=cfg.labels,
            examples=examples
        )
    else:
        ie_prompter.build_prompt(
            prompt=text,
            language=cfg.language,
            instruction=cfg.instruction,
            in_context=not cfg.zero_shot,
            domain=cfg.domain,
            labels=cfg.labels,
            examples=examples
        )

    result = ie_prompter.get_openai_result()
    logger.info(result)


if __name__ == '__main__':
    main()
```


### MMPrompt

> `MMPrompt` is the class for multimodal prompt, supporting input an image and question LLMs. We are now supporting two types of image encoding methods which are ASCII and caption.

**Example**

```python
from easyinstruct import MMPrompt
from easyinstruct.utils.api import set_openai_key

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Declare a prompt class
mm_prompt = MMPrompt(resize=24)

# Step3: Build a prompt
mm_prompt.build_prompt(prompt='What is the image about?',
                       img_path='',
                       encode_format='ASCII',
                       scale=10)

# Step4: Get the result from LLM API service
mm_prompt.get_openai_result(engine="gpt-3.5-turbo")
```

### BatchPrompt

> `BatchPrompt` is the class for batch prompts. Batch prompting is a simple alternative prompting approach that enables the LLM to run inference in batches, instead of one sample at a time. Batch prompting can reduce both token and time costs while retaining downstream performance.

**Example**

```python
from easyinstruct import BasePrompt, IEPrompt, ZeroshotCoTPrompt, FewshotCoTPrompt, BatchPrompt
from easyinstruct.utils.api import set_openai_key, set_anthropic_key, set_proxy

# Step1: Set your own API-KEY
set_openai_key("YOUR-KEY")

# Step2: Build the list of prompts in a batch

## baseprompt
prompts = BasePrompt()
prompts.build_prompt("Give me three names of cats.")

## ieprompt
in_context_examples = [{"Input": "Barcelona defeated Real Madrid 3-0 in a La Liga match on Saturday.",
                        "Output": "[{'E': 'Organization', 'W': 'Barcelona'}, {'E': 'Organization', 'W': 'Real Madrid'}, {'E': 'Competition', 'W': 'La Liga'}]"}]
ieprompts = IEPrompt(task='ner')
ieprompts.build_prompt(prompt="Japan began the defence of their Asian Cup title with a lucky 2-1 win against Syria in a Group C championship match on Friday.", examples=in_context_examples)

## cotprompt
question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"

in_context_examples = [{"question": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?","answer": "Weng earns 12/60 = $<<12/60=0.2>>0.2 per minute.Working 50 minutes, she earned 0.2 x 50 = $<<0.2*50=10>>10."}]

zeroshot_prompts = ZeroshotCoTPrompt()
zeroshot_prompts.build_prompt(question)

fewshot_prompts = FewshotCoTPrompt()
fewshot_prompts.build_prompt(question,
                             in_context_examples = in_context_examples,
                             n_shots = 1)

# Step3: Declare a batch prompt class
batch_prompt = BatchPrompt()

# Step4: Build all prompts in a batch
batch_prompt.build_prompt([prompts, ieprompts, zeroshot_prompts, fewshot_prompts])

# Step5: Get the result from LLM API service
batch_prompt.get_openai_result(engine = "gpt-3.5-turbo")

# Step6: Parse the response
batch_prompt.parse_response()
```

### llamaEngine
> `llamaEngine` is the class for local Llama models. It's an alternative to the openAI engine which supports local deployment.

**Example**
```python
from easyinstruct import llamaEngine
from transformers import GenerationConfig
# Step1: Initialize according to the your model path and the weight format
# Load the model in hf format
lengine=llamaEngine(base_path=YOUR_BASE_PATH,adapter_path=YOUR_ADAPTER_PATH,gpu=True,multi_gpu=True) 
# Load the model in cpp format
# lengine=llamaEngine(base_path=YOUR_BASE_PATH,gpu=False)

# Step2: do inference
generation_config = GenerationConfig(
                    temperature=0.6,
                    top_p=0.95,
                    repetition_penalty=1.15,
                )
print(lengine('介绍一下浙江大学',generation_config))
```

---
### 🚩Citation

Please cite our repository if you use EasyInstruct in your work.

```
@misc{easyinstruct,
  author = {Yixin Ou and Ningyu Zhang and Shengyu Mao and Runnan Fang and Yinuo Jiang and Ziwen Xu and Xiaolong Weng and Lei Li and Shuofei Qiao and Huajun Chen},
  title = {EasyInstruct: An Easy-to-use Framework to Instruct Large Language Models},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/zjunlp/EasyInstruct}},
}
```

---

## 🎉Contributors

<a href="https://github.com/zjunlp/EasyInstruct/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=zjunlp/EasyInstruct" />
</a>
