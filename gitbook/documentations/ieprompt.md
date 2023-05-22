# IEPrompt

> `IEPrompt` is the class for information extraction prompt. We are now supporting Named Entity Recognition (ner), Relation Extraction (re), Event Extraction (ee), Relational Triple Extraction (rte) and Data Augmentation (da) for re.

**Constructor**

```python
__init__(self, task='ner')
```

**Parameters**

* `task`(str): The task name, should be in one of \["ner", "re", "ee", "rte", "da"].

**Example**

```python
from easyinstruct.prompts import IEPrompt
ie_prompt = IEPrompt("ner")
```

**build\_index**

```python
build_prompt(
    self, 
    prompt: str, 
    head_entity: str = None, 
    head_type: str = None, 
    tail_entity: str = None, 
    tail_type: str = None, 
    language: str = 'en', 
    instruction: str = None, 
    in_context: bool = False, 
    domain: str = None, 
    labels: List = None, 
    examples: Dict = None
)
```

* In the Named Entity Recognition (ner) task, `prompt` parameter is the prediction text; `domain` is the domain of the prediction text, which can be empty; `labels` is the entity label set, which can also be empty.
* In the Relation Extraction (re) task, `prompt` parameter is the text; `domain` indicates the domain to which the text belongs, and it can be empty; `labels` is the set of relationship type labels. If there is no custom label set, this parameter can be empty; `head_entity` and `tail_entity` are the head entity and tail entity of the relationship to be predicted, respectively; `head_type` and `tail_type` are the types of the head and tail entities to be predicted in the relationship.
* In the Event Extraction (ee) task, `prompt` parameter is the prediction text; `domain` is the domain of the prediction text, which can also be empty.
* In the Relational Triple Extraction (rte) task, `prompt` parameter is the prediction text; `domain` is the domain of the prediction text, which can also be empty.
* The specific meanings of other parameters are as follows:
  * `language` indicates the language of the task, where `en` represents English extraction tasks, and `ch` represents Chinese extraction tasks;
  * `in_context` indicates whether in-context learning is used. When it is set to `False`, only the instruction prompt model is used for information extraction, and when it is set to `True`, in-context form is used for information extraction;
  * `instruction` parameter is used to specify the user-defined prompt instruction, and the default instruction is used when it is empty;
  * `examples` are the in-context examples used for in-context learning. The formats are defined as follows:
    *   ner re ee

        ```python
        examples = {
        	"input" = "The input",
        	"output" = "The output"
        }
        ```
    *   re da

        ```python
        examples = {
        	"relation" = "The relation",
        	"context" = "The text to be extracted",
        	"head_entity" = "head entity",
        	"head_type" = "head entity type",
        	"tail_entity" = "tail entity",
        	"tail_type" = "tail entity type"
        }
        ```

**Examples**

(Please see [Deepke llm](https://github.com/zjunlp/DeepKE/tree/main/example/llm) for more details)

```python
import os
import json
import hydra
from hydra import utils
import logging
from easyinstruct.prompts import IEPrompt
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
