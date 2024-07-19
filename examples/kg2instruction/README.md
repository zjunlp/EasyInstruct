# KG2Instruction

- [KG2Instruction](#kg2instruction)
  - [Dataset Download and Use](#dataset-download-and-use)
  - [Prepare](#prepare)
    - [Configure environment](#configure-environment)
    - [Download Tools](#download-tools)
  - [Use KG2Instruction to obtain annotation samples for any text](#use-kg2instruction-to-obtain-annotation-samples-for-any-text)
  - [KG Distant Supervision](#kg-distant-supervision)
    - [1.Build Some Necessary Mappings](#1build-some-necessary-mappings)
    - [2.Obtain Wikipedia Corpus](#2obtain-wikipedia-corpus)
    - [3.Obtain Entities (Disambiguated)](#3obtain-entities-disambiguated)
    - [4.Match all relationships between each pair of entities and obtain entity types](#4match-all-relationships-between-each-pair-of-entities-and-obtain-entity-types)
    - [5.Text Topic Classification](#5text-topic-classification)
    - [6.Apply schema constraint relationships](#6apply-schema-constraint-relationships)
  - [Apply IE-LLM to Complete Missing Triples Due to KG Incompleteness](#apply-ie-llm-to-complete-missing-triples-due-to-kg-incompleteness)
    - [1.Build Training Instruction Data](#1build-training-instruction-data)
    - [2.Train Existing IE Large Model with Limited Domain Data](#2train-existing-ie-large-model-with-limited-domain-data)
    - [3.Use Trained IE Large Model to Supplement Missing Triples](#3use-trained-ie-large-model-to-supplement-missing-triples)
    - [4.Merge KG Distant Supervision Data and LLM Completion Data](#4merge-kg-distant-supervision-data-and-llm-completion-data)
  - [NLI Model Filtering Unrealistic Triples](#nli-model-filtering-unrealistic-triples)
  - [Acknowledgments](#acknowledgments)
  - [Citation](#citation)


## Dataset Download and Use

You can access it from [Hugging Face](https://huggingface.co/datasets/zjunlp/InstructIE) download the InstructIE dataset.

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
| cate     | The category of the text's subject, with a total of 12 different thematic categories. |
| text     | The input text for the model, with the goal of extracting all the involved relationship triples. |
| relation | Describes the relationship triples contained in the text, i.e., (head, head_type, relation, tail, tail_type). |

With the fields mentioned above, users can flexibly design and implement instructions and output formats for different information extraction needs.

> We also provided the **`entity`** field in the training set to perform entity naming recognition tasks, but we did not provide corresponding entity annotation data in the test set.

Here is a simple data conversion script provided, which can convert the data in the above format into instruction data in the form of `instruction` and `output`.

```bash
python llm_cpl/build_instruction.py \
    --input_path data/example_en.json \
    --output_path data/example_en_ins.json \
    --mode train \
    --language en \
    --schema_path data/other/schema_en.json \
    --split_num -1
```

Example:
```json
{
    "instruction": "{\"instruction\": \"You are an expert in relationship extraction. Please extract relationship triples that match the schema definition from the input. Return an empty list for relationships that do not exist. Please respond in the format of a JSON string.\", \"schema\": [\"alternative name\", \"of\", \"time of discovery\", \"discoverer or inventor\", \"named after\", \"absolute magnitude\", \"diameter\", \"mass\"], \"input\": \"NGC1313 is a galaxy in the constellation of Reticulum. It was discovered by the Australian astronomer James Dunlop on September 27, 1826. It has a prominent uneven shape, and its axis does not completely revolve around its center. Near NGC1313, there is another galaxy, NGC1309.\"}", 
    "output": "{\"alternative name\": [], \"of\": [{\"subject\": \"NGC1313\", \"object\": \"Reticulum\"}], \"time of discovery\": [{\"subject\": \"NGC1313\", \"object\": \"September 27, 1826\"}], \"discoverer or inventor\": [{\"subject\": \"NGC1313\", \"object\": \"James Dunlop\"}], \"named after\": [], \"absolute magnitude\": [], \"diameter\": [], \"mass\": []}"
}
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

2. **Wikipedia**: Download `enwiki-latest-pages-articles.xml.bz2` (i.e., English Wikipedia dumps) from [here](https://dumps.wikimedia.org/enwiki/latest/). **Note** that you can also access [hh001/InstructIE-original](https://huggingface.co/datasets/ghh001/InstructIE-original) download the HTML file of the cleaned Chinese Wikipedia article (corresponding to the file that has been cleaned).

3. **NER Model**: We use the following models for Chinese and English NER:
   - For Chinese NER: [hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH](https://file.hankcs.com/hanlp/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip)
   - For English NER: [hanlp.pretrained.mtl.UD_ONTONOTES_TOK_POS_LEM_FEA_NER_SRL_DEP_SDP_CON_XLMR_BASE](https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip)

4. **Pre-trained Topic Classification Models**: `text_classification_en`, `text_classification_zh` [Baidu Cloud Download](https://pan.baidu.com/s/1Xg_4fc0WvH6l5vQZahdQag?pwd=mgch) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

5. **Pre-built Chinese Wiki Entity-Relation Mapping** (`wiki_en.db`, `alias_en.db`, `alias_rev_en.db`, `label_en.db`, `relation.db`) [Baidu Cloud Download](https://pan.baidu.com/s/1SN2aUTnH5JHQMha1hk_ltw?pwd=6nc4) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

6. **Entity Type Mapping**: `enttypeid_mapper_en.json`, `enttypeid_mapper_zh.json`, **Chinese-English Relation Mapping**: `relation_map.json`, **NLI Templates**: `template.json`, **All Domain Schema Information**: `all_schema.json` [Baidu Cloud Download](https://pan.baidu.com/s/1Ypc2JYJbwVYgMHGG4EIxBQ?pwd=1ykk) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

7. **Pre-trained Information Extraction Large Model**: [zjunlp/OneKE](https://huggingface.co/zjunlp/OneKE)、50 manually annotated samples from various domains [Baidu Cloud Download](https://pan.baidu.com/s/1Ykk5wGzI0PeYZzdcDrHdSg?pwd=yat8) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

8. **NLI Model**: [MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7) 

⚠️ **Note**: In addition to Baidu Cloud, you can also download the corresponding files from [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main).



## Use KG2Instruction to obtain annotation samples for any text

```bash
python pipeline.py \
    "Adele Laurie Blue Adkins MBE (/əˈdɛl/;[4] born 5 May 1988), known mononymously as Adele, is an English singer-songwriter. She is known for her mezzo-sopran vocals and sentimental songwriting. Adele has received numerous accolades including 16 Grammy Awards, 12 Brit Awards (including three for British Album of the Year), an Academy Award, a Primetime Emmy Award, and a Golden Globe Award." \
    --language en \
    --label_db data/db/label_en.db \
    --alias_db data/db/alias_en.db \
    --alias_rev_db data/db/alias_rev_en.db \
    --relation_db data/db/relation.db \
    --relation_map_path data/other/relation_map.json \
    --enttypeid_mapper data/other/enttypeid_mapper_en.json \
    --ner_model model/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base \
    --cls_model model/text_classification_en \
    --ie_llm /nature/ghh/OneKE \
    --nli_model model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 \
    --template_path data/other/template.json \
    --schema_path data/other/all_schema.json \
    --prompt_name llama2_zh \
    --device 0 
```


## KG Distant Supervision

### 1.Build Some Necessary Mappings

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


### 2.Obtain Wikipedia Corpus

Download Wikipedia articles in HTML format, and clean them to obtain a more concise HTML format.

```bash
python kglm/parse_wikipedia.py \
    data/title/title.txt \
    data/clean/clean.json \
    --clean
```


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
    data/en/enttype/enttype0.json \
    --language en \
    --relation_db data/db/relation.db \
    --relation_value_db data/db/relation_value.db \
    --alias_db data/db/alias_en.db \
    --relation_map_path data/other/relation_map.json \
    --enttypeid_mapper data/other/enttypeid_mapper_en.json 
```


### 5.Text Topic Classification

**a. First, convert to the input format of the topic prediction model with the format `id`, `sentence`, `label` using `topic_convert.py`**

```bash
python cate_predict/topic_convert.py \
    --mode result2cate \
    --rel_path data/en/rel/rel0.json \
    --cate_input_path data/en/cate_input/cate0.json
```

**b. Fine-tune the text topic model**

```bash
bash cate_predict/finetune_cls.bash
```

**c. Use the fine-tuned text topic model to predict and get the results `cate_predict`**

```bash
bash cate_predict/infer.bash
```

**d. Obtain sentence topics from the prediction results `cate_predict`, and convert them to new results along with the `match`, `rel`, and `enttype` directories**

```bash
python cate_predict/topic_convert.py \
    --mode infer2newresult \
    --language en \
    --rel_path data/en/rel/rel0.json \
    --cate_predict_path data/en/cate_predict/predict_results0.txt \
    --cate_path data/en/cate 
```

This will generate a directory for each topic and the corresponding result files under the `data/zh/cate` directory. For example: `data/zh/cate/人物/result0.json`, `data/zh/cate/地理地区/result0.json`.


### 6.Apply schema constraint relationships

cate_list_zh = ['人物', '地理地区', '建筑', '作品', '生物','人造物件', '自然科学', '组织', '运输', '事件', '天文对象', '医学']
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


### 1.Build Training Instruction Data


The `biaozhu_en.json` file contains fields `cate`, `text`, `entity`, `relation`, which need to be converted into `instruction`, `output` format suitable for direct model training.

```bash
python llm_cpl/build_instruction.py \
    --input_path data/biaozhu_en.json \
    --output_path data/instruction_train_en.json \
    --mode train \
    --language en \
    --schema_path data/other/schema_en.json
```


### 2.Train Existing IE Large Model with Limited Domain Data

Download models [baichuan-inc/Baichuan2-13B-Chat](https://huggingface.co/baichuan-inc/Baichuan2-13B-Chat), [baichuan2-13b-iepile-lora](https://huggingface.co/zjunlp/baichuan2-13b-iepile-lora), and refer to the official DeepKE tutorial [4.LoRA Fine-tuning](https://github.com/zjunlp/DeepKE/blob/main/example/llm/InstructKGC/README_CN.md#-4lora%E5%BE%AE%E8%B0%83) for secondary training of the model using the following command:

```bash
output_dir='lora/baichuan2-instructie-v1'
mkdir -p ${output_dir}
CUDA_VISIBLE_DEVICES="0" python src/finetune.py \
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

Here is a pre-trained large-scale information extraction model [zjunlp/OneKE](https://huggingface.co/zjunlp/OneKE) available for use.


### 3.Use Trained IE Large Model to Supplement Missing Triples

Convert the text to be extracted into instruction data format:

```bash
python llm_cpl/build_instruction.py \
    --input_path data/en/cate_limit/Person/result0.json \
    --output_path data/en/instruction/Person/result0.json \
    --mode test \
    --language en \
    --schema_path data/other/schema_en.json
```


Refer to the official DeepKE tutorial [6.1 LoRA Prediction](https://github.com/zjunlp/DeepKE/blob/main/example/llm/InstructKGC/README_CN.md#61lora%E9%A2%84%E6%B5%8B) for model prediction using the following command:

First, merge the base model and LoRA weights, then predict domain texts to obtain extraction results.

```bash
CUDA_VISIBLE_DEVICES=0 python src/export_model.py \
    --model_name_or_path 'models/Baichuan2-13B-Chat' \
    --checkpoint_dir 'lora/baichuan2-instructie-v1/checkpoint-xxx' \
    --export_dir 'lora/baichuan2-instructie-v1/baichuan2-instructie-v1' \
    --stage 'sft' \
    --model_name 'baichuan' \
    --template 'baichuan2' \
    --output_dir 'lora_results/test'


CUDA_VISIBLE_DEVICES=0 python llm_cpl/inference.py \
    --model_name_or_path 'lora/baichuan2-instructie-v1/baichuan2-instructie-v1' \
    --input_file 'data/en/instruction/Person/result0.json' \
    --output_file 'results/Person_result0.json' 
```


### 4.Merge KG Distant Supervision Data and LLM Completion Data

Convert the text results returned from IE-LLM extraction into a list structure:

```bash
python llm_cpl/extract.py \
    --path1 results/Peron_result0.json \
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