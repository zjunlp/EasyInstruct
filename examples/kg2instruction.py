from easyinstruct import KG2InstructGenerator


generator = KG2InstructGenerator(
    label_db="/newdisk3/data/guihh/KG2Instruction/data/db/label_zh.db",
    alias_db="/newdisk3/data/guihh/KG2Instruction/data/db/alias_zh.db",
    alias_rev_db="/newdisk3/data/guihh/KG2Instruction/data/db/alias_rev_zh.db",
    relation_db="/newdisk3/data/guihh/KG2Instruction/data/db/relation.db",
    relation_map_path="/newdisk3/data/guihh/KG2Instruction/data/other/relation_map.json",
    model="/newdisk3/data/guihh/KG2Instruction/model/close_tok_pos_ner_srl_dep_sdp_con_electra_base",
    language="zh",
    device=0,
    add_relation_value=False
)
result = generator.generate("《三十而已》是一部由张晓波执导，江疏影、童瑶、毛晓彤等主演的都市情感剧，该剧于2020年7月17日在东方卫视首播，并在腾讯视频同步播出。")

print(result)

