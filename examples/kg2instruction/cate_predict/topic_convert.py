from collections import defaultdict
from tqdm import tqdm
import argparse
import json
import os


def result2cate(match_path, rel_path, cate_input_path):   
    '''
    从rel_path中读取所有的id(去除了所有关系为0的), 从match_path中读取存在于rel_path中的id的句子, 
    按照id、sentence、label格式写入cate_path中
    ''' 
    keep_hash = set()
    with open(rel_path, "r") as reader:
        for line in reader:
            data = json.loads(line)
            keep_hash.add(data["id"])

    writer = open(cate_input_path, "w")
    with open(match_path, "r") as reader:
        for line in tqdm(reader):
            data = json.loads(line)
            if data["id"] in keep_hash:
                writer.write(json.dumps({"id": data["id"], "sentence":data["text"], "label":0}, ensure_ascii=False)+"\n")
    writer.close()



def infer2newresult(match_path, rel_path, enttype_path, cate_predict_path, cate_path, language='zh'):
    '''
    从cate_prdict中读取id和topic, 从rel中读取relation, 从enttype中读取entity, 从match中读取text,
    最后输入到cate中
    '''
    label2id_en = {'Person': 0, 'Geographic Location': 1, 'Building': 2, 'Artificial Object': 3, 'Creature': 4, 'Astronomy': 5, 'Organization': 6, 'Natural Science': 7, 'Medicine': 8, 'Transport': 9, 'Event': 10, 'Works': 11, 'Other': 12}
    id2label_en = {0: 'Person', 1: 'Geographic Location', 2: 'Building', 3: 'Artificial Object', 4: 'Creature', 5: 'Astronomy', 6: 'Organization', 7: 'Natural Science', 8: 'Medicine', 9: 'Transport', 10: 'Event', 11: 'Works', 12: 'Other'}
    label2id_zh = {'人物': 0, '地理地区': 1, '建筑': 2, '人造物件': 3, '生物': 4, '天文对象': 5, '组织': 6, '自然科学': 7, '医学': 8, '运输': 9, '事件': 10, '作品': 11, '其他':12}
    id2label_zh = {0: '人物', 1: '地理地区', 2: '建筑', 3: '人造物件', 4: '生物', 5: '天文对象', 6: '组织', 7: '自然科学', 8: '医学', 9: '运输', 10: '事件', 11: '作品', 12: '其他'}

    if language == 'zh':
        label2id = label2id_zh
        id2label = id2label_zh
    else:
        label2id = label2id_en
        id2label = id2label_en
        

    cate_list = [it.replace(' ', '_') for it in label2id]
    for it in cate_list:
        os.makedirs(os.path.join(cate_dir, it), exist_ok=True)

    print(i, '进行中.........')
    match_path = os.path.join(match_path)
    rel_path = os.path.join(rel_path)
    enttype_path = os.path.join(enttype_path)
    cate_predict_path = os.path.join(cate_predict_path)

    cate_dict = defaultdict(list)
    mapper = defaultdict(list)
    with open(cate_predict_path, 'r') as reader:
        for line in reader:
            spt = line.strip().split("\t")
            predict = int(spt[-1])
            if predict == 12:
                continue
            mapper[spt[0]].append(id2label[predict])

    with open(rel_path, 'r') as reader:
        for line in reader:
            data = json.loads(line)
            if data['id'] not in mapper:
                continue
            mapper[data['id']].append(('relation', data['relation']))

    with open(enttype_path, 'r') as reader:
        for line in reader:
            data = json.loads(line)
            if data['id'] not in mapper:
                continue
            mapper[data['id']].append(('entity', data['entity']))
        
    with open(match_path, 'r') as reader:
        for line in reader:
            data = json.loads(line)
            if data['id'] not in mapper:
                continue
            mapper[data['id']].append(('text', data['text']))

    for key, value in mapper.items():
        if len(value) != 4:
            continue
        if value[3][0] != 'text' or value[2][0] != 'entity' or value[1][0] != 'relation':
            continue
        cate_dict[value[0]].append({'id':key, 'cate':value[0], 'text':value[3][1], 'entity':value[2][1], 'relation':value[1][1]})

    i = match_path.split('/')[-1].replace('.json', '').replace('match', '')
    for cate, data_list in cate_dict.items():
        with open(os.path.join(cate_path, cate.replace(' ', '_'), f'result{i}.json'), "w") as writer:
            for data in tqdm(data_list):
                writer.write(json.dumps(data, ensure_ascii=False) + "\n")



if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument("--match_path", type=str, default="data/zh/match")
    parse.add_argument("--rel_path", type=str, default="data/zh/rel")
    parse.add_argument("--enttype_path", type=str, default="data/zh/enttype")
    parse.add_argument("--cate_input_path", type=str, default="data/zh/cate_input")
    parse.add_argument("--cate_predict_path", type=str, default="data/zh/cate_predict")
    parse.add_argument("--cate_path", type=str, default="data/zh/cate")
    parse.add_argument("--language", type=str, default="zh")
    parse.add_argument("--mode", type=str, default="infer2newresult")
    args = parse.parse_args()

    if args.mode == "infer2newresult":
        infer2newresult(
            match_path=args.match_path, 
            rel_path=args.rel_path,  
            enttype_path=args.enttype_path,
            cate_predict_path=args.cate_predict_path,
            cate_path=args.cate_path, 
            language=args.language
        )
    elif args.mode == "result2cate":
        result2cate(
            match_path=args.match_path, 
            rel_path=args.rel_path,  
            cate_input_path=args.cate_input_path
        )


