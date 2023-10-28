from .base_generator import BaseGenerator
from sqlitedict import SqliteDict
import hanlp

from .kg2instruction.util import format_wikilink
from .kg2instruction.hanlp_ner import ner
from .kg2instruction.match_qid import match_qid
from .kg2instruction.find_rel import Annotator


class KG2InstructGenerator(BaseGenerator):
    def __init__(
        self,
        label_db,
        alias_db,
        alias_rev_db,
        relation_db,
        relation_map_path,
        model,
        language="zh",
        relation_value_db="",
        add_relation_value=False,
        device=0,
        chunk=5,
    ):
        super().__init__()
        self.label_db = SqliteDict(label_db, flag="r")
        self.alias_db = SqliteDict(alias_db, flag="r")
        self.alias_rev_db = SqliteDict(alias_rev_db, flag="r")
        self.relation_db = SqliteDict(relation_db, flag="r")
        self.language = language
        self.add_relation_value = add_relation_value
        if self.add_relation_value:
            self.relation_value_db = SqliteDict(relation_value_db, flag="r")
        else:
            self.relation_value_db = None
        self.relation_map_path = relation_map_path
        self.HanLP = hanlp.load(model, devices=device)
        self.chunk = chunk

    def generate(self, input):
        text_list = [
            input,
        ]
        # 1、ner识别实体, 返回 List[List[List[str]]]
        hanlp_entities_list = ner(text_list, self.HanLP, self.language, self.chunk)

        # 2、从alias_rev_db中找到对应的wikidata ID, 返回List[List[List[str]]]
        new_entities_list = []
        for entities in hanlp_entities_list:
            new_entities = []
            for entity in entities:
                try:
                    iids = self.alias_rev_db[format_wikilink(entity[0])]
                except KeyError:
                    continue
                if len(iids) > 0:
                    iids = iids[0]
                    new_entities.append([entity[0], iids])
            new_entities_list.append(new_entities)

        # 3、对实体进行消歧, 每个实体都得到唯一的wikidata ID, 返回List[List[List[str]]]
        match_entities_list = match_qid(
            new_entities_list,
            self.label_db,
            self.alias_db,
            self.alias_rev_db,
            self.relation_db,
            self.language,
        )

        # 4、匹配实体间的关系, 返回{'text':List[str], 'entity':List[List[List[str]]], 'relation': List[List[Dict]]}
        annotator = Annotator(
            self.alias_db,
            self.relation_db,
            self.relation_value_db,
            self.relation_map_path,
            self.language,
        )

        for text, entities in zip(text_list, match_entities_list):
            if len(entities) == 0:
                continue
            relations, new_entities = annotator.annotate(entities, text)
        return {"text": text, "entity": new_entities, "relation": relations}
