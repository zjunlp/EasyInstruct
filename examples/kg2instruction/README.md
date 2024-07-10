# KG2Instruction

- [KG2Instruction](#kg2instruction)
  - [1.构建一些必要的映射](#1构建一些必要的映射)
  - [2.下载HTML格式的Wikipedia文章](#2下载html格式的wikipedia文章)
  - [3.清洗Wikipedia文章](#3清洗wikipedia文章)
  - [4.按段落划分Wikipedia文章, 得到初步实体ID与中文标签](#4按段落划分wikipedia文章-得到初步实体id与中文标签)
  - [5.通过hanlp识别剩余实体](#5通过hanlp识别剩余实体)
  - [6.合并3、4中的实体](#6合并34中的实体)
  - [7.实体消歧,获得唯一ID](#7实体消歧获得唯一id)
  - [8.匹配每队实体间的所有关系](#8匹配每队实体间的所有关系)
  - [9.获取实体类型(双层)](#9获取实体类型双层)
  - [10.文本主题分类](#10文本主题分类)
  - [11.应用schema约束关系](#11应用schema约束关系)
  - [12.应用规则补齐](#12应用规则补齐)
  - [聚类采样](#聚类采样)
  - [12.负样本](#12负样本)
  - [13.NLI模型过滤](#13nli模型过滤)
- [Pipeline](#pipeline)


## 准备

### 配置环境
```bash
    conda create -n kg2instruct python=3.8
    pip install -r requirements.txt
```

### 下载工具
在使用KG2Instruction框架前您需要下载以下模型和文件: 
* Wikidata(可选, 我们提供构建好的映射): 你可以从[此处](https://dumps.wikimedia.org/wikidatawiki/entities/)下载`latest-all.json.bz2`(即所有Wikidata实体)。
* Wikipedia: 从[此处](https://dumps.wikimedia.org/zhwiki/latest/)下载`zhwiki-latest-pages-articles.xml.bz2`(即中文Wikipedia dumps)。**注意**你也可以从[ghh001/InstructIE-original-zh](https://huggingface.co/datasets/ghh001/InstructIE-original-zh)下载经过清洗操作后的中文wikipedia文章的html文件(对应经过`clean_html.py`后的文件)。
* NER模型: 我们采取hanlp中的[hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH](https://file.hankcs.com/hanlp/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip)（用于中文NER） 和 [hanlp.pretrained.mtl.UD_ONTONOTES_TOK_POS_LEM_FEA_NER_SRL_DEP_SDP_CON_XLMR_BASE](https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip)（用于英文NER）
* 训练好的主题分类模型: `text_classification_en`、`text_classification_zh` [百度云盘下载](https://pan.baidu.com/s/1Xg_4fc0WvH6l5vQZahdQag?pwd=mgch)
* 构建好的中文wiki实体关系映射(`wiki_zh.db`、`alias_zh.db`、`alias_rev_zh.db`、`label_zh.db`、`relation_zh.db`) [百度云盘下载](https://pan.baidu.com/s/1Ykk5wGzI0PeYZzdcDrHdSg?pwd=yat8)
* 实体类型映射: `enttypeid_mapper_en.json`、`enttypeid_mapper_zh.json`、中英文关系映射: `relation_map.json`、NLI模版: `template.json`、所有领域的schema信息: `all_schema.json` [百度云盘下载](https://pan.baidu.com/s/1Ypc2JYJbwVYgMHGG4EIxBQ?pwd=1ykk)
* 训练好的信息抽取大模型: [zjunlp/OneKE](https://huggingface.co/zjunlp/OneKE)
* NLI模型: [MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)


# 对任意文本使用KG2Instruction获得标注样本

```bash
python pipeline.py \
    "《三十而已》是一部由张晓波执导，江疏影、童瑶、毛晓彤等主演的都市情感剧，该剧于2020年7月17日在东方卫视首播，并在腾讯视频同步播出。" \
    --language zh \
    --label_db data/db/label_zh.db \
    --alias_db data/db/alias_zh.db \
    --alias_rev_db data/db/alias_rev_zh.db \
    --relation_db data/db/relation_zh.db \
    --relation_map_path data/other/relation_map.json \
    --enttypeid_mapper data/other/enttypeid_mapper_zh.json \
    --template_path data/other/template.json \
    --schema_path data/other/all_schema.json \
    --ner_model model/close_tok_pos_ner_srl_dep_sdp_con_electra_base \
    --cls_model model/text_classification_zh \
    --ie_llm /nature/ghh/OneKE \
    --nli_model model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 \
    --prompt_name llama2_zh \
    --device 0 
```


## 1.构建一些必要的映射
   
**a.构造wikipedia title与wikidata id之间的映射 wiki.db**

```bash
python build_db/build_wiki.py \
    ./Corpus/latest-all.json.bz2 \
    --language zh \
    --db data/db/wiki_zh.db
```
得到`wiki.db`, 相同名称(label)可能具有不同的含义, 指代不同的实体(id), wikipedia title是消歧义后的实体名称, 在wikipedia中链接往往是以这种消起义的名称存在的。


**b.构造wikidata id与label、alias(别名)之间的映射 alias.db、alias_rev.db、label.db**  

```bash
python build_db/build_alias_label.py \
    ./Corpus/latest-all.json.bz2 \
    --language zh \
    --db data/db/alias_zh.db \
    --db_rev data/db/alias_rev_zh.db \
    --label_db data/db/label_zh.db
```
得到`alias.db`、`alias_rev.db`、`label.db`, 其中alias.db是wikidata id与entity mention之间的映射(一对多), alias_rev.db是entity mention与wikidata id之间的映射(一对多), label.db是wikidata id与entity label之间的映射(一对一)


**c.注意：维基数据转储不包括重定向。要添加它们，您需要下载 Wikipedia 的 XML 转储，然后运行**

```bash
python build_db/add_redirects.py \
    ./Corpus/zhwiki-latest-pages-articles.xml.bz2 \
    --db data/db/wiki_zh.db
```


**d.构造所有wikidata id之间的关系 relation.db, 所有wikidata id的时间、数值等非实体关系关系 relation_value.db**

```bash
python build_db/build_relation.py \
    ./Corpus/latest-all.json.bz2 \
    --db data/db/relation.db \
    --db_value data/db/relation_value.db
```

## 2.获得文本语料 

### 下载HTML格式的Wikipedia文章(可跳过)

```bash
python kglm/parse_wikipdia.py \
    data/title/title.txt \
    data/raw/raw_articles.json
```


### 清洗Wikipedia文章(可跳过)

```bash
python kglm/clean_html.py \
    data/raw/raw_articles.json \
    data/clean/clean.json
```

你也可以从[ghh001/InstructIE-original-zh](https://huggingface.co/datasets/ghh001/InstructIE-original-zh)下载经过清洗操作后的中文wikipedia文章的html文件(对应经过`clean_html.py`后的文件)。


## 3.按段落划分Wikipedia文章, 得到初步实体ID与中文标签

```bash
python kglm/process_html.py \
    data/zh/clean/clean0.json \
    data/zh/process/process0.json \
    --wiki_db data/db/wiki_zh.db \
    --alias_rev_db data/db/alias_rev_zh.db \
    --language zh
```  

## 4.通过hanlp识别剩余实体

NER模型, 我们采取hanlp中的[hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH](https://file.hankcs.com/hanlp/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip)（中文） 和 [hanlp.pretrained.mtl.UD_ONTONOTES_TOK_POS_LEM_FEA_NER_SRL_DEP_SDP_CON_XLMR_BASE](https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip)（英文）

```bash
python kglm/hanlp_ner.py \
    data/zh/process/process0.json \
    data/zh/hanner/hanner0.json \
    --model model/close_tok_pos_ner_srl_dep_sdp_con_electra_base \
    --device=0 \
    --language zh \
    --chunk 5
```

## 5.合并3、4中的实体

```bash
python kglm/merge_ner.py \
    data/zh/process/process0.json \
    data/zh/hanner/hanner0.json \
    data/zh/merge/merge0.json \
    -j 8 \
    --language zh \
    --alias_rev_db data/db/alias_rev_zh.db
```

会对hanlp中识别的实体查询labels.db(所有别名与Qid的映射), 得到Qid, 如果没有Qid就保持原来hanlp中的类型, 对hanlp中识别的实体和通过wikipedia链接得到的实体进行合并, 原则是如果hanlp实体是wikipedia实体的子字符串, 就采用wikipedia实体。最终得到的实体是唯一的(句子中多次出现只记录一次)


## 6.实体消歧,获得唯一ID

```bash
python kglm/match_qid.py \
    data/zh/merge/merge0.json \
    data/zh/match/match0.json \
    -j 8 \
    --language zh \
    --relation_db data/db/relation.db \
    --alias_rev_db data/db/alias_rev_zh.db \
    --alias_db data/db/alias_zh.db \
    --label_db data/db/label_zh.db 
```


## 7.匹配每对实体间的所有关系

```bash
python kglm/find_rel.py \
    data/zh/match/match0.json \
    data/zh/rel/rel0.json \
    --language zh \
    --relation_db data/db/relation.db \
    --relation_value_db data/db/relation_value.db \
    --alias_db data/db/alias_zh.db 
```


## 8.获取实体类型

实体类型映射: `enttypeid_mapper_en.json`、`enttypeid_mapper_zh.json` 需下载

```bash
python kglm/convert_enttype.py \
    data/zh/rel/rel0.json \
    data/zh/enttype/enttype0.json \
    --language zh \
    --relation_db data/db/relation.db \
    --enttypeid_mapper data/other/enttypeid_mapper_zh.jsonp
```


## 9.文本主题分类

**a.先按照id、sentence、label格式转换成主题预测模型的输入格式 `topic_convert.py`**
```bash
python cate_predict/topic_convert.py \
    --mode result2cate \
    --match_path data/zh/match0.json \
    --rel_path data/zh/rel/rel0.json \
    --cate_input_path data/zh/cate_input/cate0.json
```

**b.微调文本主题模型**
```bash
bash cate_predict/finetune_cls.bash
```

**c.用微调后的文本主题模型预测得到结果cate_prdict**
```bash
bash cate_predict/infer.bash
```

**d.从预测结果cate_prdict中得到句子主题, 与match、rel、enttype目录一起转换为新的结果**
```bash
python cate_predict/topic_convert.py \
    --mode infer2newresult \
    --language zh \
    --match_path data/zh/match/match0.json \
    --rel_path data/zh/rel/rel0.json \
    --enttype_path data/zh/enttype/enttype0.json \
    --cate_predict_path data/zh/cate_predict/predict_results0.txt \
    --cate_path data/zh/cate 
```

会在 `data/zh/cate` 目录下面生成每个主题的目录已经相应的结果文件。例如：`data/zh/cate/人物/result0.json`、``data/zh/cate/地理地区/result0.json``


## 10.应用schema约束关系

cate_list_zh = ['人物', '地理地区', '建筑', '作品', '生物','人造物件', '自然科学', '组织', '运输', '事件', '天文对象', '医学']
cate_list_en = ['Person', 'Geographic_Location', 'Building', 'Works', 'Creature', 'Artificial_Object', 'Natural_Science', 'Organization', 'Transport', 'Event', 'Astronomy', 'Medicine']


```bash
python cate_limit/relation_limit.py \
    data/zh/cate/人物/result0.json \
    data/zh/cate_limit/人物/result0.json \
    --language zh \
    --cate 人物 \
    --schema_path data/other/all_schema.json 
```


## 11.应用IE-LLM补齐因KG不完整性缺少的三元组

**1.构建训练指令数据**

`valid_zh.json` 文件包含 `cate`、`text`、`entity`、`relation` 字段, 需要将其转换为能直接送入模型训练的 `instruction`、`output` 格式。

```bash
python llm_cpl/build_instruction.py \
    data/valid_zh.json \
    data/instruction_train_zh.json \
    --mode train \
    --language zh \
    --template_path data/other/template.json
```



**2.训练模型**

下载模型[baichuan-inc/Baichuan2-13B-Chat](https://huggingface.co/baichuan-inc/Baichuan2-13B-Chat)、[baichuan2-13b-iepile-lora](https://huggingface.co/zjunlp/baichuan2-13b-iepile-lora), 参照 DeepKE 官方教程 [4.LoRA微调](https://github.com/zjunlp/DeepKE/blob/main/example/llm/InstructKGC/README_CN.md#-4lora%E5%BE%AE%E8%B0%83) 进行模型二次训练, 可采用如下命令。

推荐环境:

```bash
pip install tiktoken
pip install peft==0.7.1
pip install transformers==4.41.2

pip install vllm==0.3.0
pip install jinja2==3.0.1
pip install pydantic==1.9.2

ip route add 8.8.8.8 via 127.0.0.1
```

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
    --train_file 'data/instruction_train_zh.json' \
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

**3.预测**

将待抽取文本转换成指令数据

```bash
python llm_cpl/build_instruction.py \
    data/zh/cate_limit/人物/result0.json \
    data/zh/instruction/人物/result0.json \
    --mode test \
    --language zh \
    --template_path data/other/template.json

python llm_cpl/build_instruction.py \
    data/en/cate_limit/Person/result0.json \
    data/en/instruction/Person/result0.json \
    --mode test \
    --language en \
    --template_path data/other/template.json
```



参照 DeepKE 官方教程 [6.1LoRA预测](https://github.com/zjunlp/DeepKE/blob/main/example/llm/InstructKGC/README_CN.md#61lora%E9%A2%84%E6%B5%8B) 使用模型进行预测, 可采用如下命令。

先合并底座模型和LoRA权重, 再对领域文本进行预测, 获得抽取结果。

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
    --input_file 'data/en/instruction/人物/result0.json' \
    --output_file 'results/人物_result0.json' 
```


**4.合并KG远程监督数据和LLM补充数据**

从IE-LLM抽取返回的文本结果转换到列表结构

```bash
python llm_cpl/extract.py \
    --path1 results/人物_result0.json \
    --path2 data/en/llm_results/人物/result0.json
```


合并KG远程监督数据和LLM补充数据
```bash
python llm_cpl/direct_merge.py \
    --path1 data/en/cate_limit/人物/result0.json \
    --path2 data/en/llm_results/人物/result0.json \
    --tgt_path data/en/merge/人物/result0.json 
```



## 12.NLI模型过滤

```bash
python nli_filter/nli_filter.py \
    --input_path data/en/merge/人物/result0.json \
    --output_path data/en/nli_filtered/人物/result0.json \
    --device 0 \
    --threshold 0.5 \
    --language zh \
    --template_path data/other/template.json
```



