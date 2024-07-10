import json
import random
random.seed(42)
import argparse


def remove_nested_triplets(triplets):    
    '''
    移除嵌套的三元组, 选择最长的三元组
    '''
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
    '''
    从preds中获得别名映射
    替换preds三元组中的别名
    '''
    merges = set()
    bieming = {}
    for it in preds:
        if it[1] == '别名':
            bieming[it[2]] = it[0]
    for it in preds:
        it[0] = bieming.get(it[0], it[0])
        merges.add(tuple(it))
    return merges, bieming


def merge_pred_gold(preds, golds):
    '''
    替换golds三元组中的别名
    移除嵌套的三元组
    '''
    merges, bieming = preprocess(preds)
    for it in golds:
        it[0] = bieming.get(it[0], it[0])
        merges.add(tuple(it))
    merges = postprocess(merges)
    return merges


def merge_relations(pred_list, gold_list):
    gold_rels = []
    for it in gold_list:
        gold_rels.append([it['head'], it['relation'], it['tail']])
    merges = merge_pred_gold(pred_list, gold_rels)
    merge_rels = []
    for it in merges:
        merge_rels.append({'head': it[0], 'relation': it[1], 'tail': it[2]})
    return merge_rels



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path1", type=str, default="")
    parser.add_argument("--path2", type=str, default="")
    parser.add_argument("--tgt_path", type=str, default="")
    options = parser.parse_args() 


    mapper = {}
    with open(options.path2, 'r') as reader:
        for line in reader:
            data = json.loads(line)
            mapper[data['text']] = data['relation']

    writer = open(options.tgt_path, 'w')
    with open(options.path1, 'r') as reader:
        for line in reader:
            data = json.loads(line)
            pred_list = mapper[data['text']]
            merges = merge_relations(pred_list, data['relation'])
            data['relation'] = merges
            writer.write(json.dumps(data, ensure_ascii=False) + '\n')
