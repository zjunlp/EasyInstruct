import json 
import os
import sys
import json
import logging
import argparse
from tqdm import tqdm
sys.path.append("./")
from collections import defaultdict
from cate_limit.all_schema import all_schema_dict_zh, all_schema_dict_en
from cate_limit.utils import read_from_json, write_to_json, match_sublist
logger = logging.getLogger(__name__) 


zh_enttype = ['人物', '地理地区', '事件', '组织', '生物', '产品', '医学', '运输', '建筑结构', '时间', '天文对象类型', '专业', '度量', '其他', '度量1']
en_enttype = ['human', 'geographic_region', 'event', 'organization', 'organism', 'product', 'medicine', 'transport', 'architectural_structure', 'time', 'astronomical_object_type', 'profession', 'measure', 'other', 'measure1']
zh2en_enttype = dict(zip(zh_enttype, en_enttype))



def load_all_cate_schema(schema_path, language):
    all_schema = json.load(open(schema_path, 'r'))[language]
    return all_schema


def create_alias_remove(data, cate_schema, alias_name='alternative name'):
    '''
    去除别名, 并将别名作为三元组加入
    '''
    alias = defaultdict(set)     # {'qid': ['text', 'offset']]}  同一个qid可以有多个text, 用最早出现的text作为主text, 其他的text作为别名
    text2type = {}               # {ent_text: type}, 后面获得头、尾实体的实体类型用得到
    for ent in data['entity']:
        text2type[ent[0]] = ent[2]
        offset = match_sublist(list(data['text']), list(ent[0]))
        if len(offset) == 0:
            continue
        offset = offset[0]
        if ent[1] == 'time' or ent[1] == 'quantity':     # time 和 quantity 不需要别名替换
            alias[ent[0]].add((ent[0], offset))
            continue
        alias[ent[1]].add((ent[0], offset))
        
    remain_ent_text = set()
    rels_set = set()
    new_rels = []
    alias2text = {}   # {别名 : 主名}
    for _, alias_set in alias.items():
        alias_list = list(alias_set)
        alias_list = sorted(alias_list, key=lambda x: x[1])     # 按text在句子中首次出现的位置排序
        remain_ent_text.add(alias_list[0][0])                   # 只保留最早出现的text
        alias2text[alias_list[0][0]] = alias_list[0][0]
        for i in range(1, len(alias_list)):
            alias2text[alias_list[i][0]] = alias_list[0][0]
            rel = [alias_list[0][0], text2type[alias_list[0][0]], alias_name, alias_list[i][0], text2type[alias_list[i][0]]]
            new_rels.append(rel)
            rels_set.add((rel[0], rel[2], rel[3]))


    for rel in data['relation']:
        if rel['relation'] not in cate_schema:
            continue
        if rel['head'] not in remain_ent_text:     # 别名的三元组全部抛弃, 可以的, 因为qid与主名一样
            continue
        if rel['tail'] not in remain_ent_text:     # 别名作为尾实体, 改成主名作尾实体
            try:
                rel['tail'] = alias2text.get(rel['tail'], rel['tail'])
                rel['head'] = alias2text.get(rel['head'], rel['head'])
            except KeyError:
                print("KeyError", rel)
                continue

        if cate_schema[rel['relation']]['reverse'] == "1":
            rel = [rel['tail'], text2type[rel['tail']], rel['relation'], rel['head'], text2type[rel['head']]]    # 头实体、头实体类型、关系、尾实体、尾实体类型
        else:
            rel = [rel['head'], text2type[rel['head']], rel['relation'], rel['tail'], text2type[rel['tail']]]
        if (rel[0], rel[2], rel[3]) not in rels_set:
            new_rels.append(rel)
        rels_set.add((rel[0], rel[2], rel[3]))

    return new_rels



def get_parent_rel(rel, cate_schema, other='other', possible='possible'):
    try:
        parent_rel = cate_schema[rel]['parent']
    except KeyError:
        return other
    if parent_rel == possible:
        return rel
    return parent_rel



def apply_limit(rels, cate_schema, convert_limit, other='other', possible='possible'):
    '''
    应用schema约束, 每个关系的头、尾实体类型必须在schema中的限制范围内
    '''
    new_rels = set()
    for rel in rels:
        parent_rel = get_parent_rel(rel[2], cate_schema, other, possible)
        head_type = rel[1].split('/')[0]
        tail_type = rel[4].split('/')[0]

        if parent_rel == other:
            continue
        try:
            reltype_limit = convert_limit[parent_rel]
        except KeyError:
            new_rels.add((rel[0], parent_rel, rel[3]))
            continue
        if len(reltype_limit[0]) != 0 and head_type not in reltype_limit[0]:
            continue
        if len(reltype_limit[1]) != 0 and tail_type not in reltype_limit[1]:
            continue
        new_rels.add((rel[0], parent_rel, rel[3]))

    return list(list(it) for it in new_rels)


def transitive_reduction(graph):
    result_graph = {node: set(neighbors) for node, neighbors in graph.items()}
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if neighbor in result_graph:
                targets_to_remove = set()
                for target in result_graph[neighbor]:
                    if target != node and target in result_graph[node]:
                        targets_to_remove.add(target)
                result_graph[node] -= targets_to_remove
    return result_graph


def located_reduction(rels, located='located in'):
    new_rels = []
    located_rel = defaultdict(set)
    for rel in rels:
        if rel[1] == located:
            located_rel[rel[0]].add(rel[2])
        else:
            new_rels.append({'head':rel[0], 'relation':rel[1], 'tail':rel[2]})
    if len(located_rel) == 0:
        return new_rels
    
    transitive_located_rel = transitive_reduction(located_rel)
    for head, tails in transitive_located_rel.items():
        for tail in tails:
            new_rels.append({'head':head, 'relation':located, 'tail':tail})
    return new_rels


def unique_ents(ents):
    new_ents = []
    already = set()
    for it in ents:
        if (it[0], it[1]) not in already:
            new_ents.append(it)
            already.add((it[0], it[1]))
    return new_ents


def get_all_schema_limit(schema_path, language):
    all_schema = load_all_cate_schema(schema_path, language)
    convert_limit = {}
    if language == "zh":
        for cate, values in all_schema_dict_zh.items():
            convert_limit[cate] = {}
            limit = values[2]
            for rel, value in limit.items():
                convert_limit[cate][rel[1]] = value
    else:
        for cate, values in all_schema_dict_en.items():
            convert_limit[cate] = {}
            limit = values[2]
            for rel, value in limit.items():
                convert_limit[cate][rel[0]] = [[zh2en_enttype[it] for it in value[0]], [zh2en_enttype[it] for it in value[1]]]
    return all_schema, convert_limit


def schema_limit_data(data, cate, all_schema, convert_limit, flags):
    # 1、同一个qid可以有多个text, 用最早出现的text作为主text, 其他的text作为别名
    new_rels = create_alias_remove(data, all_schema[cate], alias_name=flags[1])
    # 2、应用schema约束
    new_rels = apply_limit(new_rels, all_schema[cate], convert_limit[cate], other=flags[2], possible=flags[3])
    new_rels = located_reduction(new_rels, located=flags[0])
    new_ents = unique_ents(data['entity'])
    data['entity'] = new_ents
    data['relation'] = new_rels
    data['cate'] = cate
    return data


def process_file(language, schema_path, src_path, tgt_path, cate, flags):
    all_schema, convert_limit = get_all_schema_limit(schema_path, language)
    datas = read_from_json(src_path)
    new_datas = []
    for data in tqdm(datas):
        data = schema_limit_data(data, cate, all_schema, convert_limit, flags)
        new_datas.append(data)
    write_to_json(tgt_path, new_datas)


def main(FLAGS):
    if FLAGS.language == "zh":
        flags = ['位于', '别名' , '其他', '可能']
    else:
        flags = ['located in', 'alternative name', 'other', 'possible']
    process_file(FLAGS.language, FLAGS.schema_path, FLAGS.input, FLAGS.output, FLAGS.cate, flags)


    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('--language', type=str, default="en")
    parser.add_argument('--schema_path', type=str, default="data/schema/all_schema.json")
    parser.add_argument('--cate', type=str, default="Person")
    parser.add_argument('--cate_list', type=str, default="Person,Geographic_Location,Building,Works,Creature,Artificial_Object,Natural_Science,Organization,Transport,Event,Astronomy,Medicine")
    FLAGS, _ = parser.parse_known_args()
    
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger.info(f"{FLAGS}")

    main(FLAGS)