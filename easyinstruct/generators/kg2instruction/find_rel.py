from typing import Any, Dict, Tuple
import argparse
import json
import logging
from collections import defaultdict
from multiprocessing import JoinableQueue, Lock, Process
from tqdm import tqdm
from sqlitedict import SqliteDict

from .render import render_quantity, render_time_zh, render_time_en
from .util import load_already

logger = logging.getLogger(__name__)


def clean_space(s):
    return s.replace(" ", "")


limit = {
    "P2053": ["集水面积", "quantity"],
    "P2044": ["海拔", "quantity"],
    "P2046": ["面积", "quantity"],
    "P2043": ["长度", "quantity"],
    "P2049": ["宽度", "quantity"],
    "P2048": ["高度", "quantity"],
    "P2386": ["直径", "quantity"],
    "P2047": ["时长", "quantity"],
    "P2067": ["质量", "quantity"],
    "P2052": ["速度", "quantity"],
    "P2262": ["吃水深度", "quantity"],
    "P1083": ["最大容量", "quantity"],
    "P1082": ["人口", "quantity"],
    "P1120": ["死亡人数", "quantity"],
    "P1538": ["户数", "quantity"],
    "P2196": ["学生人数", "quantity"],
    "P1128": ["员工人数", "quantity"],
    "P2295": ["净利润", "quantity"],
    "P3362": ["营业收入", "quantity"],
    "P2139": ["营业额", "quantity"],
    "P2403": ["资产总值", "quantity"],
    "P1831": ["选民数", "quantity"],
    "P2664": ["销量", "quantity"],
    "P2142": ["票房", "quantity"],
    "P281": ["邮政编码", "quantity"],
    "P2284": ["价值", "quantity"],
    "P569": ["出生日期", "time"],
    "P570": ["死亡日期", "time"],
    "P10786": ["成立日期", "time"],
    "P571": ["成立或创建时间", "time"],
    "P2669": ["终止日期", "time"],
    "P577": ["出版日期", "time"],
    "P2754": ["拍摄日期", "time"],
    "P2913": ["描绘日期", "time"],
    "P3999": ["正式关闭日期", "time"],
    "P4602": ["埋葬或火化日期", "time"],
    "P585": ["日期", "time"],
    "P6949": ["公告日期", "time"],
    "P729": ["服务起始日期", "time"],
    "P730": ["服务终止日期", "time"],
    "P1191": ["首演日期", "time"],
    "P746": ["消失日期", "time"],
    "P7588": ["生效日期", "time"],
    "P7589": ["批准日期", "time"],
    "P10135": ["录制日期", "time"],
    "P10673": ["出道日期", "time"],
    "P580": ["始于", "time"],
    "P582": ["终于", "time"],
    "P576": ["解散、废除或拆毁日", "time"],
    "P575": ["发现或发明时间", "time"],
}


class Annotator:
    def __init__(
        self,
        alias_db,
        relation_db,
        relation_value_db,
        relation_map_path,
        language,
        add_relation_value=False,
    ) -> None:
        self._relation_db = relation_db
        self._relation_value_db = relation_value_db
        self._alas_db = alias_db
        self._add_relation_value = add_relation_value

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

    def get_reltext(self, relation):
        if ":" in relation:
            rel = relation.split(":")
            rel_label = self._relation_mapper.get(rel[-1], rel[-1])
            return rel_label
        rel_label = self._relation_mapper.get(relation, relation)
        return rel_label

    def add_relation(self, iid):
        # 为实体iid添加所有的关系
        try:
            relations = self._relation_db[iid]
        except KeyError:
            pass
        else:
            for rel, tail_id in relations:
                if iid + tail_id not in self._relation:
                    self._relation[iid + tail_id] = set()
                self._relation[iid + tail_id].add(rel)

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
                if it[0] == "time" and rel in limit and limit[rel][1] == "time":
                    times = self._render_time(it[1], it[2])
                    times = sorted(
                        times, key=lambda x: len(x), reverse=True
                    )  # 按字符串长度排序, 从长到短匹配, 避免匹配到子串
                    for time in times:
                        if clean_space(time) in text:
                            candidate_relations[rel].add((time, "time"))  # 每种关系可能有多个值
                            break
                elif (
                    it[0] == "quantity" and rel in limit and limit[rel][1] == "quantity"
                ):
                    quantities = self._render_quantity(it[1], it[2], self._alas_db)
                    quantities = sorted(quantities, key=lambda x: len(x), reverse=True)
                    for quantity in quantities:
                        if clean_space(quantity) in text:
                            candidate_relations[rel].add((quantity, "quantity"))
                            break

            for rel, values in candidate_relations.items():
                if (entity[1], rel) in self._relation_value_unique:
                    continue
                sorted_values = sorted(
                    values, key=lambda x: len(x[1]), reverse=True
                )  # 每种关系对应的值, 取最长的
                relation = {
                    "head": entity[0],
                    "relation": self.get_reltext(rel),
                    "tail": sorted_values[0][0],
                }
                self._relation_value_unique.add((entity[1], rel))
                relation_values.append(relation)
                enityt_values.append(list(sorted_values[0]))
        return relation_values, enityt_values

    def annotate(self, entities, text) -> Dict[str, Any]:
        self._relation = dict()  # 头实体id+尾实体id : 关系
        self._relation_value_unique = (
            set()
        )  # 确保对于relation_value类型, (head id, rel id)只出现一次

        relations = []
        new_entities = entities.copy()
        # 遍历所有的Qid, 添加所有关系到self._relation中(头实体+尾实体:关系s)
        for i in range(len(entities)):
            if entities[i][1][0] != "Q":
                continue
            self.add_relation(entities[i][1])

        # 双重遍历, 匹配每一对头、尾实体, 从self._relation中取出对应的关系
        only_once = set()  # 确保(head, rel_type, tail)只出现一次
        for i in range(len(entities)):
            if entities[i][1][0] != "Q":
                continue
            for j in range(i + 1, len(entities)):
                if entities[j][1][0] != "Q":
                    continue
                rels = set()
                head, tail = "", ""
                try:
                    rels = self._relation[entities[i][1] + entities[j][1]]
                    head = entities[i][0]
                    tail = entities[j][0]
                except KeyError:
                    logger.debug("KeyError")
                if len(rels) == 0:
                    try:
                        rels = self._relation[entities[j][1] + entities[i][1]]
                        head = entities[j][0]
                        tail = entities[i][0]
                    except KeyError:
                        continue
                if len(rels) == 0 or head == "" or tail == "":
                    continue
                for rel in rels:
                    rel_type = self.get_reltext(rel)
                    if (head, rel_type, tail) in only_once:
                        continue
                    relations.append({"head": head, "relation": rel_type, "tail": tail})
                    only_once.add((head, rel_type, tail))

            if self._add_relation_value:
                relation_values, enityt_values = self.add_relation_value(
                    entities[i], text
                )
                if len(relation_values) > 0:
                    relations.extend(relation_values)
                    new_entities.extend(enityt_values)

        return relations, new_entities


def loader(q: JoinableQueue, FLAGS: Tuple[Any], already) -> None:
    with open(FLAGS.input, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            data = json.loads(line.strip())
            if data["id"] in already:
                print(f"{data['id']} has exists!")
                continue
            q.put(data)


def worker(
    q: JoinableQueue, i: int, writer, print_lock: Lock, FLAGS: Tuple[Any]
) -> None:
    relation_db = SqliteDict(FLAGS.relation_db, flag="r")
    if FLAGS.add_relation_value:
        relation_value_db = SqliteDict(FLAGS.relation_value_db, flag="r")
    else:
        relation_value_db = None
    alias_db = SqliteDict(FLAGS.alias_db, flag="r")

    annotator = Annotator(
        alias_db,
        relation_db,
        relation_value_db,
        FLAGS.relation_map_path,
        FLAGS.language,
        FLAGS.add_relation_value,
    )

    while True:
        json_data = q.get()
        relations, new_entities = annotator.annotate(
            json_data["entity"], json_data["text"]
        )
        if len(relations) == 0:
            continue
        annotation = {
            "id": json_data["id"],
            "entity": new_entities,
            "relation": relations,
        }
        print_lock.acquire()
        writer.write(json.dumps(annotation, ensure_ascii=False) + "\n")
        print_lock.release()
        q.task_done()


def main(_):
    logger.info("Starting queue loader")
    if FLAGS.mode == "w":
        already = set()
    else:
        already = load_already(FLAGS.output, "id")
    q = JoinableQueue(maxsize=256)
    l = Process(target=loader, args=(q, FLAGS, already))
    l.start()

    logger.info("Launching worker processes")
    print_lock = Lock()
    writer = open(FLAGS.output, "w", encoding="utf-8")
    processes = [
        Process(target=worker, args=(q, i, writer, print_lock, FLAGS))
        for i in range(FLAGS.j)
    ]
    for p in processes:
        p.start()

    l.join()
    q.join()
    for _ in range(FLAGS.j):
        q.put(None)
    for p in processes:
        p.join()
    logger.info("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument("-j", type=int, default=4, help="Number of processors")
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("--mode", type=str, default="w")
    parser.add_argument("--relation_db", type=str, default="data/db/relation.db")
    parser.add_argument(
        "--relation_value_db", type=str, default="data/db/relation_value.db"
    )
    parser.add_argument("--alias_db", type=str, default="data/db/alias.db")
    parser.add_argument(
        "--relation_map_path", type=str, default="data/other/relation_map.json"
    )
    parser.add_argument("--add_relation_value", action="store_true")
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info(f"{FLAGS}")

    main(_)
