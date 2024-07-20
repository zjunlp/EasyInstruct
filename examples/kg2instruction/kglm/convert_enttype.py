import os
import sys
sys.path.append("./")
from typing import List
import argparse
import json
import logging
from typing import Dict, Any
from sqlitedict import SqliteDict
from tqdm import tqdm

from kglm.util import load_already
logger = logging.getLogger(__name__) 



def generate_instances(input_file):
    with open(input_file, 'r', encoding="utf-8") as f:
        for line in tqdm(f):
            data = json.loads(line.strip())
            yield data


def get_label(qid, label_db):
    try:
        label = label_db[qid]
    except KeyError:
        return qid
    else:
        return label


def get_uppertype(qid, relation_db):
    try:
        relations = relation_db[qid]
    except KeyError:             # 该实体没有上层实体类型
        return None
    else:
        types = set()
        for rel, tail_id in relations:
            if rel == "P31" or rel == "P279":   # "instance of" or "subclass of
                types.add(tail_id)
        if len(types) == 0:      # 该实体没有上层实体类型
            return None
        return types
    

def convert_enttype(
        enttypeid: str, 
        enttypeid_mapper: Dict, 
        relation_db: SqliteDict, 
        time_quantity_other: Dict,
        max_depth=10, 
    ):
    rst = [time_quantity_other[2], time_quantity_other[2]]      # 默认为其他
    if enttypeid == 'time':          # 时间直接返回
        return [time_quantity_other[0], time_quantity_other[0]]
    elif enttypeid == 'quantity':    # 度量直接返回
        return [time_quantity_other[1], time_quantity_other[1]]
    
    if enttypeid in enttypeid_mapper:     # 存在于映射中, 可直接取两层实体类型
        rst = enttypeid_mapper[enttypeid][:-1]
    else:                                 # 不在, 就寻找上层实体类型
        cur = get_uppertype(enttypeid, relation_db)    # 获得该实体的所有上层实体类型 
        if cur is None:      # 该实体没有上层实体类型
            return rst

        i = 0
        flag = False
        while i < max_depth:       # 最多向上寻找max_depth层
            new_cur = set()
            for c in cur:       # 遍历该实体的所有上层实体类型
                if c in enttypeid_mapper:     # 存在于映射中, 可直接取两层实体类型
                    rst = enttypeid_mapper[c][:-1]
                    flag = True
                    break
                else:           # 不在, 就寻找所有上层实体类型 
                    tmp = get_uppertype(c, relation_db)
                    if tmp is None:     # 该实体没有上层实体类型
                        continue
                    else:
                        new_cur.update(tmp)                    
            cur = new_cur     # 更新
            i += 1
            if flag:
                break
    return rst


def flatten_tokens(tokens: List[List[str]]) -> List[str]:
    return [word for sent in tokens for word in sent]


def process_entity(entities, enttypeid_mapper, relation_db, time_quantity_other, enttype_db=None):
    entities_with_type = []
    for entity in entities:
        # 通过qid、enttypeid_mapper获得该实体的类型
        if enttype_db is not None and entity[0] in enttype_db:      # 是否已在enttype_db中, 在则复用
            ent_type = enttype_db[entity[0]]
        else:
            ent_type = "/".join(
                convert_enttype(
                    entity[1], 
                    enttypeid_mapper,  
                    relation_db, 
                    time_quantity_other
                    )
                )
            if enttype_db is not None:
                enttype_db[entity[0]] = ent_type
        entities_with_type.append([entity[0], entity[1], ent_type])
    return entities_with_type


def process_file(input_file, output_file, enttype_db, enttypeid_mapper, relation_db, time_quantity_other, FLAGS):
    if FLAGS.mode == 'w':
        already = set()
    else:
        already = load_already(output_file, "id")

    with open(output_file, 'w', encoding="utf-8") as writer:
        for json_data in generate_instances(input_file):
            if json_data["id"] in already:
                print(f"{json_data['id']} has exists!")
                continue
            entities = process_entity(json_data["entity"], enttypeid_mapper, relation_db, time_quantity_other, enttype_db)
            data = {"id":json_data["id"], "entity": entities}
            if FLAGS.keep:
                data['text'] = json_data['text']
            writer.write(json.dumps(data, ensure_ascii=False)+"\n")



def main(_):
    logger.info('Starting loader')
    relation_db = SqliteDict(FLAGS.relation_db, flag="r")
    if FLAGS.enttype_db != "":
        enttype_db = SqliteDict(FLAGS.enttype_db, autocommit=True)
    else:
        enttype_db = {}
    enttypeid_mapper = json.load(open(FLAGS.enttypeid_mapper, "r"))

    if FLAGS.language == "zh":
        time_quantity_other = ['时间', '度量', '其他']
        cate_list = ['人物', '地理地区', '建筑', '作品', '生物','人造物件', '自然科学', '组织', '运输', '事件', '天文对象', '医学']
    else:
        time_quantity_other = ['time', 'measure', 'other']
        cate_list = ['Person', 'Geographic_Location', 'Building', 'Works', 'Creature', 'Artificial_Object', 'Natural_Science', 'Organization', 'Transport', 'Event', 'Astronomy', 'Medicine']
    
    process_file(
        FLAGS.input, 
        FLAGS.output, 
        enttype_db, 
        enttypeid_mapper, 
        relation_db, 
        time_quantity_other,
        FLAGS
    )
    logger.info('Done')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('--mode', type=str, default="w")
    parser.add_argument('--language', type=str, default="en")
    parser.add_argument('--relation_db', type=str, default="data/db/relation.db")
    parser.add_argument('--enttype_db', type=str, default='')
    parser.add_argument('--keep', action='store_true')
    parser.add_argument('--enttypeid_mapper', type=str, default="data/other/enttype/enttypeid_mapper_zh.json")
    parser.add_argument('--cate_list', type=str, default='Person,Creature,Artificial_Object,Geographic_Location,Building,Natural_Science,Organization,Works,Transport,Event,Astronomy,Medicine')
    FLAGS, _ = parser.parse_known_args()
    
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger.info(f"{FLAGS}")

    main(_)

