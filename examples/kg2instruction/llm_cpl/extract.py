import argparse
import json

def post_process4(result):        
    try:      
        rst = json.loads(result)
    except json.decoder.JSONDecodeError:
        print("json decode error", result)
        return False, []
    if type(rst) != dict:
        print(f"type({rst}) != dict")
        return False, []
    new_record = []
    for key, values in rst.items():
        if type(key) != str or type(values) != list:
            if type(key) != str:
                print(f"type({key}) != str")
            elif type(values) != list:
                print(f"type({values}) != list")
            continue
        for iit in values:
            if type(iit) != dict:
                print(f"type({iit}) != dict")
                continue
            subject = iit.get('subject', '')
            object = iit.get('object', '')
            if type(subject) != str or type(object) != str:
                if type(subject) != str:
                    print(f"type({subject}) != str")
                elif type(object) != str:
                    print(f"type({object}) != str")
                continue
            new_record.append([subject, key, object])
    return new_record



def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("--path1", type=str, default="")
    parse.add_argument("--path2", type=str, default="")
    options = parse.parse_args() 
    
    mapper = {}
    with open(options.path1, 'r') as reader:
        for line in reader:
            data = json.loads(line)
            if type(data['instruction']) == str:
                sinput = json.loads(data['instruction'])['input']
            else:
                sinput = data['instruction']['input']
            iid = data['id']
            output = data['output'].strip()
            if iid in mapper:
                mapper[iid]['output'].append(output)
            else:
                mapper[iid] = {'cate':data.get('cate', 'all'), 'text':sinput, 'output':[output, ]}

    writer = open(options.path2, 'w')
    for key, value in mapper.items():
        preds = value['output']
        converted_preds = []
        for it in preds:
            out_rst = post_process4(it)
            converted_preds.extend(out_rst)
        data = {'cate': value['cate'], 'text': value['text'], 'relation': converted_preds}
        writer.write(json.dumps(data, ensure_ascii=False)+'\n')
        



if __name__=="__main__":
    main()

