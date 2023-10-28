import argparse
import json
from typing import Dict, Set, List
from tqdm import tqdm
from collections import defaultdict
from multiprocessing import JoinableQueue, Lock, Process
import logging
from sqlitedict import SqliteDict

from .util import format_wikilink, format_title, load_already, stable_hash

logger = logging.getLogger(__name__)


def generate_instances(q: JoinableQueue, FLAGS, already):
    with open(FLAGS.input, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            data = json.loads(line.strip())
            if data["title"] in already:
                logger.info(f"{data['title']} has exists!")
                continue
            q.put(data)


def add_tail(
    entity: List[str], tail_qids: Dict, relation_db: SqliteDict, alias_db: SqliteDict
) -> Dict[str, Set[str]]:
    """
    添加该实体对应的所有尾实体, 直觉是在文本中出现的实体其尾实体出现的概率更大
    """
    tail_qids[entity[0]].add(entity[1])
    try:
        ent_rels = relation_db[entity[1]]
    except:
        return tail_qids
    else:
        for rel, qid in ent_rels:
            if rel == "P1889":  # different from
                continue
            try:
                alias = alias_db[qid]
            except KeyError:
                continue
            else:
                for alia in alias:
                    tail_qids[alia].add(qid)
        return tail_qids


def get_tail_labels(
    iid: str, relation_db: SqliteDict, label_db: SqliteDict
) -> Set[str]:
    relations = relation_db[iid]
    tails = set()
    for _, tail_id in relations:
        try:
            tail_text = label_db[tail_id]
        except KeyError:
            pass
        else:
            tails.add(tail_text)
    return tails


def get_score_qid(total_entity: Set[str], tail_labels: Set[str]) -> int:
    """
    total_entity是整个文档中出现的实体text
    tail_labels是某一实体text对应的所有尾实体label
    tail_labels与total_entity的交集越多, 分数越大
    """
    score = 0
    for it in tail_labels:
        for iit in total_entity:
            if iit in it:
                score += 1
    return score


def match_qid(
    entity_list: List[List[List[str]]],
    label_db: SqliteDict,
    alias_db: SqliteDict,
    alias_rev_db: SqliteDict,
    relation_db: SqliteDict,
    language: str = "en",
) -> List[List[List[str]]]:
    # 1、先得到整个文档所有的实体(set), 相当于整个文档的信息
    total_entity = set()
    for entities in entity_list:
        for entity in entities:
            total_entity.add(format_wikilink(format_title(entity[0]), language))

    # 2、遍历所有entity, 开始消歧
    tail_qids = defaultdict(set)  # 截止当前匹配的实体及其尾实体,  直觉是在文本中出现的实体其尾实体出现的概率更大
    new_entity_list = []
    for entities in entity_list:
        new_entities = []
        for entity in entities:
            entity = list(entity)
            qids = None
            try:  # 是否直接在tail_qids中
                qids = tail_qids[format_wikilink(entity[0], language)]
            except KeyError:
                logger.debug("KeyError")
            else:
                if len(qids) == 1:  # 直接在tail_qids中，且无歧义，就是这个，不需要后续
                    entity[1] = list(qids)[0]
                    new_entities.append(entity)
                    tail_qids = add_tail(entity, tail_qids, relation_db, alias_db)
                    continue

            if len(qids) != 0:  # 从tail_ids中取的更精准些(搜索范围更小)
                alia_ids = qids
            else:
                try:
                    alia_ids = alias_rev_db[
                        format_wikilink(entity[0], language)
                    ]  # 根据text取出所有的qid
                    alia_ids = set(alia_ids)
                except KeyError:
                    entity[0] = format_title(entity[0])
                    alia_ids = set([entity[1]])

            if entity[1][0] != "Q":
                continue
            alia_ids.add(entity[1])

            if len(alia_ids) == 1:  # 仅有唯一的Qid, 直接就是该Qid
                entity[1] = list(alia_ids)[0]
                tail_qids = add_tail(entity, tail_qids, relation_db, alias_db)
            else:
                score_qids = []
                for iid in alia_ids:
                    try:
                        tail_labels = get_tail_labels(iid, relation_db, label_db)
                    except KeyError:  # 该iid没有关系对应的label，分数=-1
                        score = -1
                    else:  # 该iid有关系对应的label，计算分数
                        score = get_score_qid(total_entity, tail_labels)
                    score_qids.append([score, iid])

                score_qids = sorted(
                    score_qids, key=lambda x: x[0]
                )  # 排序匹配分数, 分数最大的qid是消歧后的entity id
                entity[1] = score_qids[-1][1]
                tail_qids = add_tail(entity, tail_qids, relation_db, alias_db)
                entity[0] = format_title(entity[0])

            new_entities.append(entity)
        new_entity_list.append(new_entities)

    return new_entity_list


def worker(q: JoinableQueue, writer, print_lock: Lock, FLAGS) -> None:
    relation_db = SqliteDict(FLAGS.relation_db, flag="r")
    alias_rev_db = SqliteDict(FLAGS.alias_rev_db, flag="r")
    alias_db = SqliteDict(FLAGS.alias_db, flag="r")
    label_db = SqliteDict(FLAGS.label_db, flag="r")

    while True:
        json_data = q.get()
        entity_list = match_qid(
            json_data["entity"],
            label_db,
            alias_db,
            alias_rev_db,
            relation_db,
            FLAGS.language,
        )
        print_lock.acquire()
        for text, entity in zip(json_data["text"], entity_list):
            data = {"id": stable_hash(text), "text": text, "entity": entity}
            writer.write(json.dumps(data, ensure_ascii=False) + "\n")
        print_lock.release()
        q.task_done()


def main(_):
    logger.info("Starting queue loader")
    if FLAGS.mode == "w":
        already = set()
    else:
        already = load_already(FLAGS.output)

    q = JoinableQueue(maxsize=256)
    l = Process(target=generate_instances, args=(q, FLAGS, already))
    l.start()
    print_lock = Lock()

    writer = open(FLAGS.output, FLAGS.mode, encoding="utf-8")
    for _ in range(FLAGS.j):
        p = Process(target=worker, args=(q, writer, print_lock, FLAGS))
        p.start()

    l.join()
    q.join()
    for _ in range(FLAGS.j):
        q.put(None)
    p.join()
    logger.info("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument("-j", type=int, default=1, help="Number of processors")
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("--relation_db", type=str, default="data/db/relation.db")
    parser.add_argument("--alias_rev_db", type=str, default="data/db/alias_rev.db")
    parser.add_argument("--alias_db", type=str, default="data/db/alias.db")
    parser.add_argument("--label_db", type=str, default="data/db/label.db")
    parser.add_argument("--mode", type=str, default="w")
    FLAGS, _ = parser.parse_known_args()

    main(_)
