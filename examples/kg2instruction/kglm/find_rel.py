import os
import sys
sys.path.append("./")
from typing import Any,  Dict, Tuple
import argparse
import json
import logging
from collections import defaultdict
from multiprocessing import JoinableQueue, Lock, Process
from tqdm import tqdm
from sqlitedict import SqliteDict

from kglm.render import render_quantity, render_time_zh, render_time_en
from kglm.util import load_already, format_wikilink
from kglm.convert_enttype import process_entity

logger = logging.getLogger(__name__) 


def clean_space(s):
    return s.replace(" ", "")


limit = {
    'P2053':['集水面积', 'quantity'],
    'P2044':['海拔', 'quantity'],
    'P2046':['面积', 'quantity'],
    'P2043':['长度', 'quantity'],
    'P2049':['宽度', 'quantity'],
    'P2048':['高度', 'quantity'],
    'P2386':['直径', 'quantity'],
    'P2047':['时长', 'quantity'],
    'P2067':['质量', 'quantity'],
    'P2052':['速度', 'quantity'],
    'P2262':['吃水深度', 'quantity'],
    'P1083':['最大容量', 'quantity'],
    'P1082':['人口', 'quantity'],
    'P1120':['死亡人数', 'quantity'],
    'P1538':['户数', 'quantity'],
    'P2196':['学生人数', 'quantity'],
    'P1128':['员工人数', 'quantity'],
    'P2295':['净利润', 'quantity'],
    'P3362':['营业收入', 'quantity'],
    'P2139':['营业额', 'quantity'],
    'P2403':['资产总值', 'quantity'],
    'P1831':['选民数', 'quantity'],
    'P2664':['销量', 'quantity'],
    'P2142':['票房', 'quantity'],
    'P281':['邮政编码', 'quantity'],
    'P2284':['价值', 'quantity'],

    'P569':['出生日期', 'time'],
    'P570':['死亡日期', 'time'],
    'P10786':['成立日期', 'time'],
    'P571':['成立或创建时间', 'time'],
    'P2669':['终止日期', 'time'],
    'P577':['出版日期', 'time'],
    'P2754':['拍摄日期', 'time'],
    'P2913':['描绘日期', 'time'],
    'P3999':['正式关闭日期', 'time'],   
    'P4602':['埋葬或火化日期', 'time'],
    'P585':['日期', 'time'],
    'P6949':['公告日期', 'time'],
    'P729':['服务起始日期', 'time'],
    'P730':['服务终止日期', 'time'],
    'P1191':['首演日期', 'time'],
    'P746':['消失日期', 'time'],
    'P7588':['生效日期', 'time'],
    'P7589':['批准日期', 'time'],
    'P10135':['录制日期', 'time'],
    'P10673':['出道日期', 'time'],
    'P580':['始于', 'time'],
    'P582':['终于', 'time'],
    'P576':['解散、废除或拆毁日', 'time'],
    'P575':['发现或发明时间', 'time'],

    'P1619':['正式开放日期', 'time'],
    'P1390':['比赛时间', 'time'],
    'P8556':['灭绝日期', 'time'],
    'P606':['首航日期', 'time'],
    'P5204':['商品化日期', 'time'],
    'P2781':['竞赛时间', 'time'],
    'P1636':['洗礼日期', 'time'],
    'P1734':['就职誓言日期', 'time'],
    'P1249':['最早文献记录时间', 'time'],
    'P1319':['最早日期', 'time'],
    'P1326':['最晚日期', 'time'],
}

limit_string1 = {
    'P1448': ['官方名称'], 
    'P1449': ['昵称'], 
    'P1477': ['出生姓名'], 
    'P1559': ['母语人名'], 
    'P1782': ['表字'], 
    'P1785': ['庙号'], 
    'P1786': ['谥号'], 
    'P1787': ['号'], 
    'P1813': ['简称'], 
    'P1814': ['日语假名'], 
    'P1843': ['生物俗名'], 
    'P1845': ['反病毒别名'], 
    'P2093': ['作者姓名字符串'], 
    'P223': ['星系类型'], 
    'P225': ['学名'], 
    'P2561': ['名称'], 
    'P4970': ['又名']
}

limit_string2 = {
    'P229': ['IATA航空公司代码'], 
    'P230': ['ICAO航空公司代码'], 
    'P246': ['元素符号'], 
    'P274': ['化学式'], 
    'P296': ['车站编号'], 
}



class Annotator:
    def __init__(self, alias_db, relation_db, relation_value_db, relation_map_path, language) -> None:
        self._relation_db = relation_db
        self._relation_value_db = relation_value_db
        self._alas_db = alias_db

        relation_map = {}
        with open(relation_map_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line.strip())
                if language == "zh":
                    relation_map[record["id"]] = record["label-zh"]
                else:
                    relation_map[record["id"]] = record["label"]
        self._relation_mapper = relation_map

        if language == "zh":
            self._render_time = render_time_zh
        else:
            self._render_time = render_time_en
        self._render_quantity = render_quantity

        self._relation = dict()  # head entity ID + tail entity ID: relationship
        

    def get_reltext(self, relation):
        if ":" in relation:
            rel = relation.split(":")
            rel_label1 = self._relation_mapper.get(rel[0], rel[0])
            rel_label2 = self._relation_mapper.get(rel[-1], rel[-1])
            return rel_label1 + rel_label2
        rel_label = self._relation_mapper.get(relation, relation)
        return rel_label


    def add_relation(self, iid):
        # Add all relationships for entity iid
        try:
            relations = self._relation_db[iid]
        except KeyError:
            pass
        else:
            for rel, tail_id in relations:
                if iid+tail_id not in self._relation:
                    self._relation[iid+tail_id] = set()
                self._relation[iid+tail_id].add(rel)


    def add_relation_value(self, entity, text):
        text = clean_space(text)
        relation_values = []
        enityt_values = []
        try:
            relations = self._relation_value_db[entity[1]]
        except KeyError:
            return [], []
        else:
            candidate_relations = defaultdict(set)
            for rel, it in relations:
                if it[0] == 'time' and rel in limit and limit[rel][1] == 'time':
                    times = self._render_time(it[1], it[2])
                    times = sorted(times, key=lambda x:len(x), reverse=True)    # Sort by string length, match from long to short, avoiding matching to substrings
                    for time in times:
                        if clean_space(time) in text:
                            candidate_relations[rel].add((time, 'time'))   # Each relationship may have multiple values
                            break
                elif it[0] == 'quantity' and rel in limit and limit[rel][1] == 'quantity':
                    quantities = self._render_quantity(it[1], it[2], self._alas_db)
                    quantities = sorted(quantities, key=lambda x:len(x), reverse=True)
                    for quantity in quantities:
                        if clean_space(quantity) in text:
                            candidate_relations[rel].add((quantity, 'quantity'))
                            break
            
            for rel, values in candidate_relations.items():
                if (entity[0], rel) in self._relation_value_unique:
                    continue
                sorted_values = sorted(values, key=lambda x:len(x[1]), reverse=True)   # Take the longest value corresponding to each relationship
                relation = {"head":entity[0], "relation":self.get_reltext(rel), "tail":sorted_values[0][0]}
                self._relation_value_unique.add((entity[1], rel))
                relation_values.append(relation)
                enityt_values.append(list(sorted_values[0]))
        return relation_values, enityt_values


    def add_relation_string(self, entity, text):
        text = clean_space(text)
        relation_values = []
        enityt_values = []
        try:
            relations = self._relation_string_db[entity[1]]
        except KeyError:
            return [], []
        else:
            candidate_relations = defaultdict(set)
            format_text = format_wikilink(text)
            for rel, it in relations:
                if format_wikilink(it) in format_text:
                    candidate_relations[rel].add(it)
                    break
        
            for rel, values in candidate_relations.items():
                if (entity[1], rel) in self._relation_string_unique:
                    continue
                sorted_values = sorted(values, key=lambda x:len(x), reverse=True)   # Take the longest value corresponding to each relationship
                if rel in limit_string2:
                    tail_type = 'quantity'
                else:
                    tail_type = 'self'
                if entity[0] == sorted_values[0]:
                    continue
                relation = {"head":entity[0], "relation":self.get_reltext(rel), "tail":sorted_values[0]}
                self._relation_value_unique.add((entity[1], rel))
                relation_values.append(relation)
                enityt_values.append([sorted_values[0], tail_type])
        return relation_values, enityt_values


    def annotate_only_value(self, entities, text) -> Dict[str, Any]:
        self._relation = dict()
        self._relation_value_unique = set()  # Ensure that for the relation_value type, (head id, rel id) only appears once
        self._relation_string_unique = set()  

        relations = []
        new_entities = []
        for i in range(len(entities)):
            if entities[i][1][0] != "Q":
                continue
            relation_values, enityt_values = self.add_relation_value(entities[i], text)
            if len(relation_values) > 0:
                relations.extend(relation_values)
                new_entities.extend(enityt_values)
        return relations, new_entities

                    
    def annotate(self, entities, text, keep, flags) -> Dict[str, Any]:
        self._relation = dict()
        self._relation_value_unique = set()  # 确保对于relation_value类型, (head id, rel id)只出现一次

        relations = []
        new_entities = entities.copy()
        # 遍历所有的Qid, 添加所有关系到self._relation中(头实体+尾实体:关系s)
        for i in range(len(entities)):
            if entities[i][1][0] != "Q":
                continue
            self.add_relation(entities[i][1])

        # 双重遍历, 匹配每一对头、尾实体, 从self._relation中取出对应的关系
        only_once = set()   # 确保(head, rel_type, tail)只出现一次
        for i in range(len(entities)):
            if entities[i][1][0] != "Q":
                continue
            for j in range(i+1, len(entities)):
                if entities[j][1][0] != "Q":
                    continue
                rels = set()
                head, tail = "", ""
                try:
                    rels = self._relation[entities[i][1]+entities[j][1]]
                    head = entities[i][0]
                    tail = entities[j][0]
                except KeyError:
                    logger.debug("KeyError")
                if len(rels) == 0:
                    try: 
                        rels = self._relation[entities[j][1]+entities[i][1]]
                        head = entities[j][0]
                        tail = entities[i][0]
                    except KeyError:
                        continue
                if len(rels) == 0 or head == "" or tail == "":
                    continue
                for rel in rels:  
                    rel_type = self.get_reltext(rel)
                    if  (head, rel_type, tail) in only_once:
                        continue                
                    relations.append({"head":head, "relation":rel_type, "tail":tail})
                    only_once.add((head, rel_type, tail))
            relation_values, entity_values = self.add_relation_value(entities[i], text)
            if len(relation_values) > 0:
                relations.extend(relation_values)
                if keep:
                    entity_values = [[it[0], it[1], flags[it[1]]] for it in entity_values]
                new_entities.extend(entity_values)
        return relations, new_entities



def process_file(input_file, output_file, alias_db, relation_db, relation_value_db, enttypeid_mapper, flags, time_quantity_other, FLAGS):
    if FLAGS.mode == 'w':
        already = set()
    else:
        already = load_already(output_file, "id")

    annotator = Annotator(
        alias_db, 
        relation_db, 
        relation_value_db, 
        FLAGS.relation_map_path, 
        FLAGS.language
    )

    writer = open(output_file, "w", encoding="utf-8")
    with open(input_file, 'r', encoding="utf-8") as f:
        for line in tqdm(f):
            json_data = json.loads(line)
            if json_data["id"] in already:
                print(f"{json_data['id']} has exists!")
                continue
            relations, new_entities = annotator.annotate(json_data['entity'], json_data['text'], FLAGS.keep, flags)
            entities = process_entity(new_entities, enttypeid_mapper, relation_db, time_quantity_other)
            if len(relations) == 0:
                continue
            annotation = {"id":json_data["id"], "text": json_data["text"], "entity":entities, "relation":relations}
            writer.write(json.dumps(annotation, ensure_ascii=False)+'\n')
    writer.close()


def main(_): 
    if FLAGS.language == "zh":
        flags = {'time':'时间/时间', 'quantity':'度量/度量'}
        time_quantity_other = ['时间', '度量', '其他']
        cate_list = ['人物', '地理地区', '建筑', '作品', '生物','人造物件', '自然科学', '组织', '运输', '事件', '天文对象', '医学']
    else:
        flags = {'time':'time/time', 'quantity':'quantity/quantity'}
        time_quantity_other = ['time', 'measure', 'other']
        cate_list = ['Person', 'Geographic_Location', 'Building', 'Works', 'Creature', 'Artificial_Object', 'Natural_Science', 'Organization', 'Transport', 'Event', 'Astronomy', 'Medicine']
    
    
    cate_list = FLAGS.cate_list.split(',')
    logger.info('Starting queue loader')
    relation_db = SqliteDict(FLAGS.relation_db, flag='r')
    relation_value_db = SqliteDict(FLAGS.relation_value_db, flag='r')
    alias_db = SqliteDict(FLAGS.alias_db, flag='r')  
    enttypeid_mapper = json.load(open(FLAGS.enttypeid_mapper, "r")) 

    if os.path.isfile(FLAGS.input):
        process_file(
            FLAGS.input, 
            FLAGS.output, 
            alias_db, 
            relation_db, 
            relation_value_db,
            enttypeid_mapper,
            flags,
            time_quantity_other,
            FLAGS
        )
    else:
        for cate in cate_list:
            print(cate)
            os.makedirs(os.path.join(FLAGS.output, cate), exist_ok=True)
            for fl in sorted(os.listdir(os.path.join(FLAGS.input, cate))):
                print(fl)
                process_file(
                    os.path.join(FLAGS.input, cate, fl), 
                    os.path.join(FLAGS.output, cate, fl), 
                    alias_db, 
                    relation_db, 
                    relation_value_db,
                    enttypeid_mapper,
                    flags,
                    time_quantity_other,
                    FLAGS
                )
    logger.info('Done')
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('-j', type=int, default=4, help='Number of processors')
    parser.add_argument('--language', type=str, default='en')
    parser.add_argument('--mode', type=str, default="w")
    parser.add_argument('--relation_db', type=str, default='data/db/relation.db')
    parser.add_argument('--relation_value_db', type=str, default='data/db/relation_value.db')
    parser.add_argument('--alias_db', type=str, default='data/db/alias.db')
    parser.add_argument('--relation_map_path', type=str, default="data/other/relation_map.json")
    parser.add_argument('--enttypeid_mapper', type=str, default="data/other/enttypeid_mapper_zh.json")
    parser.add_argument('--cate_list', type=str, default='Person,Creature,Artificial_Object,Geographic_Location,Building,Natural_Science,Organization,Works,Transport,Event,Astronomy,Medicine')
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger.info(f"{FLAGS}")

    main(_)
    