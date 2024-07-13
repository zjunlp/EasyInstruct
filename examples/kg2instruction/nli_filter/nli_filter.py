import os
import sys
sys.path.append('./')
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import json
from collections import defaultdict
import argparse
from tqdm import tqdm


def load_nli_model_and_tokenizer(model_path, device):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
    return tokenizer, model, device


def convert_hypothesis(templates, rel):
    hypothesis = []
    for t in templates:
        h = t.replace('[X]', rel['head'])
        h = h.replace('[Y]', rel['tail'])
        hypothesis.append(h)
    return hypothesis


def get_hypotheses_for_relations(iid, cate, relations, template):
    hypothesis = []
    rel_texts = []
    iids = []
    template_dict = template[cate]
    for relation in relations:
        rel_text = f'{relation["head"]}_{relation["relation"]}_{relation["tail"]}'
        if relation["relation"] not in template_dict:
            continue
        templates = template_dict[relation["relation"]]
        tmp_hypothesis = convert_hypothesis(templates, relation)
        hypothesis += tmp_hypothesis
        rel_texts += [rel_text] * len(tmp_hypothesis)
        iids += [iid] * len(tmp_hypothesis)
    return iids, rel_texts, hypothesis


def get_score(premise, hypothesis, tokenizer, model, device):
    inputs = tokenizer(premise, hypothesis, truncation=True, padding=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs.to(device))
    scores = torch.softmax(outputs.logits, dim=-1)
    return scores[:, 0].tolist() 


def all_under_threshold(score_list, threshold):
    return all(score <= threshold for score in score_list)


def remove_rel_notin_template(relations, schema_list):
    new_rels = []
    for item in relations:
        if item['relation'] not in schema_list:
            continue
        new_rels.append(item)
    return new_rels
    


def nli_filter_datas(datas, batch_size, template, model, tokenizer, device, threshold):
    for batch_start in tqdm(range(0, len(datas), batch_size)):
        batch_data = datas[batch_start: batch_start + batch_size]
        iids, rel_texts, premises, hypotheses = [], [], [], []

        for i, data in enumerate(batch_data):
            data['relation'] = remove_rel_notin_template(data['relation'], list(template[data['cate']].keys()))
            tmp_iids, tmp_rel_texts, tmp_hypotheses = get_hypotheses_for_relations(i, data['cate'], data['relation'], template)
            premises.extend([data['text']] * len(tmp_hypotheses))
            iids.extend(tmp_iids)
            rel_texts.extend(tmp_rel_texts)
            hypotheses.extend(tmp_hypotheses)

        total_scores = []
        for batch_start in tqdm(range(0, len(premises), batch_size)):
            batch_premises = premises[batch_start: batch_start + batch_size]
            batch_hypotheses = hypotheses[batch_start: batch_start + batch_size]
            batch_scores = get_score(batch_premises, batch_hypotheses, tokenizer, model, device)
            total_scores.extend(batch_scores)

        hypothesis_score_dict = defaultdict(list)
        for iid, rel_text, score in zip(iids, rel_texts, total_scores):
            hypothesis_score_dict[(iid, rel_text)].append(score)

        remove_relation_dict = defaultdict(list)
        for (iid, rel_text), score_list in hypothesis_score_dict.items():
            score_list = hypothesis_score_dict.get((iid, rel_text), [])
            if all_under_threshold(score_list, threshold):
                remove_relation_dict[iid].append(rel_text)
                total_remove += 1
        
        for i, data in enumerate(batch_data):
            remove_relation = remove_relation_dict.get(i, [])
            new_rels = []
            for rel in data['relation']:
                rel_text = '_'.join([rel['head'], rel['relation'], rel['tail']])
                if rel_text not in remove_relation:
                    new_rels.append(rel)
            data['relation'] = new_rels
    return datas



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, default='')
    parser.add_argument('--output_path', type=str, default='')
    parser.add_argument('--mode', type=str, default='w')
    parser.add_argument('--language', type=str, default='zh')
    parser.add_argument('--device', type=int, default=0)
    parser.add_argument('--model_path', type=str, default="hf_models/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
    parser.add_argument('--template_path', type=str, default="data/other/template.json")
    parser.add_argument('--threshold', type=float, default=0.5)
    parser.add_argument('--batch_size', type=int, default=64)
    args = parser.parse_args()

    device = torch.device(f"cuda:{args.device}") if torch.cuda.is_available() else torch.device("cpu")
    tokenizer, model, device = load_nli_model_and_tokenizer(args.model_path, device)
    template_path = args.template_path
    template = json.load(open(template_path, 'r', encoding='utf-8'))[args.language]
    
    total_remove = 0
    already = set()
    if args.mode == 'a':
        with open(args.output_path, 'r') as reader:
            for line in reader:
                data = json.loads(line)
                already.add(data['id'])

    datas = []
    with open(args.input_path, 'r') as reader:
        for line in reader:
            data = json.loads(line)
            datas.append(data)

    datas = nli_filter_datas(datas, args.batch_size, template, model, tokenizer, device)
    writer = open(args.output_path, args.mode)
    for data in datas:
        writer.write(json.dumps(data, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()