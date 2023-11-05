<div align="center">

<img src="figs/logo.png" width="300px">

**An Easy-to-use Instruction Processing Framework for Large Language Models.**

---

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#installation">Installation</a> •
  <a href="#use-easyinstruct">How To Use</a> •
  <a href="https://zjunlp.gitbook.io/easyinstruct/">Docs</a> •
  <a href="#citation">Citation</a> •
  <a href="#contributors">Contributors</a>
</p>

![](https://img.shields.io/badge/version-v0.1.1-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
![](https://img.shields.io/github/last-commit/zjunlp/EasyInstruct?color=green) 
![](https://img.shields.io/badge/PRs-Welcome-red) 

</div>

## Table of Contents

- <a href="#news">What's New</a>
- <a href="#overview">Overview</a>
- <a href="#installation">Installation</a>
- <a href="#use-easyinstruct">Use EasyInstruct</a>
  - <a href="#generators">Generators</a>
  - <a href="#selectors">Selectors</a>
  - <a href="#prompts">Prompts</a>
  - <a href="#engines">Engines</a>
- <a href="#citation">Citation</a>
- <a href="#contributors">Contributors</a>

## 🔔News

- **2023-10-28 We release version 0.1.1, supporting for new features of instruction generation and instruction selection.**
- **2023-8-9 We release version 0.0.6, supporting Cohere API calls.**
- **2023-7-12 We release [EasyEdit](https://github.com/zjunlp/EasyEdit), an easy-to-use framework to edit Large Language Models.**
<details>
<summary><b>Previous news</b></summary>

- **2023-5-23 We release version 0.0.5, removing requirement of llama-cpp-python.**
- **2023-5-16 We release version 0.0.4, fixing some problems.**
- **2023-4-21 We release version 0.0.3, check out our [documentations](https://zjunlp.gitbook.io/easyinstruct/documentations) for more details.**
- **2023-3-25 We release version 0.0.2, suporting IndexPrompt, MMPrompt, IEPrompt and more LLMs**
- **2023-3-13 We release version 0.0.1, supporting in-context learning, chain-of-thought with ChatGPT.**
  
</details>

---

This repository is a subproject of [KnowLM](https://github.com/zjunlp/KnowLM).


## 🌟Overview

EasyInstruct is a Python package which is proposed as an easy-to-use instruction processing framework for Large Language Models(LLMs) like GPT-3, Llama, ChatGLM in your research experiments. EasyInstruct is designed to be easy to use and easy to extend.

[KnowLM](https://github.com/zjunlp/KnowLM) | [Falcon](https://github.com/falconry/falcon) | [Alpaca](https://github.com/tatsu-lab/stanford_alpaca) | [ChatGLM](https://github.com/THUDM/ChatGLM-6B) | [Chinese-LLaMA-Alpaca](https://github.com/ymcui/Chinese-LLaMA-Alpaca) | [MOSS](https://github.com/OpenLMLab/MOSS) | [Baize](https://github.com/project-baize/baize-chatbot) | [Vicuna](https://github.com/lm-sys/FastChat) | [BenTsao](https://github.com/SCIR-HI/Huatuo-Llama-Med-Chinese) | [Linly](https://github.com/CVI-SZU/Linly) | [ChatYuan](https://github.com/clue-ai/ChatYuan) | [Dolly](https://github.com/databrickslabs/dolly) | [MPT](https://github.com/mosaicml/llm-foundry) | [HuatuoGPT](https://github.com/FreedomIntelligence/HuatuoGPT) | [BayLing](https://github.com/ictnlp/BayLing)| [BELLE](https://github.com/LianjiaTech/BELLE) | [ChatGPT](https://chat.openai.com/)  

<img src="figs/overview.png">

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

### Generators

The `Generators` module streamlines the process of instruction data generation, allowing for the generation of instruction data based on seed data. You can choose the appropriate generator based on your specific needs.

#### BaseGenerator

> `BaseGenerator` is the base class for all generators.

> You can also easily inherit this base class to customize your own generator class. Just override the `__init__` and `generate` method.

#### SelfInstructGenerator

> `SelfInstructGenerator` is the class for the instruction generation method of Self-Instruct. See [Self-Instruct: Aligning Language Model with Self Generated Instructions](http://arxiv.org/abs/2212.10560) for more details.

<b>Example</b>

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

#### BackTranslationGenerator

> `BackTranslationGenerator` is the class for the instruction generation method of Instruction Backtranslation. See [Self-Alignment with Instruction Backtranslation](http://arxiv.org/abs/2308.06259) for more details.

<details>
<summary><b>Example</b></summary>

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

</details>

#### EvolInstructGenerator

> `EvolInstructGenerator` is the class for the instruction generation method of EvolInstruct. See [WizardLM: Empowering Large Language Models to Follow Complex Instructions](http://arxiv.org/abs/2304.12244) for more details.

<details>
<summary><b>Example</b></summary>

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

</details>

#### KG2InstructGenerator

> `KG2InstructGenerator` is the class for the instruction generation method of KG2Instruct. See [InstructIE: A Chinese Instruction-based Information Extraction Dataset](https://arxiv.org/abs/2305.11527) for more details.

### Selectors

The `Selectors` module standardizes the instruction selection process, enabling the extraction of high-quality instruction datasets from raw, unprocessed instruction data. The raw data can be sourced from publicly available instruction datasets or generated by the framework itself. You can choose the appropriate selector based on your specific needs.

#### BaseSelector

> `BaseSelector` is the base class for all selectors.

> You can also easily inherit this base class to customize your own selector class. Just override the `__init__` and `__process__` method.

#### Deduplicator

> `Deduplicator` is the class for eliminating duplicate instruction samples that could adversely affect both pre-training stability and the performance of LLMs. `Deduplicator` can also enables efficient use and optimization of storage space.

#### LengthSelector

> `LengthSelector` is the class for selecting instruction samples based on the length of the instruction. Instructions that are too long or too short can affect data quality and are not conducive to instruction tuning.

#### RougeSelector

> `RougeSelector` is the class for selecting instruction samples based on the ROUGE metric which is often used for evaluating the quality of automated generation of text.

#### GPTScoreSelector

> `GPTScoreSelector` is the class for selecting instruction samples based on the GPT score, which reflects whether the output is a good example of how AI Assistant should respond to the user's instruction, provided by ChatGPT.

#### PPLSelector

> `PPLSelector` is the class for selecting instruction samples based on the perplexity, which is the exponentiated average negative log-likelihood of response.

#### MTLDSelector

> `MTLDSelector` is the class for selecting instruction samples based on the MTLD, which is short for Measure of Textual Lexical Diversity.

#### MultiSelector

> `MultiSelector` is the class for combining multiple appropricate selectors based on your specific needs.

### Prompts

The `Prompts` module standardizes the instruction prompting step, where user requests are constructed as instruction prompts and sent to specific LLMs to obtain responses. You can choose the appropriate prompting method based on your specific needs.

<img src="figs/prompt.png">

Please check out <a href="https://github.com/zjunlp/EasyInstruct/blob/main/README_PROMPTS.md">link</a> for more detials.

### Engines

The `Engines` module standardizes the instruction execution process, enabling the execution of instruction prompts on specific locally deployed LLMs. You can choose the appropriate engine based on your specific needs.

Please check out <a href="https://github.com/zjunlp/EasyInstruct/blob/main/README_ENGINES.md">link</a> for more detials.

---
### 🚩Citation

Please cite our repository if you use EasyInstruct in your work.

```bibtex
@misc{easyinstruct,
  author = {Yixin Ou and Ningyu Zhang and Honghao Gui and Zhen Bi and Yida Xue and Runnan Fang and Kangwei Liu and Lei Li and Shuofei Qiao and Huajun Chen},
  title = {EasyInstruct: An Easy-to-use Instruction Processing Framework for Large Language Models},
  year = {2023},
  url = {https://github.com/zjunlp/EasyInstruct},
}

@misc{knowlm,
  author = {Ningyu Zhang and Jintian Zhang and Xiaohan Wang and Honghao Gui and Kangwei Liu and Yinuo Jiang and Xiang Chen and Shengyu Mao and Shuofei Qiao and Yuqi Zhu and Zhen Bi and Jing Chen and Xiaozhuan Liang and Yixin Ou and Runnan Fang and Zekun Xi and Xin Xu and Lei Li and Peng Wang and Mengru Wang and Yunzhi Yao and Bozhong Tian and Yin Fang and Guozhou Zheng and Huajun Chen},
  title = {KnowLM: An Open-sourced Knowledgeable Large Langugae Model Framework},
  year = {2023},
 url = {http://knowlm.zjukg.cn/},
}
```

---

## 🎉Contributors

<a href="https://github.com/zjunlp/EasyInstruct/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=zjunlp/EasyInstruct" />
</a>

We will offer long-term maintenance to fix bugs, solve issues and meet new requests. So if you have any problems, please put issues to us.