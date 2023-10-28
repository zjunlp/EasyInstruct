# 准备

## 配置环境
```bash
    conda create -n kg2instruct python=3.8
    pip install -r requirements.txt
```



## 数据
你可以从[此处](https://dumps.wikimedia.org/wikidatawiki/entities/)下载latest-all.json.bz2(即所有Wikidata实体), 从[此处](https://dumps.wikimedia.org/zhwiki/latest/)下载zhwiki-latest-pages-articles.xml.bz2(即中文Wikipedia dumps)。你也可以从[ghh001/InstructIE-original-zh](https://huggingface.co/datasets/ghh001/InstructIE-original-zh)下载经过清洗操作后的中文wikipedia文章的html文件(对应经过`clean_html.py`后的文件)。


NER模型, 我们采取hanlp中的[hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH](https://file.hankcs.com/hanlp/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip)（中文） 和 [hanlp.pretrained.mtl.UD_ONTONOTES_TOK_POS_LEM_FEA_NER_SRL_DEP_SDP_CON_XLMR_BASE](https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip)（英文）


构建好的中文映射(`wiki_zh.db`、`alias_zh.db`、`alias_rev_zh.db`、`label_zh.db`、`relation_zh.db`), 可从[百度云盘](https://pan.baidu.com/s/1hX5135_jHzUQHz_hz2R8WQ?pwd=mykq)下载, 提取码: mykq




# 构建一些必要的映射



a. 构造wikipedia title与wikidata id之间的映射 wiki.db  
```bash
    python build_db/build_wiki.py \
        /data/Corpus/latest-all.json.bz2 \
        --language zh \
        --db data/db/wiki_zh.db
```
得到wiki.db, 相同名称(label)可能具有不同的含义, 指代不同的实体(id), wikipedia title是消歧义后的实体名称, 在wikipedia中链接往往是以这种消起义的名称存在的。


b. 构造wikidata id与label、alias(别名)之间的映射 alias.db、alias_rev.db、label.db  
```bash
    python build_db/build_alias_label.py \
        /data/Corpus/latest-all.json.bz2 \
        --language zh \
        --db data/db/alias_zh.db \
        --db_rev data/db/alias_rev_zh.db \
        --label_db data/db/label_zh.db \
        --entities data/other/allowed_entity_zh.txt
```
得到alias.db、alias_rev.db、label.db、allowed_entity.txt, 其中alias.db是wikidata id与中文别名之间的映射(一对多), alias_rev.db是中文别名与wikidata id之间的映射(一对多), label.db是wikidata id与中文label之间的映射(一对一), allowed_entity.txt是所有具有中文别名的wikidata id


c. 注意：维基数据转储不包括重定向。要添加它们，您需要下载 Wikipedia 的 XML 转储，然后运行：
```bash
    python build_db/add_redirects.py \
        /data/Corpus/zhwiki-latest-pages-articles.xml.bz2 \
        --db data/db/wiki_zh.db \
        --entities data/other/allowed_entity_zh.txt
```


d. 构造所有wikidata id之间的关系 relation.db
```bash
    python build_db/build_relation.py \
        /newdisk3/data/guihh/Corpus/latest-all.json.bz2 \
        --db data/db/relation_zh.db 
```
--entities限制了只有出现在allowed_entity.txt中的实体(具有中文别名)才会考虑它与其他实体之间的关系


e. 构造所有wikidata id的时间、数值等非实体关系关系
```bash
python build_db/build_relation_value.py \
    /newdisk3/data/guihh/Corpus/latest-all.json.bz2 \
    --db data/db/relation_value.db 
```


# 对Wikipedia使用Wikidata进行KG2Instruction

1. 下载HTML格式的Wikipedia文章
```bash
    python src/parse_wikipdia.py \
        data/title/title.txt \
        data/raw/raw_articles0.json \
        --language zh
```


2. 清洗Wikipedia文章
```bash
    python src/clean_html.py \
        data/raw/raw_articles0.json \
        data/clean/clean0.json
```


3. 按段落划分Wikipedia文章、得到初步实体id与中文标签
```bash
    python src/process_html.py \
        data/zh/clean/clean0.json \
        data/zh/process/process0.json \
        --wiki_db data/db/wiki_zh.db \
        --alias_rev_db data/db/alias_rev_zh.db \
        --language zh
```  



4. hanlp运行剩余实体识别
```bash
    python src/hanlp_ner.py \
        data/zh/process/process0.json \
        data/zh/hanner/hanner0.json \
        --model model/close_tok_pos_ner_srl_dep_sdp_con_electra_base \
        --device 0 \
        --language zh 
```
对于LOC、PERSON、ORG等类型, hanlp识别地还算准确, 但是存在很多实体在wikidata中没有记录(没有Qid)



5. 合并3、4中的实体
```bash
    python src/merge_ner.py \
        data/zh/process/process0.json \
	    data/zh/hanner/hanner0.json \
	    data/zh/merge/merge1.json \
	    -j 8 \
	    --language zh \
	    --alias_rev_db data/db/alias_rev_zh.db
```
会对hanlp中识别的实体查询labels.db(所有别名与Qid的映射), 得到Qid, 如果没有Qid就保持原来hanlp中的类型, 对hanlp中识别的实体和通过wikipedia链接得到的实体进行合并, 原则是如果hanlp实体是wikipedia实体的子字符串, 就采用wikipedia实体。最终得到的实体是唯一的(句子中多次出现只记录一次)



6. 消歧义
```bash
    python src/match_qid.py \
        data/zh/merge/merge0.json \
        data/zh/match/match0.json \
        -j 8 \
        --language zh \
        --relation_db data/db/relation_zh.db \
        --alias_rev_db data/db/alias_rev_zh.db \
        --alias_db data/db/alias_zh.db \
        --label_db data/db/label_zh.db
```



7. 匹配关系
```bash
    python src/find_rel.py \
        data/zh/match/match0.json \
        data/zh/rel/rel0.json \
        --language zh \
        --relation_db data/db/relation_zh.db \
        --alias_db data/db/alias_zh.db
```



# 对任意文本使用Wikidata进行KG2Instruction

```bash
    python src/pipeline.py \
        "《三十而已》是一部由张晓波执导，江疏影、童瑶、毛晓彤等主演的都市情感剧，该剧于2020年7月17日在东方卫视首播，并在腾讯视频同步播出。" \
        --language zh \
        --label_db data/db/label_zh.db \
        --alias_db data/db/alias_zh.db \
        --alias_rev_db data/db/alias_rev_zh.db \
        --relation_db data/db/relation_zh.db \
        --relation_map_path data/other/relation_map.json \
        --model model/close_tok_pos_ner_srl_dep_sdp_con_electra_base \
        --device 0
```



# 感谢

部分代码来自于 [kglm-data](https://github.com/rloganiv/kglm-data), 感谢！


# 引用

如果您使用了本项目代码或数据，烦请引用下列论文:
```bibtex
@article{DBLP:journals/corr/abs-2305-11527,
  author       = {Honghao Gui and
                  Jintian Zhang and
                  Hongbin Ye and
                  Ningyu Zhang},
  title        = {InstructIE: {A} Chinese Instruction-based Information Extraction Dataset},
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
