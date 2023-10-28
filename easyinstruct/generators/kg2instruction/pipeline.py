import argparse
import logging
from sqlitedict import SqliteDict
import hanlp

from .util import LOG_FORMAT, stable_hash, format_wikilink
from .hanlp_ner import ner
from .match_qid import match_qid
from .find_rel import Annotator

logger = logging.getLogger(__name__)


def main(_):
    label_db = SqliteDict(FLAGS.label_db, flag="r")
    alias_db = SqliteDict(FLAGS.alias_db, flag="r")
    alias_rev_db = SqliteDict(FLAGS.alias_rev_db, flag="r")
    relation_db = SqliteDict(FLAGS.relation_db, flag="r")
    if FLAGS.add_relation_value:
        relation_value_db = SqliteDict(FLAGS.relation_value_db, flag="r")
    else:
        relation_value_db = None
    HanLP = hanlp.load(FLAGS.model, devices=FLAGS.device)

    text_list = [
        FLAGS.input,
    ]
    # 1、ner识别实体, 返回 List[List[List[str]]]
    hanlp_entities_list = ner(text_list, HanLP, FLAGS.language, FLAGS.chunk)

    # 2、从alias_rev_db中找到对应的wikidata ID, 返回List[List[List[str]]]
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

    # 3、对实体进行消歧, 每个实体都得到唯一的wikidata ID, 返回List[List[List[str]]]
    match_entities_list = match_qid(
        new_entities_list, label_db, alias_db, alias_rev_db, relation_db, FLAGS.language
    )

    # 4、匹配实体间的关系, 返回{'text':List[str], 'entity':List[List[List[str]]], 'relation': List[List[Dict]]}
    annotator = Annotator(
        alias_db,
        relation_db,
        relation_value_db,
        FLAGS.relation_map_path,
        FLAGS.language,
    )

    for text, entities in zip(text_list, match_entities_list):
        if len(entities) == 0:
            continue
        iid = stable_hash(text)
        relations, new_entities = annotator.annotate(entities, text)
        print("id:", iid)
        print("text:", text)
        print("entity:", new_entities)
        print("relation:", relations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("--mode", type=str, default="w", help="w: rewrite; a: append")

    parser.add_argument("--label_db", type=str, default="data/db/label.db")
    parser.add_argument("--alias_db", type=str, default="data/db/alias.db")
    parser.add_argument("--alias_rev_db", type=str, default="data/db/alias_rev.db")
    parser.add_argument("--relation_db", type=str, default="data/db/relation.db")
    parser.add_argument(
        "--relation_value_db", type=str, default="data/db/relation_value.db"
    )
    parser.add_argument(
        "--relation_map_path", type=str, default="data/other/relation_map.json"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="model/close_tok_pos_ner_srl_dep_sdp_con_electra_base",
    )
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--chunk", type=int, default=5)
    parser.add_argument("--add_relation_value", action="store_true")

    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)
