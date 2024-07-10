import json

def read_from_json(path):
    datas = []
    with open(path, 'r') as reader:
        for line in reader:
            data = json.loads(line)
            datas.append(data)
    return datas


def write_to_json(path, datas):
    with open(path, 'w') as writer:
        for data in datas:
            writer.write(json.dumps(data, ensure_ascii=False)+"\n")

def match_sublist(the_list, to_match):
    len_to_match = len(to_match)
    matched_list = list()
    for index in range(len(the_list) - len_to_match + 1):
        if to_match == the_list[index:index + len_to_match]:
            matched_list += [(index, index + len_to_match)]
    return matched_list
