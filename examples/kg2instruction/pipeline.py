import argparse
import logging
import json
from sqlitedict import SqliteDict
import hanlp
import torch
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from kglm.util import LOG_FORMAT, stable_hash, format_wikilink
from kglm.hanlp_ner import ner
from kglm.match_qid import match_qid
from kglm.find_rel import Annotator
from kglm.convert_enttype import process_entity
from cate_limit.relation_limit import schema_limit_data, get_all_schema_limit


from llm_cpl.build_instruction import build_instruction
from llm_cpl.inference import get_tokenizer_model, get_ie_llm_cpl, get_llm_sampling, get_ie_llm_cpl_vllm
from llm_cpl.extract import post_process4
from llm_cpl.direct_merge import merge_relations
from nli_filter.nli_filter import nli_filter_datas, load_nli_model_and_tokenizer

logger = logging.getLogger(__name__)


def main(_):
    label_db = SqliteDict(FLAGS.label_db, flag="r")    # label name to ids  
    alias_db = SqliteDict(FLAGS.alias_db, flag="r")    # alias name to ids
    alias_rev_db = SqliteDict(FLAGS.alias_rev_db, flag="r")   # id to alias names
    relation_db = SqliteDict(FLAGS.relation_db, flag="r")     # head_id&tail_id to relations
    if FLAGS.add_relation_value:
        relation_value_db = SqliteDict(FLAGS.relation_value_db, flag="r")    # head_id&tail_id to relations (value number)
    else:
        relation_value_db = None
    enttypeid_mapper = json.load(open(FLAGS.enttypeid_mapper, "r"))    # id to entity type
    HanLP = hanlp.load(FLAGS.ner_model, devices=FLAGS.device)          # NER model
    if FLAGS.language == "zh":
        time_quantity_other = ['时间', '度量', '其他']
        flags = {'time':'时间/时间', 'quantity':'度量/度量'}
        limit_flags = ['位于', '别名' , '其他', '可能']
    else:
        time_quantity_other = ['time', 'measure', 'other']
        flags = {'time':'time/time', 'quantity':'quantity/quantity'}
        limit_flags = ['located in', 'alternative name', 'other', 'possible']
    # topic mapper
    id2label_en = {0: 'Person', 1: 'Geographic Location', 2: 'Building', 3: 'Artificial Object', 4: 'Creature', 5: 'Astronomy', 6: 'Organization', 7: 'Natural Science', 8: 'Medicine', 9: 'Transport', 10: 'Event', 11: 'Works', 12: 'Other'}
    id2label_zh = {0: '人物', 1: '地理地区', 2: '建筑', 3: '人造物件', 4: '生物', 5: '天文对象', 6: '组织', 7: '自然科学', 8: '医学', 9: '运输', 10: '事件', 11: '作品', 12: '其他'}
    
    text_list = [FLAGS.input, ]
    if FLAGS.print_result:
        print('text list: ', text_list)

    # 1. NER
    # Return: List[List[List[str]]]
    hanlp_entities_list = ner(text_list, HanLP, FLAGS.language, FLAGS.chunk)
    if FLAGS.print_result:
        print('NER results: ', hanlp_entities_list)

    # 2. Find the corresponding wikidata ID from alias_rev_db
    # Return: List[List[List[str]]]
    new_entities_list = []
    for entities in hanlp_entities_list:
        new_entities = []
        for entity in entities:
            try:
                iids = alias_rev_db[format_wikilink(entity[0])]
            except KeyError:
                continue
            if len(iids) > 0:
                iids = iids[0]
                new_entities.append([entity[0], iids])
        new_entities_list.append(new_entities)
    if FLAGS.print_result:
        print('entity and id results: ', new_entities_list)

    # 3. Disambiguate entities, obtaining unique wikidata IDs for each entity
    # Return List[List[List[str]]]
    match_entities_list = match_qid(
        new_entities_list, label_db, alias_db, alias_rev_db, relation_db, FLAGS.language
    )
    if FLAGS.print_result:
        print('Disambiguate entities: ', match_entities_list)

    # 4. Matching relationships between entities
    # Return [{'text':List[str], 'entity':List[List[List[str]]], 'relation': List[List[Dict]]}]
    annotator = Annotator(
        alias_db,
        relation_db,
        relation_value_db,
        FLAGS.relation_map_path,
        FLAGS.language,
    )
    datas = []
    for text, entities in zip(text_list, match_entities_list):
        if len(entities) == 0:
            continue
        iid = stable_hash(text)
        relations, new_entities = annotator.annotate(entities, text, keep=True, flags=flags)
        print('matched relations:', relations)
        # 5. Assign entity types to entities
        entities_with_type = process_entity(new_entities, enttypeid_mapper, relation_db, time_quantity_other)
        print('entity with type', entities_with_type)
        data = {'id': iid, 'text': text, 'entity': entities_with_type, 'relation': relations}
        datas.append(data)

    # 6. Predicting Text Themes
    cls_tokenizer = AutoTokenizer.from_pretrained(FLAGS.cls_model)
    cls_model = AutoModelForSequenceClassification.from_pretrained(FLAGS.cls_model)
    texts = [data['text'] for data in datas]
    encoding = cls_tokenizer(texts, return_tensors='pt')
    labels = torch.tensor([1]).unsqueeze(0)  
    outputs = cls_model(**encoding, labels=labels)
    logits = outputs.logits
    preds = np.argmax(logits.detach().numpy(), axis=1)
    if FLAGS.language == "zh":
        topics = [id2label_zh[int(it)] for it in preds]
    else:
        topics = [id2label_en[int(it)] for it in preds]

    # 7. Execute schema constraint based filtering (filtering out schemas unrelated to the current text topic)
    for data, topic in zip(datas, topics):
        all_schema, convert_limit = get_all_schema_limit(FLAGS.schema_path, FLAGS.language)
        data['cate'] = topic
        if topic != '其他' and topic != 'Other':
            data = schema_limit_data(data, topic, all_schema, convert_limit, limit_flags)
        else:
            continue

    # 8. IE-LLM Completing Missing Triples
    schema_dict = {}
    template = json.load(open(FLAGS.template_path))[FLAGS.language]
    for key_cate, values2 in template.items():
        schema_list = list(values2.keys())
        schema_dict[key_cate] = schema_list

    if FLAGS.use_vllm:
        ie_tokenizer, llm, sampling_params = get_llm_sampling(FLAGS.model_name_or_path, FLAGS)
    else:
        ie_tokenizer, ie_model, device = get_tokenizer_model(FLAGS.ie_llm)
    for data in datas:
        instructions = build_instruction(FLAGS.language, schema_dict[data['cate']], data['text'])
        pred_list = []
        for ins in instructions:
            ins = json.dumps(ins, ensure_ascii=False)
            if FLAGS.use_vllm:
                llm_output = get_ie_llm_cpl_vllm(ins, ie_tokenizer, llm, sampling_params, FLAGS.prompt_name, device)
            else:
                llm_output = get_ie_llm_cpl(ins, ie_tokenizer, ie_model, device, FLAGS.prompt_name, FLAGS)
            pred_list.extend(post_process4(llm_output))
        merges = merge_relations(pred_list, data['relation'])
        data['relation'] = merges
    
    #9. NLI model filters unreal triplets
    tokenizer, nli_model, device = load_nli_model_and_tokenizer(FLAGS.nli_model, device)
    datas = nli_filter_datas(datas, FLAGS.batch_size, template, nli_model, tokenizer, device, FLAGS.nli_threshold)
    print('results: ', datas)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("--language", type=str, default="zh")
    parser.add_argument("--label_db", type=str, default="data/db/label_zh.db")
    parser.add_argument("--alias_db", type=str, default="data/db/alias_zh.db")
    parser.add_argument("--alias_rev_db", type=str, default="data/db/alias_rev_zh.db")
    parser.add_argument("--relation_db", type=str, default="data/db/relation.db")
    parser.add_argument("--relation_value_db", type=str, default="data/db/relation_value.db")
    parser.add_argument("--relation_map_path", type=str, default="data/other/relation_map.json")
    parser.add_argument('--enttypeid_mapper', type=str, default="data/other/enttype/enttypeid_mapper_zh.json")
    parser.add_argument('--template_path', type=str, default="data/other/template.json")
    parser.add_argument('--schema_path', type=str, default="data/schema/all_schema.json")

    parser.add_argument("--ner_model", type=str, default="model/close_tok_pos_ner_srl_dep_sdp_con_electra_base")
    parser.add_argument("--cls_model", type=str, default="model/text_classification_zh")
    parser.add_argument("--ie_llm", type=str, default="model/OneKE")
    parser.add_argument("--nli_model", type=str, default="model/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--chunk", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--add_relation_value", action="store_true")
    parser.add_argument("--use_vllm", action="store_true")
    parser.add_argument("--prompt_name", type=str, default="llama2_zh")
    parser.add_argument("--print_result", action="store_true")
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--max_new_tokens", type=int, default=256)
    parser.add_argument("--nli_threshold", type=float, default=0.5)

    FLAGS, _ = parser.parse_known_args()
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)
