# Make sure you are in the EasyInstruction/examples/kg2instruction directory
cd EasyInstruct/examples/kg2instruction


# Download the cleaned Wikipedia corpus
mkdir -p data/en/clean
wget -O data/en/clean/clean0.json https://huggingface.co/datasets/ghh001/InstructIE-original/resolve/main/clean_en0.json


# Download wikidata mapping data
mkdir -p data/db
wget -O data/db/label_en.db.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/label_en.db.zip
unzip data/db/label_en.db.zip -d data/db
wget -O data/db/alias_en.db.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/alias_en.db.zip
unzip data/db/alias_en.db.zip -d data/db
wget -O data/db/alias_rev_en.db.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/alias_rev_en.db.zip
unzip data/db/alias_rev_en.db.zip -d data/db
wget -O data/db/relation.db.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/relation.db.zip
unzip data/db/relation.db.zip -d data/db

# Download other data
mkdir -p data/other
wget -O data/other/relation_map.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/relation_map.json
wget -O data/other/enttypeid_mapper_en.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/enttypeid_mapper_en.json
wget -O data/other/template.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/template.json
wget -O data/other/all_schema.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/all_schema.json
wget -O data/other/biaozhu_en.json https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/biaozhu_en.json

# Download Model
mkdir -p model
wget -O model/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base.zip https://file.hankcs.com/hanlp/mtl/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base_20220608_003435.zip
unzip model/ud_ontonotes_tok_pos_lem_fea_ner_srl_dep_sdp_con_xlm_base.zip -d model
wget -O model/text_classification_en.zip https://huggingface.co/datasets/ghh001/InstructIE_tool/resolve/main/text_classification_en.zip
unzip model/text_classification_en.zip -d model

pip install -U huggingface_hub
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download --resume-download zjunlp/OneKE --local-dir model/OneKE
huggingface-cli download --resume-download MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 --local-dir model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
