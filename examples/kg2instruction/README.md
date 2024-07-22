# KG2Instruction

- [KG2Instruction](#kg2instruction)
  - [Dataset Download and Use](#dataset-download-and-use)
    - [Dataset Download](#dataset-download)
    - [Data Format Conversion](#data-format-conversion)
    - [Evaluation](#evaluation)
  - [Prepare](#prepare)
    - [Configure environment](#configure-environment)
    - [Download Tools](#download-tools)
  - [Use KG2Instruction to obtain annotation samples for any text](#use-kg2instruction-to-obtain-annotation-samples-for-any-text)
  - [KG Distant Supervision](#kg-distant-supervision)
    - [1.Build Some Necessary Mappings (Optional, We provide pre-built mappings)](#1build-some-necessary-mappings-optional-we-provide-pre-built-mappings)
    - [2.Obtain Wikipedia Corpus (Optional, We provide cleaned Wikipedia documents)](#2obtain-wikipedia-corpus-optional-we-provide-cleaned-wikipedia-documents)
    - [3.Obtain Entities (Disambiguated)](#3obtain-entities-disambiguated)
    - [4.Match all relationships between each pair of entities and obtain entity types](#4match-all-relationships-between-each-pair-of-entities-and-obtain-entity-types)
    - [5.Text Topic Classification](#5text-topic-classification)
    - [6.Apply schema constraint relationships](#6apply-schema-constraint-relationships)
  - [Apply IE-LLM to Complete Missing Triples Due to KG Incompleteness](#apply-ie-llm-to-complete-missing-triples-due-to-kg-incompleteness)
    - [1.Train an existing IE large model with a small amount of domain data (optional, we provide IE large models trained on domain data)](#1train-an-existing-ie-large-model-with-a-small-amount-of-domain-data-optional-we-provide-ie-large-models-trained-on-domain-data)
    - [2.Use Trained IE Large Model to Supplement Missing Triples](#2use-trained-ie-large-model-to-supplement-missing-triples)
    - [3.Merge KG Distant Supervision Data and LLM Completion Data](#3merge-kg-distant-supervision-data-and-llm-completion-data)
  - [NLI Model Filtering Unrealistic Triples](#nli-model-filtering-unrealistic-triples)
  - [Acknowledgments](#acknowledgments)
  - [Citation](#citation)


## Dataset Download and Use


### Dataset Download

You can download the InstructIE dataset from [Hugging Face](https://huggingface.co/datasets/zjunlp/InstructIE).

The InstructIE dataset has files such as `train_zh.json`, `valid_zh.json`, `test_zh.json`, `schema_zh.json`, `train_en.json`, `valid_en.json`, `test_en.json`, and `schema_en.json`. Here, `_zh` indicates Chinese data and `_en` indicates English data. `train.json` is automatically produced by the KG2Instruction framework and may have some noise; `valid.json` and `test.json` are labeled through manual crowdsourcing.

The `schema.json` file is a dictionary of schema information in various fields. The **`key`** is the field name, and the **`value`** is two lists. The first list is the relationship types with head and tail entity types, and the second list is pure relationship types. The following is an example of schema information in the "event" field.


```json
"Event": [
    [
        "event_participant_organization/human",
        "event_scene_geographic region",
        "event_occurrence time_time",
        "event_alternative name_event",
        "event_sponsor_organization/human",
        "event_casualties_measure",
        "event_has cause_text",
        "event_has effect_text",
        "event_organizer_organization",
        "event_awards_profession",
        "event_winner_organization/human"
    ],
    [
        "participant",
        "scene",
        "occurrence time",
        "alternative name",
        "sponsor",
        "casualties",
        "has cause",
        "has effect",
        "organizer",
        "awards",
        "winner"
    ]
]
```

An example of a single piece of data in the dataset is shown as follows:


```json
{
  "id": "841ef2af4cfe766dd9295fb7daf321c299df0fd0cef14820dfcb421161eed4a1", 
  "cate": "Astronomy",
  "text": "NGC1313 is a galaxy in the constellation of Reticulum. It was discovered by the Australian astronomer James Dunlop on September 27, 1826. It has a prominent uneven shape, and its axis does not completely revolve around its center. Near NGC1313, there is another galaxy, NGC1309.", 
  "relation": [
    {"head": "NGC1313", "head_type": "astronomical object type", "relation": "time of discovery", "tail": "September 27, 1826", "tail_type": "time"}, 
    {"head": "NGC1313", "head_type": "astronomical object type", "relation": "discoverer or inventor", "tail": "James Dunlop", "tail_type": "organization/human"}, 
    {"head": "NGC1313", "head_type": "astronomical object type", "relation": "of", "tail": "Reticulum", "tail_type": "astronomical object type"}
  ]
}
```

Description of each field:

| Field    | Description                                                  |
| -------- | ------------------------------------------------------------ |
| id       | The unique identifier for each data point.                   |
| cate     | The domain of the text, with a total of 12 different domains. |
| text     | The input text. |
| relation | Annotate data in the format of (head, head_type, relation, tail, tail_type). |

> We also provided the **`entity`** field in the training set to perform entity naming recognition tasks, but we did not provide corresponding entity annotation data in the test set.

With the fields mentioned above, users can flexibly design and implement instructions and output formats for different information extraction needs.

Here is a simple data conversion script provided, which can convert the data in the above format into instruction data in the form of `instruction` and `output`.


### Data Format Conversion


Simple data conversion scripts are provided here. Through this script, the data in the above format can be converted into instruction data in the form of instruction and output.

**Conversion of Training Data Format**

```bash
python llm_cpl/build_instruction.py \
    --input_path data/example_en.json \
    --output_path data/example_en_ins.json \
    --mode train \
    --language en \
    --schema_path data/other/schema_en.json \
    --split_num -1
```


The splitting number can be set through `split_num`. For example, for domain data with 16 schemas, if split_num is set to 4, then one piece of data will be split into 4 pieces (16 // 4) of instruction data.

`input_path` can be directly replaced with the `train_en.json` and `valid_en.json` files in InstructIE.

Example of the converted data in the format of (`instruction`, `output`):

```json
{
    "instruction": "{\"instruction\": \"You are an expert in relationship extraction. Please extract relationship triples that match the schema definition from the input. Return an empty list for relationships that do not exist. Please respond in the format of a JSON string.\", \"schema\": [\"alternative name\", \"of\", \"time of discovery\", \"discoverer or inventor\", \"named after\", \"absolute magnitude\", \"diameter\", \"mass\"], \"input\": \"NGC1313 is a galaxy in the constellation of Reticulum. It was discovered by the Australian astronomer James Dunlop on September 27, 1826. It has a prominent uneven shape, and its axis does not completely revolve around its center. Near NGC1313, there is another galaxy, NGC1309.\"}", 
    "output": "{\"alternative name\": [], \"of\": [{\"subject\": \"NGC1313\", \"object\": \"Reticulum\"}], \"time of discovery\": [{\"subject\": \"NGC1313\", \"object\": \"September 27, 1826\"}], \"discoverer or inventor\": [{\"subject\": \"NGC1313\", \"object\": \"James Dunlop\"}], \"named after\": [], \"absolute magnitude\": [], \"diameter\": [], \"mass\": []}"
}
```


**Conversion of Test Data**


```bash
python llm_cpl/build_instruction.py \
    --input_path data/test_en.json \
    --output_path data/test_en_ins.json \
    --mode test \
    --language en \
    --schema_path data/other/schema_en.json \
    --split_num 4
```


> Note, `mode` needs to be converted to `test`

The difference between the conversion of test data and training data lies in that the test data generates the label field (consistent with the content of the relation field), which is used for subsequent F1 evaluation.


```json
{
  "id": "841ef2af4cfe766dd9295fb7daf321c299df0fd0cef14820dfcb421161eed4a1", 
  "cate": "Astronomy",
  "instruction": "{\"instruction\": \"You are an expert in relationship extraction. Please extract relationship triples that match the schema definition from the input. Return an empty list for relationships that do not exist. Please respond in the format of a JSON string.\", \"schema\": [\"alternative name\", \"of\", \"time of discovery\", \"discoverer or inventor\", \"named after\", \"absolute magnitude\", \"diameter\", \"mass\"], \"input\": \"NGC1313 is a galaxy in the constellation of Reticulum. It was discovered by the Australian astronomer James Dunlop on September 27, 1826. It has a prominent uneven shape, and its axis does not completely revolve around its center. Near NGC1313, there is another galaxy, NGC1309.\"}", 
  "label": [
    {"head": "NGC1313", "head_type": "astronomical object type", "relation": "time of discovery", "tail": "September 27, 1826", "tail_type": "time"}, 
    {"head": "NGC1313", "head_type": "astronomical object type", "relation": "discoverer or inventor", "tail": "James Dunlop", "tail_type": "organization/human"}, 
    {"head": "NGC1313", "head_type": "astronomical object type", "relation": "of", "tail": "Reticulum", "tail_type": "astronomical object type"}
  ]
}
```


### Evaluation

After the model makes inferences, the prediction results will be output in the `output` field.


```json
{
  "id": "841ef2af4cfe766dd9295fb7daf321c299df0fd0cef14820dfcb421161eed4a1", 
  "cate": "Astronomy",
  "instruction": "{\"instruction\": \"You are an expert in relationship extraction. Please extract relationship triples that match the schema definition from the input. Return an empty list for relationships that do not exist. Please respond in the format of a JSON string.\", \"schema\": [\"alternative name\", \"of\", \"time of discovery\", \"discoverer or inventor\", \"named after\", \"absolute magnitude\", \"diameter\", \"mass\"], \"input\": \"NGC1313 is a galaxy in the constellation of Reticulum. It was discovered by the Australian astronomer James Dunlop on September 27, 1826. It has a prominent uneven shape, and its axis does not completely revolve around its center. Near NGC1313, there is another galaxy, NGC1309.\"}", 
  "output": "{\"alternative name\": [], \"of\": [{\"subject\": \"NGC1313\", \"object\": \"Reticulum\"}], \"time of discovery\": [{\"subject\": \"NGC1313\", \"object\": \"September 27, 1826\"}], \"discoverer or inventor\": [{\"subject\": \"NGC1313\", \"object\": \"James Dunlop\"}], \"named after\": [], \"absolute magnitude\": [], \"diameter\": [], \"mass\": []}"
  "label": [
    {"head": "NGC1313", "head_type": "astronomical object type", "relation": "time of discovery", "tail": "September 27, 1826", "tail_type": "time"}, 
    {"head": "NGC1313", "head_type": "astronomical object type", "relation": "discoverer or inventor", "tail": "James Dunlop", "tail_type": "organization/human"}, 
    {"head": "NGC1313", "head_type": "astronomical object type", "relation": "of", "tail": "Reticulum", "tail_type": "astronomical object type"}
  ]
}
```

The output of the model and the true label can be evaluated through the following code:


```bash
python eval_func.py \
    --path1 results/eval_output.json \
    --task RE \
    --sort_by cate
```


## Prepare

### Configure environment

```bash
conda create -n kg2instruct python=3.8
pip install -r requirements.txt
```


### Download Tools

Before using the `KG2Instruction` framework, you need to download the following models and files:

1. **Wikidata (optional, we provide a pre-built mapping)**: You can download `latest-all.json.bz2` (i.e., all Wikidata entities) from [here](https://dumps.wikimedia.org/wikidatawiki/entities/).

2. **Wikipedia**: Download `enwiki-latest-pages-articles.xml.bz2` (i.e., English Wikipedia dumps) from [here](https://dumps.wikimedia.org/enwiki/latest/). **Note** that you can also access [hh001/InstructIE-original](https://huggingface.co/datasets/ghh001/InstructIE-original) download the HTML file of the cleaned Wikipedia article (corresponding to the file that has been cleaned).

3. **NER Model**: We use the following models for Chinese and English NER:
   - For Chinese NER: [hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH](https://file.hankcs.com/hanlp/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip)
   - For English NER: [hanlp.pretrained.mtl.UD_ONTONOTES_TOK_POS_LEM_FEA_NER_SRL_DEP_SDP_CON_XLMR_BASE](https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip)

4. **Text Domain Classification Models**: You can download the `text_classification_en` model from [Baidu Cloud Download](https://pan.baidu.com/s/1Xg_4fc0WvH6l5vQZahdQag?pwd=mgch) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

5. **Pre-built Wiki Entity-Relation Mapping**: You can download the (`wiki_en.db`, `alias_en.db`, `alias_rev_en.db`, `label_en.db`, `relation.db`) from [Baidu Cloud Download](https://pan.baidu.com/s/1SN2aUTnH5JHQMha1hk_ltw?pwd=6nc4) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

6. **Entity Type Mapping**: `enttypeid_mapper_en.json`, `enttypeid_mapper_zh.json`, **Chinese-English Relation Mapping**: `relation_map.json`, **NLI Templates**: `template.json`, **All Domain Schema Information**: `all_schema.json` [Baidu Cloud Download](https://pan.baidu.com/s/1Ypc2JYJbwVYgMHGG4EIxBQ?pwd=1ykk) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

7. **Pre-trained Information Extraction Large Language Model**: [zjunlp/OneKE](https://huggingface.co/zjunlp/OneKE)、50 manually annotated samples from various domains (`biaozhu_en.json`) [Baidu Cloud Download](https://pan.baidu.com/s/1Ykk5wGzI0PeYZzdcDrHdSg?pwd=yat8) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

8. **NLI Model**: [MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7) 

⚠️ **Note**: You can download the corresponding files and place them in the corresponding directory by running the [download_en.bash](./download_en.bash) script.


## Use KG2Instruction to obtain annotation samples for any text

Please make sure that all the files have been downloaded and placed correctly in the designated folders. 

[data/db/label_en.db](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/label_en.db.zip?download=true), [data/db/alias_en.db](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/alias_en.db.zip?download=true), [data/db/alias_rev_en.db](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/alias_rev_en.db.zip?download=true), and [data/db/relation.db](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/relation.db.zip?download=true) are placed under the `data/db` folder.

[data/other/relation_map.json](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/relation_map.json?download=true), [data/other/enttypeid_mapper_en.json](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/enttypeid_mapper_en.json?download=true), [data/other/template.json](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/template.json?download=true), [data/other/all_schema.json](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/all_schema.json?download=true) and [data/other/biaozhu_en.json](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/biaozhu_en.json?download=true) are placed under the `data/db/other` folder.

[model/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base](https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip), [model/text_classification_en](https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/text_classification_en.zip?download=true), [model/OneKE](https://huggingface.co/zjunlp/OneKE), and [model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7) are placed under the `model` folder.


```bash
python pipeline.py \
    "Taylor Swift was born on December 13, 1989 in Pennsylvania, the United States. She is a female pop singer and musician. In 2006, she released her debut self-titled music album《Taylor Swift》." \
    --language en \
    --label_db data/db/label_en.db \
    --alias_db data/db/alias_en.db \
    --alias_rev_db data/db/alias_rev_en.db \
    --relation_db data/db/relation.db \
    --relation_map_path data/other/relation_map.json \
    --enttypeid_mapper data/other/enttypeid_mapper_en.json \
    --template_path data/other/template.json \
    --schema_path data/other/all_schema.json \
    --ner_model model/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base \
    --cls_model model/text_classification_en \
    --ie_llm model/OneKE \
    --nli_model model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 \
    --prompt_name llama2_zh \
    --device 0 \
    --print_result
```

Output result:

```json
{
    "id": "9f8452fd7904a760e1fbce7c7b0246da0f03ecf682595168adea0f241dc369c7", 
    "text": "Taylor Swift was born on December 13, 1989 in Pennsylvania, the United States. She is a female pop singer and musician. In 2006, she released her debut self-titled music album《Taylor Swift》.", 
    "entity": [["Taylor Swift", "Q26876", "human/human"], ["Pennsylvania", "Q1400", "geographic_region/administrative_territorial_entity"], ["the United States", "Q30", "product/product"], ["2006", "Q2021", "time/time"], ["December 13, 1989", "time", "time/time"]], 
    "relation": [{"head": "Taylor Swift", "relation": "occupation", "tail": "pop singer"}, {"head": "Taylor Swift", "relation": "work", "tail": "Taylor Swift"}, {"head": "Taylor Swift", "relation": "date of birth", "tail": "December 13, 1989"}, {"head": "Taylor Swift", "relation": "occupation", "tail": "musician"}, {"head": "Taylor Swift", "relation": "country of citizenship", "tail": "the United States"}], 
    "cate": "Person"
}
```


## KG Distant Supervision

### 1.Build Some Necessary Mappings (Optional, We provide pre-built mappings)

**a. Construct the mapping between Wikipedia titles and Wikidata IDs (`wiki.db`)**

```bash
python build_db/build_wiki.py \
    ./Corpus/latest-all.json.bz2 \
    --language en \
    --db data/db/wiki_en.db
```
This will generate `wiki.db`. The same label may have different meanings and refer to different entities (IDs). The Wikipedia title is the disambiguated entity name, and in Wikipedia, links often exist in this disambiguated form.

**b. Construct the mapping between Wikidata IDs and labels, aliases (`alias.db`, `alias_rev.db`, `label.db`)**

```bash
python build_db/build_alias_label.py \
    ./Corpus/latest-all.json.bz2 \
    --language en \
    --db data/db/alias_en.db \
    --db_rev data/db/alias_rev_en.db \
    --label_db data/db/label_en.db
```
This will generate `alias.db`, `alias_rev.db`, and `label.db`. `alias.db` is the mapping between Wikidata IDs and entity mentions (one-to-many), `alias_rev.db` is the mapping between entity mentions and Wikidata IDs (one-to-many), and `label.db` is the mapping between Wikidata IDs and entity labels (one-to-one).

**c. Note: The Wikidata dump does not include redirects. To add them, you need to download Wikipedia's XML dump and then run**

```bash
python build_db/add_redirects.py \
    ./Corpus/enwiki-latest-pages-articles.xml.bz2 \
    --db data/db/wiki_en.db
```

**d. Construct the relationships between all Wikidata IDs (`relation.db`) and the non-entity relationships such as time and numerical values (`relation_value.db`)**

```bash
python build_db/build_relation.py \
    ./Corpus/latest-all.json.bz2 \
    --db data/db/relation.db \
    --db_value data/db/relation_value.db
```

We provide pre-built mappings. You can download the (`wiki_en.db`, `alias_en.db`, `alias_rev_en.db`, `label_en.db`, `relation.db`) from [Baidu Cloud Download](https://pan.baidu.com/s/1SN2aUTnH5JHQMha1hk_ltw?pwd=6nc4) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)



### 2.Obtain Wikipedia Corpus (Optional, We provide cleaned Wikipedia documents)

Download Wikipedia articles in HTML format, and clean them to obtain a more concise HTML format.

```bash
python kglm/parse_wikipedia.py \
    data/title/title.txt \
    data/clean/clean.json \
    --clean
```

We provide cleaned Wikipedia documents. You can also access [hh001/InstructIE-original](https://huggingface.co/datasets/ghh001/InstructIE-original) download the HTML file of the cleaned Wikipedia article (corresponding to the file that has been cleaned).


### 3.Obtain Entities (Disambiguated)

1. Divide Wikipedia articles into paragraphs, and obtain initial entity IDs and Chinese labels through the links in Wikipedia.
2. Identify the remaining entities using HanLP.
3. Merge the entities from steps 1 and 2.
4. Disambiguate the merged entities from step 3 to obtain unique IDs.

For the NER model, we use HanLP's [hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH](https://file.hankcs.com/hanlp/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip) (Chinese) and [hanlp.pretrained.mtl.UD_ONTONOTES_TOK_POS_LEM_FEA_NER_SRL_DEP_SDP_CON_XLMR_BASE](https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip) (English).


```bash
python kglm/process_html.py \
    data/en/clean/clean0.json \
    data/en/match/match0.json \
    --wiki_db data/db/wiki_en.db \
    --alias_db data/db/alias_en.db \
    --label_db data/db/label_en.db \
    --alias_rev_db data/db/alias_rev_en.db \
    --relation_db data/db/relation.db \
    --language en \
    --model model/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base \
    --device=0 \
    --chunk 5
```  


### 4.Match all relationships between each pair of entities and obtain entity types

```bash
python kglm/find_rel.py \
    data/en/match/match0.json \
    data/en/rel/rel0.json \
    --language en \
    --relation_db data/db/relation.db \
    --relation_value_db data/db/relation_value.db \
    --alias_db data/db/alias_en.db \
    --relation_map_path data/other/relation_map.json \
    --enttypeid_mapper data/other/enttypeid_mapper_en.json 
```


### 5.Text Topic Classification

We provide a trained text topic classification model, `text_classification_en`, which can be downloaded from here [Baidu Cloud Download](https://pan.baidu.com/s/1Xg_4fc0WvH6l5vQZahdQag?pwd=mgch) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)


**Predicting text topic classification results from a trained text topic classification model**

```bash
CUDA_VISIBLE_DEVICES="0" python cate_predict/infer_classification.py \
    data/en/rel/rel0.json \
    data/en/cate_output/predict_results0.txt \
    --cls_model output/text_classification_zh \
    --batch_size 16
```

**Merge the predicated results**

```bash
python cate_predict/topic_convert.py \
    --mode infer2newresult \
    --language en \
    --rel_path data/en/rel/rel0.json \
    --cate_predict_path data/en/cate_predict/predict_results0.txt \
    --cate_path data/en/cate 
```

This will generate a directory for each topic and the corresponding result files under the `data/en/cate` directory. For example: `data/en/cate/Person/result0.json`, `data/en/cate/Geographic_Location/result0.json`.


### 6.Apply schema constraint relationships

cate_list_en = ['Person', 'Geographic_Location', 'Building', 'Works', 'Creature', 'Artificial_Object', 'Natural_Science', 'Organization', 'Transport', 'Event', 'Astronomy', 'Medicine']

```bash
python cate_limit/relation_limit.py \
    data/en/cate/Person/result0.json \
    data/en/cate_limit/Person/result0.json \
    --language en \
    --cate Person \
    --schema_path data/other/all_schema.json 
```


## Apply IE-LLM to Complete Missing Triples Due to KG Incompleteness

### 1.Train an existing IE large model with a small amount of domain data (optional, we provide IE large models trained on domain data)

**Build training instruction data**


The `biaozhu_en.json` file contains fields `cate`, `text`, `entity`, `relation`, which need to be converted into `instruction`, `output` format suitable for direct model training.

```bash
python llm_cpl/build_instruction.py \
    --input_path data/biaozhu_en.json \
    --output_path data/instruction_train_en.json \
    --mode train \
    --language en \
    --schema_path data/other/schema_en.json
```

**Download the model that has been fine tuned with the universal domain information extraction instruction**

Download models [baichuan-inc/Baichuan2-13B-Chat](https://huggingface.co/baichuan-inc/Baichuan2-13B-Chat), [baichuan2-13b-iepile-lora](https://huggingface.co/zjunlp/baichuan2-13b-iepile-lora)


**Secondary training on domain data**

Refer to the official DeepKE tutorial [4.LoRA Fine-tuning](https://github.com/zjunlp/DeepKE/blob/main/example/llm/InstructKGC/README_CN.md#-4lora%E5%BE%AE%E8%B0%83) for secondary training of the model using the following command:

```bash
output_dir='lora/baichuan2-instructie-v1'
mkdir -p ${output_dir}
CUDA_VISIBLE_DEVICES="0" python llm_cpl/src/finetune.py \
    --do_train --do_eval \
    --overwrite_output_dir \
    --model_name_or_path 'baichuan-inc/Baichuan2-13B-Chat' \
    --checkpint_dir 'models/baichuan2-13b-iepile-lora' \
    --stage 'sft' \
    --model_name 'baichuan' \
    --template 'baichuan2' \
    --train_file 'data/instruction_train_en.json' \
    --val_set_size 50 \
    --output_dir=${output_dir} \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 2 \
    --gradient_accumulation_steps 4 \
    --preprocessing_num_workers 16 \
    --num_train_epochs 5 \
    --learning_rate 5e-5 \
    --max_grad_norm 0.5 \
    --optim "adamw_torch" \
    --max_source_length 510 \
    --cutoff_len 800 \
    --max_target_length 300 \
    --evaluation_strategy "epoch" \
    --save_strategy "epoch" \
    --save_total_limit 10 \
    --lora_r 8 \
    --lora_alpha 16 \
    --lora_dropout 0.05 \
    --fp16 \
    --bits 4 
```


**Merge the base model and LoRA weights**

```bash
CUDA_VISIBLE_DEVICES=0 python src/export_model.py \
    --model_name_or_path 'models/Baichuan2-13B-Chat' \
    --checkpoint_dir 'lora/baichuan2-instructie-v1/checkpoint-xxx' \
    --export_dir 'lora/baichuan2-instructie-v1/baichuan2-instructie-v1' \
    --stage 'sft' \
    --model_name 'baichuan' \
    --template 'baichuan2' \
    --output_dir 'lora_results/test'
```


Here is a pre-trained large-scale information extraction model [zjunlp/OneKE](https://huggingface.co/zjunlp/OneKE) available for use.


### 2.Use Trained IE Large Model to Supplement Missing Triples

**Convert the text to be extracted into instruction data format**

```bash
python llm_cpl/build_instruction.py \
    --input_path data/en/cate_limit/Person/result0.json \
    --output_path data/en/instruction/Person/result0.json \
    --mode test \
    --language en \
    --schema_path data/other/schema_en.json
```


**Call the model for prediction**


```bash
CUDA_VISIBLE_DEVICES=0 python llm_cpl/inference.py \
    --model_name_or_path 'lora/baichuan2-instructie-v1/baichuan2-instructie-v1' \
    --input_file 'data/en/instruction/Person/result0.json' \
    --output_file 'results/Person_result0.json' \
    --max_length 512 \
    --max_new_tokens 256
```

You can use `--use_vllm` to accelerate the generation speed through `vllm`, but there are certain requirements for the device, CUDA, and environment.


### 3.Merge KG Distant Supervision Data and LLM Completion Data

Convert the text results returned from IE-LLM extraction into a list structure:

```bash
python llm_cpl/extract.py \
    --path1 data/en/results/Peron_result0.json \
    --path2 data/en/llm_results/Person/result0.json
```


Merge KG distant supervision data and LLM completion data:

```bash
python llm_cpl/direct_merge.py \
    --path1 data/en/cate_limit/Person/result0.json \
    --path2 data/en/llm_results/Person/result0.json \
    --tgt_path data/en/merge/Person/result0.json 
```


## NLI Model Filtering Unrealistic Triples

```bash
python nli_filter/nli_filter.py \
    --input_path data/en/merge/Person/result0.json \
    --output_path data/en/nli_filtered/Person/result0.json \
    --device 0 \
    --threshold 0.5 \
    --language zh \
    --model_path model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 \
    --template_path data/other/template.json
```


## Acknowledgments

Some code is from [kglm-data](https://github.com/rloganiv/kglm-data), thank you!


## Citation

If you use the code or data from this project, please cite the following paper:

```
@article{DBLP:journals/corr/abs-2305-11527,
  author       = {Honghao Gui and Shuofei Qiao and Jintian Zhang and Hongbin Ye and Mengshu Sun and Lei Liang and Huajun Chen and Ningyu Zhang},
  title        = {InstructIE: A Bilingual Instruction-based Information Extraction Dataset},
  journal      = {CoRR},
  volume       = {abs/2305.11527},
  year         = {2023},
  url          = {https://doi.org/10.48550/arXiv.2305.11527},
  doi          = {10.48550/arXiv.2305.11527},
  eprinttype    = {arXiv},
  eprint       = {2305.11527},
  timestamp    = {Thu, 25 May 2023 15:41:47 +0200},
  biburl       = {https://dblp.org/rec/journals/corr/abs-2305-11527.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}
```