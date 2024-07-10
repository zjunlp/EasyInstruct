import json
from collections import defaultdict
import os
import shutil

def transitive_closure(graph):
    # Using Floyd-Warshall algorithm to compute transitive closure
    closure = {node: set(neighbors) for node, neighbors in graph.items()}
    for k in graph:
        for i in closure:
            # Skip if there is no edge between i and k
            if k not in closure[i]:
                continue
            for j in closure[k]:
                if i != j:  
                    closure[i].add(j)
    return closure

def transitive_reduction(graph):
    closure = transitive_closure(graph)
    reduction = {node: set(neighbors) for node, neighbors in graph.items()}
    for i in graph:
        for j in graph[i]:
            if i == j:
                if len(closure.get(i, {i}) - {i}) > 0:
                    reduction[i].remove(j)
                continue
            for k in closure.get(i, []):
                if k != i and k != j and j in closure.get(k, []):
                    reduction[i].remove(j)
                    break
    return reduction

def process_located(new_mergs):
    located_graph = defaultdict(set)
    for it in new_mergs:
        if it[1] == '位于':
            located_graph[it[0]].add(it[2])
    if len(located_graph) != 0:
        graphs = transitive_reduction(located_graph)
        if graphs != located_graph:
            newnew_merge = []
            for it in new_mergs:
                if it[1] == '位于':
                    continue
                newnew_merge.append(it)
            for key, values in graphs.items():
                for it in values:
                    newnew_merge.append([key, '位于', it])
            new_mergs = newnew_merge
    return new_mergs


def process_parent(new_mergs):
    located_graph = defaultdict(set)
    for it in new_mergs:
        if it[1] == '父级分类单元':
            located_graph[it[0]].add(it[2])
    if len(located_graph) != 0:
        graphs = transitive_reduction(located_graph)
        if graphs != located_graph:
            #print('graph', graphs)
            #print('located_graph', located_graph)
            #print('\n\n')
            newnew_merge = []
            for it in new_mergs:
                if it[1] == '父级分类单元':
                    continue
                newnew_merge.append(it)
            for key, values in graphs.items():
                for it in values:
                    newnew_merge.append([key, '父级分类单元', it])
            new_mergs = newnew_merge
    return new_mergs
    

def remove_nested_triplets(triplets):    
    for i in range(len(triplets)):
        for j in range(len(triplets)):
            if i != j and triplets[i][0] == triplets[j][0] and triplets[i][1] == triplets[j][1] and triplets[i][2] != triplets[j][2] and triplets[i][2] in triplets[j][2]:
                triplets[i][2] = triplets[j][2]
            if i != j and triplets[i][0] != triplets[j][0] and triplets[i][1] == triplets[j][1] and triplets[i][2] == triplets[j][2] and triplets[i][0] in triplets[j][0]:
                triplets[i][0] = triplets[j][0]
    return triplets


def postprocess(merges):
    new_mergs = []
    for it in merges:
        new_mergs.append(list(it))
    new_mergs = remove_nested_triplets(new_mergs)
    new_mergs_set = set()
    for it in new_mergs:
        new_mergs_set.add(tuple(it))
    new_mergs = []
    for it in new_mergs_set:
        new_mergs.append(list(it))
    return new_mergs


def preprocess(preds):
    merges = set()
    bieming = {}
    for it in preds:
        if it[1] == '别名':
            bieming[it[2]] = it[0]
    for it in preds:
        it[0] = bieming.get(it[0], it[0])
        merges.add(tuple(it))
    return merges, bieming


def process1(preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        it[0] = bieming.get(it[0], it[0])
        if it[1] in ['用途', '生成物', "发现者或发明者", "组成"]:
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    return new_mergs


def process2(preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        it[0] = bieming.get(it[0], it[0])
        if it[1] in ['用药', '传播方式', '症状', '疗法']:
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    return new_mergs
    
def process3(preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        if it[1] in ['品牌', '发现者或发明者', '制造商', '材料']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    return new_mergs

def process4(preds, golds):
    merges = set()
    bieming = {}
    for it in preds:
        if it[1] == '高度':
            continue
        elif it[1] == '别名':
            bieming[it[2]] = it[0]

    for it in preds:
        it[0] = bieming.get(it[0], it[0])
        merges.add(tuple(it))

    for it in golds:
        it[0] = bieming.get(it[0], it[0])
        if it[1] in ['面积', '长度', '宽度', '海拔', '人口', '位于']:
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    new_mergs = process_located(new_mergs)
    return new_mergs


def process5(text, preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        if it[1] == '参与者':
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))
        elif it[1] == '获胜者':
            if text.startswith(it[0]):
                it[0] = bieming.get(it[0], it[0])
                merges.add(tuple(it))
        elif it[1] == '所获奖项':
            if text.endswith(it[2]):
                it[0] = bieming.get(it[0], it[0])
                merges.add(tuple(it))
    
    new_mergs = postprocess(merges)
    return new_mergs

def process6(text, preds, golds):
    merges = set()
    bieming = {}
    long_set = defaultdict(set)
    for it in preds:
        if it[1] == '别名':
            bieming[it[2]] = it[0]
    
    for it in preds: 
        if it[1] == '长度':
            it[0] = bieming.get(it[0], it[0])
            long_set[(it[0], it[1])].add(tuple(it))       
        if it[1] in ['高度', '宽度', '重量']:
            it[0] = bieming.get(it[0], it[0])
            index = text.find(it[2])
            if text[index-1] == '约':
                it[2] = '约' + it[2]
            merges.add(tuple(it))
        else:
            merges.add(tuple(it))

    for it in golds:
        if it[1] == '父级分类单元':
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))
    
    for key, value in long_set.items():
        if len(value) == 1:
            merges.add(tuple(value.pop()))

    new_mergs = postprocess(merges)
    new_mergs = process_parent(new_mergs)
    return new_mergs


def process7(preds, golds):
    merges = set()
    bieming = {}
    long_set = defaultdict(set)
    for it in preds:
        if it[1] == '别名':
            bieming[it[2]] = it[0]
    
    for it in preds: 
        if it[1] in ['直径', '质量', '发现时间']:
            it[0] = bieming.get(it[0], it[0])
            long_set[(it[0], it[1])].add(tuple(it))       
        else:
            merges.add(tuple(it))

    for key, value in long_set.items():
        if len(value) == 1:
            merges.add(tuple(value.pop()))
    for it in golds:
        if it[1] == '属于':
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    return new_mergs


def process8(preds, golds):
    merges, bieming = preprocess(preds)
    for it in golds:
        if it[1] in ['位于', '车站等级']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))
    new_mergs = postprocess(merges)
    new_mergs = process_located(new_mergs)
    return new_mergs


def process9(preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        if it[1] in ['创办者', '位于', '产品', '成员', '子组织']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    new_mergs = process_located(new_mergs)
    return new_mergs


def process10(text, preds, golds, entities):
    merges = set()
    bieming = {}
    zuozhe = {}
    bianju = {}
    for it in preds:
        if it[1] == '别名':
            bieming[it[2]] = it[0]
        elif it[1] == '作者':
            zuozhe[(it[0], it[1])] = it[2]
        elif it[1] == '编剧':
            bianju[(it[0], it[1])] = it[2]

    for it in preds:
        it[0] = bieming.get(it[0], it[0])
        merges.add(tuple(it))

    for it in golds:
        if it[1] == '作者':
            it[0] = bieming.get(it[0], it[0])
            zuozhe[(it[0], it[1])] = it[2]
        elif it[1] == '编剧':
            it[0] = bieming.get(it[0], it[0])
            bianju[(it[0], it[1])] = it[2]
        elif it[1] == '出版时间':
            it[0] = bieming.get(it[0], it[0])
            if '月' in it[2]:
                merges.add(tuple(it))
        elif it[1] in ['产地', '演员', '出版商', '曲目', '开发者']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))
        elif it[1] == '首播电视台':
            if text.find(it[0]) <= 5:
                it[0] = bieming.get(it[0], it[0])
                it[1] = '平台'
                merges.add(tuple(it))

    for key, value in zuozhe.items():
        if key not in bianju and key[0] not in bieming:
            merges.add((key[0], key[1], value))

    new_mergs = []
    for it in merges:
        new_mergs.append(list(it))
    new_mergs = remove_nested_triplets(new_mergs)
    final_merges = set()
    for it in new_mergs:
        if it[1] in ["演员","作者","开发者", "作词者", "制作商","作曲者","制片人", "编剧","导演"]:
            spt = it[2].split('、')
            for iit in spt:
                final_merges.add((it[0], it[1], iit))
        else:
            final_merges.add(tuple(it))
    final_merges_s = []
    for it in final_merges:
        final_merges_s.append(list(it))

    persons = set()
    for ent in entities:
        enttype = ent[2].split('/')[0]
        if enttype == '人物' or enttype == '组织' or enttype == '其他':
            persons.add(ent[0])

    new_merges_s = []
    for it in final_merges_s:
        if it[1] in ["演员","作者","开发者", "作词者", "制作商","作曲者","制片人", "编剧","导演"]:
            if it[2] in persons:
                new_merges_s.append(it)
            else:
                p = []
                for person in persons:
                    if person in it[2] and it[2] not in person:
                        p.append(person)
                if len(p) > 1:
                    for i in p:
                        new_merges_s.append([it[0], it[1], i])
                else:
                    new_merges_s.append(it)
        else:
            new_merges_s.append(it)
    return new_merges_s


def process11(text, preds, golds):
    merges = set()
    bieming = {}
    already = set()
    for it in preds:
        if it[1] == '别名':
            bieming[it[2]] = it[0]
        if it[1] == '父母':
            already.add(tuple(it))

    for it in golds:
        if it[1] in ['父母']:
            it[0] = bieming.get(it[0], it[0])
            if (tuple(it)) in already and ((it[2], it[1], it[0])) in already:
                continue
            merges.add(tuple(it))
        elif it[1] in ['配偶', '兄弟姊妹', '所属组织', '作品', '职务', '职业']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))

    for it in preds:
        if it[1] in ['父母']:
            it[0] = bieming.get(it[0], it[0])
            if (it[0], it[1], it[2]) in already and (it[2], it[1], it[1]) in already:
                continue
        merges.add(tuple(it))

    new_mergs = postprocess(merges)
    already = set()
    for rel in new_mergs:
        if rel[1] == '父母':
            already.add(tuple(rel))
    final_mergs = []
    for rel in new_mergs:
        if rel[1] == '父母':
            if (rel[2], rel[1], rel[0]) in already and (rel[0], rel[1], rel[2]) in already:
                continue
        final_mergs.append(rel)
    return final_mergs


def process12(text, preds, golds):
    merges = set()
    bieming = {}
    for it in preds:
        if it[1] == '别名':
            bieming[it[2]] = it[0]
    
    already = defaultdict(list)
    for it in preds:     
        if it[1] in ['高度', '宽度', '长度', '面积']:
            it[0] = bieming.get(it[0], it[0])
            index = text.find(it[2])
            if text[index-1] == '约':
                it[2] = '约' + it[2]
            merges.add(tuple(it))
        elif it[1] == '创建时间':
            already[(it[0], it[1])].append(it)
        else:
            merges.add(tuple(it))

    for key, value in already.items():
        if len(value) > 1:
            print(text, key, value)

    for it in golds:
        if it[1] in ['成就', '位于']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    new_mergs = process_located(new_mergs)
    return new_mergs



def process(path1, path2, path3, source):
    records_mapper = {}
    with open(path2, 'r') as reader:
        for line in reader:
            record = json.loads(line)
            golds = []
            for it in record['relation']:
                golds.append([it['head'], it['relation'], it['tail']])
            records_mapper[record['text']] = [golds, record['entity']]

    writer = open(path3, 'w')
    with open(path1, 'r') as reader:
        for line in reader:
            record = json.loads(line)
            record['input'] = record['text']
            preds = record['pred_list']
            golds, record['entity'] = records_mapper[record['text']]

            if source == '自然科学':
                merges = process1(preds, golds)
            elif source == '医学':
                merges = process2(preds, golds)
            elif source == '人造物件':
                merges = process3(preds, golds)
            elif source == '地理地区':
                merges = process4(preds, golds)
            elif source == '事件':
                merges = process5(record['input'], preds, golds)
            elif source == '生物':
                merges = process6(record['input'], preds, golds)
            elif source == '天文对象':
                merges = process7(preds, golds)
            elif source == '运输':
                merges = process8(preds, golds)
            elif source == '组织':
                merges = process9(preds, golds)
            elif source == '作品':
                merges = process10(record['input'], preds, golds, record['entity'])
            elif source == '人物':
                merges = process11(record['input'], preds, golds)
            elif source == '建筑结构':
                merges = process12(record['input'], preds, golds)
            relations = []
            for it in merges:
                relations.append({'head': it[0], 'relation': it[1], 'tail': it[2]})
            new_reord = {'text': record['input'], 'relation': relations}
            writer.write(json.dumps(new_reord, ensure_ascii=False) + '\n')


        
if __name__ == '__main__':
    base_path1 = '/newdisk3/data/guihh/KG2Instruction/data/zh/InstructIE-zh-IEPile-predict'
    base_path2 = '/newdisk3/data/guihh/KG2Instruction/data/zh/cate_limit_rule/first_nli0.5_filtered'
    source_list = ['自然科学', '医学', '人造物件', '地理地区', '事件', '生物', '天文对象', '运输', '组织', '作品', '人物', '建筑结构']   # '自然科学', '医学', '人造物件', '地理地区', '事件', '生物', '天文对象', '运输', '组织', '作品', '人物', '建筑结构'
    for source in source_list:
        print(source)
        path1 = os.path.join(base_path1, 'InstructIE_'+ source + '.json')
        path2 = os.path.join(base_path2, source, 'train.json')
        os.makedirs(os.path.join(base_path1, 'InstructIE_'+ source), exist_ok=True)
        schema1 = os.path.join(base_path2, source, 'schema.json')
        schema2 = os.path.join(base_path1, 'InstructIE_'+ source, 'schema.json')
        shutil.copy(schema1, schema2)
        continue
        path3 = os.path.join(base_path1, 'InstructIE_'+ source, 'train.json')
        process(path1, path2, path3, source)