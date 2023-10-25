import argparse
from typing import Dict, List, Set
import json
from tqdm import tqdm
import logging
from sqlitedict import SqliteDict
from multiprocessing import JoinableQueue, Lock, Process

from .util import (
    add_space,
    remove_space,
    containEnglish,
    clean_u200b,
    format_wikilink,
    load_already,
)

logger = logging.getLogger(__name__)

BAD = [
    "CARDINAL",
    "ORDINAL",
    "TIME",
    "LANGUAGE",
    "DATE",
    "MONEY",
    "QUANTITY",
    "PERCENT",
    "LANGUAGE",
]


def generate_instances(q: JoinableQueue, FLAGS, already):
    """Generates instances from an input JSON-lines file"""
    with open(FLAGS.wikiinput, "r", encoding="utf-8") as f1:
        with open(FLAGS.hanlpinput, "r", encoding="utf-8") as f2:
            for line1, line2 in tqdm(zip(f1, f2)):
                try:
                    data1 = json.loads(line1)
                    if data1["title"] in already:
                        print(f"{data1['title']} has exists!")
                        continue
                    data2 = json.loads(line2)
                    assert data1["title"] == data2["title"], print(
                        f"{data1['title']} != {data2['title']}"
                    )
                    data = {"data1": data1, "data2": data2}
                    q.put(data)
                except KeyError:
                    continue


def keep(
    ners1: List[List[str]], ner2: List[str], alias_rev_db, language: str = "en"
) -> str:
    if ner2[1] in BAD:
        return None
    # 看实体是否在alias_rev中, 在才保留
    try:
        iids = alias_rev_db[format_wikilink(ner2[0], language)]
    except KeyError:
        return None
    if len(iids) > 0:
        iids = iids[0]
    else:
        return None
    for ner1 in ners1:
        # ner2存在ner1中或ner1存在ner2中都不保留
        if ner2[0] in ner1[0] or ner1[0] in ner2[0]:
            return None
    return iids


def merge_ner(
    sner1: List[List[str]],
    sner2: List[List[str]],
    alias_rev_db: SqliteDict,
    language: str = "en",
) -> Set:
    ners1 = set(tuple(s) for s in sner1)
    for ner2 in sner2:
        iid = keep(ners1, ner2, alias_rev_db, language)
        if iid is not None:
            ners1.add((ner2[0], iid))
    return ners1


def merge_ner_list(
    ner_list1: List[List[List[str]]],
    ner_list2: List[List[List[str]]],
    alias_rev_db: SqliteDict,
    language: str = "en",
) -> Dict:
    if len(ner_list2) == 0:
        return ner_list1
    new_ner_list = []
    for ners2, ners1 in zip(ner_list2, ner_list1):
        ners = merge_ner(ners1, ners2, alias_rev_db, language)
        new_ner_list.append(ners)
    return new_ner_list


def remove_u200b(ner_list: List[List[List[str]]]) -> List[Set]:
    new_ner_list = []
    for ners in ner_list:
        new_ners = set()
        for ner in ners:
            new_ners.add((clean_u200b(ner[0]), ner[1]))
        new_ner_list.append(new_ners)
    return new_ner_list


def match_sublist(the_list: List[str], to_match: List[str]) -> List:
    len_to_match = len(to_match)
    matched_list = list()
    for index in range(len(the_list) - len_to_match + 1):
        if to_match == the_list[index : index + len_to_match]:
            matched_list += [(index, index + len_to_match)]
    return matched_list


def get_offset(
    token_list: List[List[str]], entity_list: List[List[List[str]]], language: str
):
    tentity_list = []
    for tokens, entities in zip(token_list, entity_list):
        tentities = []
        for entity, entity_type in entities:
            if len(entity) == 0:
                continue
            if language == "zh":
                if containEnglish(entity):
                    entity_token = add_space(tokens, entity.replace(" ", ""))
                    if type(entity_token) == list:
                        entity = "".join(entity_token).strip()
                    else:
                        entity = entity_token
                else:
                    entity = entity.replace(" ", "")
            # 如果entity在tokens中出现, 就表示匹配到了
            offsets = match_sublist(tokens, list(entity))
            if len(offsets) == 0:
                continue
            tentities.append([offsets[0][0], (entity, entity_type)])

        tentities = sorted(tentities, key=lambda x: x[0])
        ientities = [it[1] for it in tentities]
        tentity_list.append(ientities)

    return tentity_list


def remove_nested(entity_list):
    new_entity_list = []
    for entity in entity_list:
        result = []
        for i in range(len(entity)):
            is_nested = False
            for j in range(len(entity)):
                if i != j and entity[0] in entity[0]:
                    is_nested = True
                    break
            if not is_nested:
                result.append(entity[i])
        new_entity_list.append(result)
    return new_entity_list


def merge(
    text: List[str],
    entity1: List[List[List[str]]],
    entity2: List[List[List[str]]],
    alias_rev_db: SqliteDict,
    language: str = "en",
):
    if len(text) == 0:
        return [], []
    if len(entity1) == 0 and len(entity2) == 0:
        return [], []

    # 1、将texts的多余空格移除
    if language == "zh":
        text_list = [remove_space(texts) for texts in text]
    else:
        text_list = text

    # 2、合并record1(来自wiki链接)和record2(hanlp)中的实体, 注意消除text的"\u200b", 并获得doc级别的entity dict
    entity_list = merge_ner_list(
        remove_u200b(entity1), remove_u200b(entity2), alias_rev_db, language
    )

    # 3、用doc级别的entity dict匹配每个text(防遗漏), 注意zh中的英文entity text需要额外操作, 因为空格全被去掉了
    token_list = [list(texts) for texts in text_list]
    entity_list = get_offset(token_list, entity_list, language)
    # entity_list = remove_nested(entity_list)

    # 4、去掉没有实体的text
    new_text_list = []
    new_entity_list = []
    for texts, entities in zip(text_list, entity_list):
        if len(entities) == 0:
            continue
        new_text_list.append(texts)
        new_entity_list.append(entities)

    return new_text_list, new_entity_list


def worker(q: JoinableQueue, writer, print_lock: Lock, FLAGS) -> None:
    alias_rev_db = SqliteDict(FLAGS.alias_rev_db, flag="r")

    while True:
        json_data = q.get()
        try:
            record1, record2 = json_data["data1"], json_data["data2"]
        except TypeError:
            break

        text_list, entity_list = merge(
            record1["text"],
            record1["entity"],
            record2["entity"],
            alias_rev_db,
            FLAGS.language,
        )

        print_lock.acquire()
        writer.write(
            json.dumps(
                {"title": record1["title"], "text": text_list, "entity": entity_list},
                ensure_ascii=False,
            )
            + "\n"
        )
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
    parser.add_argument("wikiinput", type=str)
    parser.add_argument("hanlpinput", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument("-j", type=int, default=4, help="Number of processors")
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("--alias_rev_db", type=str, default="data/db/alias_rev.db")
    parser.add_argument("--mode", type=str, default="w")
    FLAGS, _ = parser.parse_known_args()

    main(_)
