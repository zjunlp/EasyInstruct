# KG2Instruction

# Use KG2Instruction to obtain annotation samples for any text

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


