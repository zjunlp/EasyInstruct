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
        if it[1] == 'located in':
            located_graph[it[0]].add(it[2])
    if len(located_graph) != 0:
        graphs = transitive_reduction(located_graph)
        if graphs != located_graph:
            newnew_merge = []
            for it in new_mergs:
                if it[1] == 'located in':
                    continue
                newnew_merge.append(it)
            for key, values in graphs.items():
                for it in values:
                    newnew_merge.append([key, 'located in', it])
            new_mergs = newnew_merge
    return new_mergs


def process_parent(new_mergs):
    located_graph = defaultdict(set)
    for it in new_mergs:
        if it[1] == 'parent taxon':
            located_graph[it[0]].add(it[2])
    if len(located_graph) != 0:
        graphs = transitive_reduction(located_graph)
        if graphs != located_graph:
            #print('graph', graphs)
            #print('located_graph', located_graph)
            #print('\n\n')
            newnew_merge = []
            for it in new_mergs:
                if it[1] == 'parent taxon':
                    continue
                newnew_merge.append(it)
            for key, values in graphs.items():
                for it in values:
                    newnew_merge.append([key, 'parent taxon', it])
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
        if it[1] == 'alternative name':
            bieming[it[2]] = it[0]
    for it in preds:
        it[0] = bieming.get(it[0], it[0])
        merges.add(tuple(it))
    return merges, bieming


def process1(preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        it[0] = bieming.get(it[0], it[0])
        if it[1] in ['has use', 'product', 'discoverer or inventor', 'composition']:
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    return new_mergs


def process2(preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        it[0] = bieming.get(it[0], it[0])
        if it[1] in ['drug or therapy used for treatment', 'disease transmission process', 'symptoms and signs', 'possible treatment']:
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    return new_mergs
    
def process3(preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        if it[1] in ['brand', 'discoverer or inventor', 'manufacturer', 'made from material']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    return new_mergs

def process4(preds, golds):
    merges = set()
    bieming = {}
    for it in preds:
        if it[1] == 'height':
            continue
        elif it[1] == 'alternative name':
            bieming[it[2]] = it[0]

    for it in preds:
        it[0] = bieming.get(it[0], it[0])
        merges.add(tuple(it))

    for it in golds:
        it[0] = bieming.get(it[0], it[0])
        if it[1] in ['area', 'length', 'width', 'elevation above sea level', 'population', 'located in']:
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    new_mergs = process_located(new_mergs)
    return new_mergs


def process5(text, preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        if it[1] == 'participant':
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))
        elif it[1] == 'winner':
            if text.startswith(it[0]):
                it[0] = bieming.get(it[0], it[0])
                merges.add(tuple(it))
        elif it[1] == 'awards':
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
        if it[1] == 'alternative name':
            bieming[it[2]] = it[0]
    
    for it in preds: 
        if it[1] == 'length':
            it[0] = bieming.get(it[0], it[0])
            long_set[(it[0], it[1])].add(tuple(it))       
        if it[1] in ['height', 'width', 'weight']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))
        else:
            merges.add(tuple(it))

    for it in golds:
        if it[1] == 'parent taxon':
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
        if it[1] == 'alternative name':
            bieming[it[2]] = it[0]
    
    for it in preds: 
        if it[1] in ['diameter', 'mass', 'time of discovery']:
            it[0] = bieming.get(it[0], it[0])
            long_set[(it[0], it[1])].add(tuple(it))       
        else:
            merges.add(tuple(it))

    for key, value in long_set.items():
        if len(value) == 1:
            merges.add(tuple(value.pop()))
    for it in golds:
        if it[1] == 'of':
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    return new_mergs


def process8(preds, golds):
    merges, bieming = preprocess(preds)
    new_mergs = postprocess(merges)
    for it in golds:
        if it[1] in ['located in', 'class of station']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))
    new_mergs = postprocess(merges)
    new_mergs = process_located(new_mergs)
    return new_mergs


def process9(preds, golds):
    merges, bieming = preprocess(preds)

    for it in golds:
        if it[1] in ['founded by', 'located in', 'product or material produced', 'member', 'has subsidiary']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))

    new_mergs = postprocess(merges)
    new_mergs = process_located(new_mergs)
    return new_mergs


def process10(text, preds, golds):
    merges = set()
    bieming = {}
    zuozhe = {}
    bianju = {}
    for it in preds:
        if it[1] == 'alternative name':
            bieming[it[2]] = it[0]
        elif it[1] == 'author':
            zuozhe[(it[0], it[1])] = it[2]
        elif it[1] == 'screenwriter':
            bianju[(it[0], it[1])] = it[2]

    for it in preds:
        it[0] = bieming.get(it[0], it[0])
        merges.add(tuple(it))

    for it in golds:
        if it[1] == 'author':
            it[0] = bieming.get(it[0], it[0])
            zuozhe[(it[0], it[1])] = it[2]
        elif it[1] == 'screenwriter':
            it[0] = bieming.get(it[0], it[0])
            bianju[(it[0], it[1])] = it[2]
        elif it[1] == 'publication date':
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))
        elif it[1] in ['country of origin', 'cast member', 'publisher', 'tracklist', 'developer']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))
        elif it[1] == 'original broadcaster':
            if text.find(it[0]) <= 5:
                it[0] = bieming.get(it[0], it[0])
                it[1] = 'platform'
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
        if it[1] in ["cast member","author","developer", "lyrics by", "production company","composer","producer", "screenwriter","director"]:
            spt = it[2].split('、')
            for iit in spt:
                final_merges.add((it[0], it[1], iit))
        else:
            final_merges.add(tuple(it))
    final_merges_s = []
    for it in final_merges:
        final_merges_s.append(list(it))

    return final_merges_s


def process11(text, preds, golds):
    merges = set()
    bieming = {}
    already = set()
    for it in preds:
        if it[1] == 'alternative name':
            bieming[it[2]] = it[0]
        if it[1] == 'parent':
            already.add(tuple(it))

    for it in golds:
        if it[1] in ['parent']:
            it[0] = bieming.get(it[0], it[0])
            if (tuple(it)) in already and ((it[2], it[1], it[0])) in already:
                continue
            merges.add(tuple(it))
        elif it[1] in ['spouse', 'sibling', 'member of', 'work', 'position held', 'occupation']:
            it[0] = bieming.get(it[0], it[0])
            merges.add(tuple(it))

    for it in preds:
        if it[1] in ['parent']:
            it[0] = bieming.get(it[0], it[0])
            if (it[0], it[1], it[2]) in already and (it[2], it[1], it[1]) in already:
                continue
        merges.add(tuple(it))

    new_mergs = postprocess(merges)
    already = set()
    for rel in new_mergs:
        if rel[1] == 'parent':
            already.add(tuple(rel))
    final_mergs = []
    for rel in new_mergs:
        if rel[1] == 'parent':
            if (rel[2], rel[1], rel[0]) in already and (rel[0], rel[1], rel[2]) in already:
                continue
        final_mergs.append(rel)
    return final_mergs


def process12(text, preds, golds):
    merges = set()
    bieming = {}
    for it in preds:
        if it[1] == 'alternative name':
            bieming[it[2]] = it[0]
    
    already = defaultdict(list)
    for it in preds:     
        if it[1] in ['height', 'width', 'length', 'area']:
            it[0] = bieming.get(it[0], it[0])
            index = text.find(it[2])
            merges.add(tuple(it))
        elif it[1] == 'creation time':
            already[(it[0], it[1])].append(it)
        else:
            merges.add(tuple(it))

    for key, value in already.items():
        if len(value) > 1:
            print(text, key, value)

    for it in golds:
        if it[1] in ['achievement', 'located in']:
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
            records_mapper[record['text']] = golds

    writer = open(path3, 'w')
    with open(path1, 'r') as reader:
        for line in reader:
            record = json.loads(line)
            record['input'] = record['text']
            preds = record['pred_list']
            golds = records_mapper[record['text']]

            if source == 'Natural_Science':
                merges = process1(preds, golds)
            elif source == 'Medicine':
                merges = process2(preds, golds)
            elif source == 'Artificial_Object':
                merges = process3(preds, golds)
            elif source == 'Geographic_Location':
                merges = process4(preds, golds)
            elif source == 'Event':
                merges = process5(record['input'], preds, golds)
            elif source == 'Creature':
                merges = process6(record['input'], preds, golds)
            elif source == 'Astronomy':
                merges = process7(preds, golds)
            elif source == 'Transport':
                merges = process8(preds, golds)
            elif source == 'Organization':
                merges = process9(preds, golds)
            elif source == 'Works':
                merges = process10(record['input'], preds, golds)
            elif source == 'Person':
                merges = process11(record['input'], preds, golds)
            elif source == 'Building':
                merges = process12(record['input'], preds, golds)

            relations = []
            for it in merges:
                relations.append({'head': it[0], 'relation': it[1], 'tail': it[2]})
            new_reord = {'text': record['input'], 'relation': relations}
            writer.write(json.dumps(new_reord, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    base_path1 = '/newdisk3/data/guihh/KG2Instruction/data/en/InstructIE-en-IEPile-predict'
    base_path2 = '/newdisk3/data/guihh/KG2Instruction/data/en/cate_limit_rule/first_nli0.5_filtered'
    source_list = ['Person', 'Geographic_Location', 'Building', 'Works', 'Creature', 'Artificial_Object', 'Natural_Science', 'Organization', 'Transport', 'Event', 'Astronomy', 'Medicine']   # 'Person', 'Geographic_Location', 'Building', 'Works', 'Creature', 'Artificial_Object', 'Natural_Science', 'Organization', 'Transport', 'Event', 'Astronomy', 'Medicine'
    for source in source_list:
        print(source)
        path1 = os.path.join(base_path1, 'InstructIE_'+ source + '.json')
        path2 = os.path.join(base_path2, 'InstructIE_'+ source, 'train.json')
        os.makedirs(os.path.join(base_path1, 'InstructIE_'+ source), exist_ok=True)
        schema1 = os.path.join(base_path2, 'InstructIE_'+ source, 'schema.json')
        schema2 = os.path.join(base_path1, 'InstructIE_'+ source, 'schema.json')
        shutil.copy(schema1, schema2)
        path3 = os.path.join(base_path1, 'InstructIE_'+ source, 'train.json')
        process(path1, path2, path3, source)
        
