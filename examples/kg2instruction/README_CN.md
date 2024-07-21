# KG2Instruction

- [KG2Instruction](#kg2instruction)
  - [数据集下载与使用](#数据集下载与使用)
  - [准备](#准备)
    - [配置环境](#配置环境)
    - [下载工具](#下载工具)
  - [对任意文本使用KG2Instruction获得标注样本](#对任意文本使用kg2instruction获得标注样本)
  - [KG远程监督](#kg远程监督)
    - [1.构建一些必要的映射(可跳过)](#1构建一些必要的映射可跳过)
    - [2.获得wikipedia语料(可跳过)](#2获得wikipedia语料可跳过)
    - [3.获得实体(消歧后的)](#3获得实体消歧后的)
    - [4.匹配每对实体间的所有关系且获得实体类型](#4匹配每对实体间的所有关系且获得实体类型)
    - [5.文本主题分类](#5文本主题分类)
    - [6.应用schema约束关系](#6应用schema约束关系)
  - [应用IE-LLM补齐因KG不完整性缺少的三元组](#应用ie-llm补齐因kg不完整性缺少的三元组)
    - [1.构建训练指令数据](#1构建训练指令数据)
    - [2.用少量领域数据训练已有IE大模型](#2用少量领域数据训练已有ie大模型)
    - [3.用训练好的IE大模型补充缺失三元组](#3用训练好的ie大模型补充缺失三元组)
    - [4.合并KG远程监督数据和LLM补充数据](#4合并kg远程监督数据和llm补充数据)
  - [NLI模型过滤不真实三元组](#nli模型过滤不真实三元组)
  - [致谢](#致谢)
  - [引用](#引用)


## 数据集下载与使用

你可以从[Hugging Face](https://huggingface.co/datasets/zjunlp/InstructIE)下载InstructIE数据集。

```json
{
  "id": "bac7c32c47fddd20966e4ece5111690c9ce3f4f798c7c9dfff7721f67d0c54a5", 
  "cate": "地理地区", 
  "text": "阿尔夫达尔（挪威语：Alvdal）是挪威的一个市镇，位于内陆郡，行政中心为阿尔夫达尔村。市镇面积为943平方公里，人口数量为2,424人（2018年），人口密度为每平方公里2.6人。", 
  "relation": [
    {"head": "阿尔夫达尔", "head_type": "地理地区", "relation": "面积", "tail": "943平方公里", "tail_type": "度量"}, 
    {"head": "阿尔夫达尔", "head_type": "地理地区", "relation": "别名", "tail": "Alvdal", "tail_type": "地理地区"}, 
    {"head": "内陆郡", "head_type": "地理地区", "relation": "位于", "tail": "挪威", "tail_type": "地理地区"}, 
    {"head": "阿尔夫达尔", "head_type": "地理地区", "relation": "位于", "tail": "内陆郡", "tail_type": "地理地区"}, 
    {"head": "阿尔夫达尔", "head_type": "地理地区", "relation": "人口", "tail": "2,424人", "tail_type": "度量"}
  ]
}
```

各字段的说明:

|   字段   |                             说明                             |
| :------: | :----------------------------------------------------------: |
|    id    | 每个数据点的唯一标识符。|
|   cate   | 文本的领域类别，总计12种不同的领域。|
|   text   | 输入文本。|
| relation | 标注数据，以(head, head_type, relation, tail, tail_type)的格式组成。|

> 在训练集中我们还提供了 **`entity`** 字段可以执行实体命名识别任务，但我们没有在测试集中提供相应的实体标注数据。

利用上述字段，用户可以灵活地设计和实施针对不同信息**抽取需求**的指令和**输出格式**。

这里提供了简单的数据转换脚本, 通过该脚本可以将上面格式的数据转换成 `instruction`、`output` 形式的指令数据。

```bash
python llm_cpl/build_instruction.py \
    --input_path data/example_zh.json \
    --output_path data/example_zh_ins.json \
    --mode train \
    --language zh \
    --schema_path data/other/schema_zh.json \
    --split_num -1
```

转换后数据的例子：

```json
{
    "instruction": "{\"instruction\": \"你是专门进行关系抽取的专家。请从input中抽取出符合schema定义的关系三元组，不存在的关系返回空列表。请按照JSON字符串的格式回答。\", \"schema\": [\"位于\", \"别名\", \"人口\", \"行政中心\", \"面积\", \"长度\", \"宽度\", \"海拔\"], \"input\": \"阿尔夫达尔（挪威语：Alvdal）是挪威的一个市镇，位于内陆郡，行政中心为阿尔夫达尔村。市镇面积为943平方公里，人口数量为2,424人（2018年），人口密度为每平方公里2.6人。\"}", 
    "output": "{\"位于\": [{\"subject\": \"阿尔夫达尔\", \"object\": \"内陆郡\"}, {\"subject\": \"内陆郡\", \"object\": \"挪威\"}], \"别名\": [{\"subject\": \"阿尔夫达尔\", \"object\": \"Alvdal\"}], \"人口\": [{\"subject\": \"阿尔夫达尔\", \"object\": \"2,424人\"}], \"行政中心\": [], \"面积\": [{\"subject\": \"阿尔夫达尔\", \"object\": \"943平方公里\"}], \"长度\": [], \"宽度\": [], \"海拔\": []}"
}
```

## 准备

### 配置环境

```bash
    conda create -n kg2instruct python=3.8
    pip install -r requirements.txt
```

### 下载工具
在使用KG2Instruction框架前您需要下载以下模型和文件: 
1. **Wikidata(可选, 我们提供构建好的映射)**: 你可以从[此处](https://dumps.wikimedia.org/wikidatawiki/entities/)下载`latest-all.json.bz2`(即所有Wikidata实体)。

2. **Wikipedia**: 从[此处](https://dumps.wikimedia.org/zhwiki/latest/)下载`zhwiki-latest-pages-articles.xml.bz2`(即中文Wikipedia dumps)。**注意**你也可以从[ghh001/InstructIE-original](https://huggingface.co/datasets/ghh001/InstructIE-original)下载经过清洗操作后的中文wikipedia文章的html文件(对应经过`clean_html.py`后的文件)。

3. **NER模型**: 我们采取hanlp中的[hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH](https://file.hankcs.com/hanlp/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip)（用于中文NER） 和 [hanlp.pretrained.mtl.UD_ONTONOTES_TOK_POS_LEM_FEA_NER_SRL_DEP_SDP_CON_XLMR_BASE](https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip)（用于英文NER）

4. **训练好的文本领域分类模型**: `text_classification_zh` 可以从这里下载 [百度云盘下载](https://pan.baidu.com/s/1Xg_4fc0WvH6l5vQZahdQag?pwd=mgch) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

5. **构建好的wiki实体关系映射**: (`wiki_zh.db`、`alias_zh.db`、`alias_rev_zh.db`、`label_zh.db`、`relation_zh.db`) 可以从这里下载 [百度云盘下载](https://pan.baidu.com/s/1Ykk5wGzI0PeYZzdcDrHdSg?pwd=yat8) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

6. **实体类型映射**: `enttypeid_mapper_en.json`、`enttypeid_mapper_zh.json`、中英文关系映射: `relation_map.json`、NLI模版: `template.json`、所有领域的schema信息: `all_schema.json` [百度云盘下载](https://pan.baidu.com/s/1Ypc2JYJbwVYgMHGG4EIxBQ?pwd=1ykk) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

7. **训练好的信息抽取大模型**: [zjunlp/OneKE](https://huggingface.co/zjunlp/OneKE)、人工标注的各个领域下的50条样本 `biaozhu_zh.json` [百度云盘下载](https://pan.baidu.com/s/1Ykk5wGzI0PeYZzdcDrHdSg?pwd=yat8)  | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)
   
8.  **NLI模型**: [MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)


⚠️**注意**：你可以通过运行 [download_zh.bash](./download_zh.bash) 脚本来下载相应的文件, 并放置在对应的目录下面。


## 对任意文本使用KG2Instruction获得标注样本

请确保所有的文件都已经下载, 并且正确的放置在指定的文件夹下, `data/db/label_zh.db`、`data/db/alias_zh.db`、`data/db/alias_rev_zh.db`、`data/db/relation_zh.db` 放在 `data/db` 文件夹下面， `data/other/relation_map.json` `data/other/enttypeid_mapper_zh.json` `data/other/template.json` `data/other/all_schema.json` `data/other/biaozhu_zh.json` 放在 `data/db/other` 文件夹下面， `model/close_tok_pos_ner_srl_dep_sdp_con_electra_base` `model/text_classification_zh` `model/OneKE` `model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` 放在 `model` 文件夹下面。

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
    --ie_llm model/OneKE \
    --nli_model model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 \
    --prompt_name llama2_zh \
    --device 0 \
    --print_result
```

输出结果:

```json
{
    "id": "7d30c9154153bfd116aa3760cd70307e5460069c09a4948a03f98cc4c7529514", 
    "text": "《三十而已》是一部由张晓波执导，江疏影、童瑶、毛晓彤等主演的都市情感剧，该剧于2020年7月17日在东方卫视首播，并在腾讯视频同步播出。", 
    "entity": [["三十而已", "Q97194938", "产品/作品"], ["江疏影", "Q15913516", "人物/人"], ["童瑶", "Q9049580", "人物/人"], ["毛晓彤", "Q8260142", "人物/人"], ["2020年7月17日", "Q57396819", "事件/事件"], ["东方卫视", "Q3356288", "组织/工商企业"], ["腾讯", "Q860580", "组织/工商企业"], ["2020年7月17日", "time", "时间/时间"]], 
    "relation": [{"head": "三十而已", "relation": "导演", "tail": "张晓波"}, {"head": "三十而已", "relation": "首播电视台", "tail": "东方卫视"}, {"head": "三十而已", "relation": "平台", "tail": "东方卫视"}, {"head": "三十而已", "relation": "演员", "tail": "毛晓彤"}, {"head": "三十而已", "relation": "出版时间", "tail": "2020年7月17日"}, {"head": "三十而已", "relation": "演员", "tail": "童瑶"}, {"head": "三十而已", "relation": "演员", "tail": "江疏影"}], 
    "cate": "作品"
}
```


## KG远程监督


### 1.构建一些必要的映射(可跳过)
   
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
    --db data/db/relation_zh.db \
    --db_value data/db/relation_value.db
```


### 2.获得wikipedia语料(可跳过)

下载HTML格式的Wikipedia文章(html格式), 并清洗(获得更精简的html格式)

```bash
python kglm/parse_wikipdia.py \
    data/title/title.txt \
    data/clean/clean.json \
    --clean
```

你也可以从[ghh001/InstructIE-original-zh](https://huggingface.co/datasets/ghh001/InstructIE-original-zh)下载经过清洗操作后的中文wikipedia文章的html文件(对应经过`clean_html.py`后的文件)。


### 3.获得实体(消歧后的)

1、按段落划分Wikipedia文章, 通过wikipeida中的链接得到初步实体ID与中文标签
2、通过hanlp识别剩余实体
3、合并1、2中的实体
4、对3中合并后的实体消歧, 获得唯一ID

NER模型, 我们采取hanlp中的[hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH](https://file.hankcs.com/hanlp/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip)（中文） 和 [hanlp.pretrained.mtl.UD_ONTONOTES_TOK_POS_LEM_FEA_NER_SRL_DEP_SDP_CON_XLMR_BASE](https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip)（英文）



```bash
python kglm/process_html.py \
    data/zh/clean/clean0.json \
    data/zh/match/match0.json \
    --wiki_db data/db/wiki_zh.db \
    --alias_db data/db/alias_zh.db \
    --label_db data/db/label_zh.db \
    --alias_rev_db data/db/alias_rev_zh.db \
    --relation_db data/db/relation.db \
    --language zh \
    --model model/close_tok_pos_ner_srl_dep_sdp_con_electra_base \
    --device=0 \
    --chunk 5
```  


### 4.匹配每对实体间的所有关系且获得实体类型

```bash
python kglm/find_rel.py \
    data/zh/match/match0.json \
    data/zh/enttype/enttype0.json \
    --language zh \
    --relation_db data/db/relation_zh.db \
    --relation_value_db data/db/relation_value.db \
    --alias_db data/db/alias_zh.db \
    --relation_map_path data/other/relation_map.json \
    --enttypeid_mapper data/other/enttypeid_mapper_zh.json 
```


### 5.文本主题分类

我们提供训练好的文本主题分类模型 `text_classification_zh` 可以从这里下载 [百度云盘下载](https://pan.baidu.com/s/1Xg_4fc0WvH6l5vQZahdQag?pwd=mgch) | [Hugging Face](https://huggingface.co/datasets/ghh001/InstructIE_tool/tree/main)

**从训练好的文本主题分类模型上预测文本主题分类结果**

```bash
CUDA_VISIBLE_DEVICES="0" python cate_predict/infer_classification.py \
    data/zh/rel/rel0.json \
    data/zh/cate_output/predict_results0.txt \
    --cls_model output/text_classification_zh \
    --batch_size 16
```

**合并预测结果**

```bash
python cate_predict/topic_convert.py \
    --mode infer2newresult \
    --language zh \
    --rel_path data/zh/rel/rel0.json \
    --cate_predict_path data/zh/cate_predict/predict_results0.txt \
    --cate_path data/zh/cate 
```

会在 `data/zh/cate` 目录下面生成每个主题的目录已经相应的结果文件。例如：`data/zh/cate/人物/result0.json`、`data/zh/cate/地理地区/result0.json`


### 6.应用schema约束关系

cate_list_zh = ['人物', '地理地区', '建筑', '作品', '生物','人造物件', '自然科学', '组织', '运输', '事件', '天文对象', '医学']

```bash
python cate_limit/relation_limit.py \
    data/zh/cate/人物/result0.json \
    data/zh/cate_limit/人物/result0.json \
    --language zh \
    --cate 人物 \
    --schema_path data/other/all_schema.json 
```


## 应用IE-LLM补齐因KG不完整性缺少的三元组

### 1.构建训练指令数据

`biaozhu_zh.json` 文件包含 `cate`、`text`、`entity`、`relation` 字段, 需要将其转换为能直接送入模型训练的 `instruction`、`output` 格式。


```bash
python llm_cpl/build_instruction.py \
    --input_path data/biaozhu_zh.json \
    --output_path data/instruction_train_zh.json \
    --mode train \
    --language zh \
    --schema_path data/other/schema_zh.json
```



### 2.用少量领域数据训练已有IE大模型

下载模型[baichuan-inc/Baichuan2-13B-Chat](https://huggingface.co/baichuan-inc/Baichuan2-13B-Chat)、[baichuan2-13b-iepile-lora](https://huggingface.co/zjunlp/baichuan2-13b-iepile-lora), 参照 DeepKE 官方教程 [4.LoRA微调](https://github.com/zjunlp/DeepKE/blob/main/example/llm/InstructKGC/README_CN.md#-4lora%E5%BE%AE%E8%B0%83) 进行模型二次训练, 可采用如下命令。


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

此处提供训练好的信息抽取大模型 [zjunlp/OneKE](https://huggingface.co/zjunlp/OneKE) 供使用。


### 3.用训练好的IE大模型补充缺失三元组

将待抽取文本转换成指令数据

```bash
python llm_cpl/build_instruction.py \
    --input_path data/zh/cate_limit/人物/result0.json \
    --output_path data/zh/instruction/人物/result0.json \
    --mode test \
    --language zh \
    --schema_path data/other/schema_zh.json
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
    --input_file 'data/zh/instruction/人物/result0.json' \
    --output_file 'results/人物_result0.json' 
```


### 4.合并KG远程监督数据和LLM补充数据

从IE-LLM抽取返回的文本结果转换到列表结构

```bash
python llm_cpl/extract.py \
    --path1 results/人物_result0.json \
    --path2 data/zh/llm_results/人物/result0.json
```


合并KG远程监督数据和LLM补充数据

```bash
python llm_cpl/direct_merge.py \
    --path1 data/zh/cate_limit/人物/result0.json \
    --path2 data/zh/llm_results/人物/result0.json \
    --tgt_path data/zh/merge/人物/result0.json 
```



## NLI模型过滤不真实三元组

```bash
python nli_filter/nli_filter.py \
    --input_path data/zh/merge/人物/result0.json \
    --output_path data/zh/nli_filtered/人物/result0.json \
    --device 0 \
    --threshold 0.5 \
    --language zh \
    --model_path model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 \
    --template_path data/other/template.json
```


## 致谢

部分代码来自于 [kglm-data](https://github.com/rloganiv/kglm-data), 感谢！


## 引用

如果您使用了本项目代码或数据，烦请引用下列论文:

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