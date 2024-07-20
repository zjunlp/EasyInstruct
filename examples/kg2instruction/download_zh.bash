# 确保你处在 EasyInstruct/examples/kg2instruction 目录下
cd EasyInstruct/examples/kg2instruction

# 下载清洗后的wikipedia语料
mkdir -p data/zh/clean
wget -O data/zh/clean/clean0.json https://huggingface.co/datasets/ghh001/InstructIE-original/resolve/main/clean0.json


# 下载wikidata映射数据
mkdir -p data/db
wget -O data/db/label_zh.db.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/label_zh.db.zip
unzip data/db/label_zh.db.zip -d data/db
wget -O data/db/alias_zh.db.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/alias_zh.db.zip
unzip data/db/alias_zh.db.zip -d data/db
wget -O data/db/alias_rev_zh.db.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/alias_rev_zh.db.zip
unzip data/db/alias_rev_zh.db.zip -d data/db
wget -O data/db/relation.db.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/relation.db.zip
unzip data/db/relation.db.zip -d data/db

# 下载其他数据
mkdir -p data/other
wget -O data/other/relation_map.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/relation_map.json
wget -O data/other/enttypeid_mapper_zh.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/enttypeid_mapper_zh.json
wget -O data/other/template.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/template.json
wget -O data/other/all_schema.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/all_schema.json
wget -O data/other/biaozhu_zh.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/biaozhu_zh.json

# 下载模型
mkdir -p model
wget -O model/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip https://file.hankcs.com/hanlp/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip
unzip model/close_tok_pos_ner_srl_dep_sdp_con_electra_base_20210111_124519.zip -d model
wget -O model/text_classification_zh.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/text_classification_zh.zip
unzip model/text_classification_zh.zip -d model

pip install -U huggingface_hub
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download --resume-download zjunlp/OneKE --local-dir model/OneKE
huggingface-cli download --resume-download MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 --local-dir model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
