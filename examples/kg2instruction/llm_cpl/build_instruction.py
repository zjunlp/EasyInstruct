import json
import argparse
from collections import defaultdict


instruction_mapper = {
    'REzh': "你是专门进行关系抽取的专家。请从input中抽取出符合schema定义的关系三元组，不存在的关系返回空列表。请按照JSON字符串的格式回答。",
    'REen': "You are an expert in relationship extraction. Please extract relationship triples that match the schema definition from the input. Return an empty list for relationships that do not exist. Please respond in the format of a JSON string."
}


def build_instruction(language, schema_list, text):
    ins = instruction_mapper['RE'+language]
    split_schemas = [schema_list[i:i+4] for i in range(0, len(schema_list), 4)]
    sintructs = []
    for split_schema in split_schemas:
        sintructs.append({'instruction':ins, 'schema':split_schema, 'input':text},)
    return sintructs


def get_label_dict(records):
    labels = defaultdict(list)
    for rel in records:
        head = rel['head']
        relation = rel['relation']
        tail = rel['tail']
        labels[relation].append({'subject':head, 'object':tail})
    return labels


def convert_target4(text, schema, label_dict):
    outputs = defaultdict(list)
    for it in schema:
        if it not in label_dict:
            outputs[it] = []
        else:
            outputs[it] = label_dict[it]
    
    sorted_outputs = {}
    for key, value in outputs.items():
        value_index = []
        for it in value:
            value_index.append([text.find(it['subject']), text.find(it['object']), it])
        value_index.sort(key=lambda x:(x[0], x[1]))
        sorted_value = []
        for it in value_index:
            sorted_value.append(it[2])
        sorted_outputs[key] = sorted_value

    output_text = json.dumps(dict(sorted_outputs), ensure_ascii=False)
    return output_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, default='')
    parser.add_argument('--output_path', type=str, default='')
    parser.add_argument('--mode', type=str, default='train')
    parser.add_argument('--language', type=str, default='zh')
    parser.add_argument('--cate', type=str, default='人物')
    parser.add_argument('--template_path', type=str, default="./data/other/template.json")
    args = parser.parse_args()
    
    schema_dict = {}
    template = json.load(open(args.template_path))
    for lang, values1 in template.items():
        for key_cate, values2 in values2:
            schema_list = list(values2.keys())
            schema_dict[key_cate] = schema_list

    cate_data_dict = defaultdict(list)
    writer = open(args.output_path)
    with open(args.input_path) as reader:
        for line in reader:
            data = json.loads(line)
            cate_data_dict[data['cate']].append(data)
            
    
    for cate, datas in cate_data_dict.items():
        schema_list = schema_dict[cate]
        for i, data in enumerate(datas):
            instructions = build_instruction(args.language, schema_list, data['text'])
            if args.mode == 'train':
                label_dict = get_label_dict(data['realtion'])
                for ins in instructions:
                    output_text = convert_target4(data['text'], ins['schema'], label_dict)
                    new_data = {'instruction': json.dumps(ins, ensure_ascii=True), 'output': output_text}
                    writer.write(json.dumps(new_data, ensure_ascii=False)+'\n')
            else:
                for ins in instructions:
                    if 'id' in data:
                        iid = data['id']
                    else:
                        iid = cate+'_'+str(i)
                    new_data = {'id':iid, 'cate':cate, 'instruction': json.dumps(ins, ensure_ascii=True)}
                    writer.write(json.dumps(new_data, ensure_ascii=False)+'\n')



if __name__ == '__main__':
    main()

