from typing import Any, Dict, Generator, List, Set
import bz2
import json
import logging
import tqdm
import string
import re
import os
from tqdm import tqdm
import tarfile
import zhconv
import hashlib


def stable_hash(input_str):
    sha256 = hashlib.sha256()
    sha256.update(input_str.encode("utf-8"))
    return sha256.hexdigest()


logger = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def flatten_tokens(tokens: List[List[str]]) -> List[str]:
    return [word for sent in tokens for word in sent]


def format_wikilink(wikilink: str, language="en") -> str:
    wikilink = wikilink.strip()
    wikilink = wikilink.replace(" ", "_").replace("\u200b", "")
    if language == "en":
        return wikilink.lower()
    else:
        return zhconv.convert(wikilink, "zh-hans")


def format_title(title):  # 有些会有(XXX)注释, 需要去掉, 即 YYY(XXX)->YYY
    if title is None:
        return None
    if "(" in title:
        index = title.find("(")
        if index != -1:
            return title[:index].strip()
    if "（" in title:
        index = title.find("（")
        if index != -1:
            return title[:index].strip()
    return title


def format_titletext(titletext):
    if titletext is None:
        return None
    return clean_u200b(titletext.replace("《", "").replace("》", ""))


def get_length(text, language="en"):
    if language == "zh":
        return len(text)
    else:
        return len(text.split(" "))


def generate_from_json_bz2(fname: str) -> Generator[Dict[str, Any], None, None]:
    with bz2.open(fname) as f:
        f.read(2)  # skip first two bytes: "{\n"
        for line in tqdm(f):
            try:
                yield json.loads(line[:-2])
            except json.decoder.JSONDecodeError:
                logger.warning('Could not decode line to JSON:\n"%s"\n', line)
                continue


def generate_from_json_tar_gz(
    fname: str, target_file: str
) -> Generator[Dict[str, Any], None, None]:
    with tarfile.open(fname, "r:gz") as tar:
        with tar.extractfile(target_file) as f:
            for line in tqdm(f):
                try:
                    yield json.loads(line[:-2])
                except json.decoder.JSONDecodeError:
                    logger.warning('Could not decode line to JSON:\n"%s"\n', line)
                    continue


def load_allowed_entities(fname: str) -> Set[str]:
    """Loads a set of allowed entities from a txt file."""
    if fname is None:
        logger.info("Entities not restricted")
        return
    else:
        logger.info('Loading allowed entities from: "%s"', fname)
        allowed_entities = set()
        with open(fname, "r") as f:
            for line in f:
                allowed_entities.add(line.strip())
        logger.info("%i allowed entities found", len(allowed_entities))
        return allowed_entities


def load_already(soutput: str, key: str = "title"):
    already = set()
    if os.path.exists(soutput):
        with open(soutput, "r", encoding="utf-8") as reader:
            for line in reader:
                already.add(json.loads(line.strip())[key])
    return already


def containChinese(text):
    zhPattern = re.compile("[\u4e00-\u9fa5]+")
    match = zhPattern.search(text)
    if match:
        return True
    else:
        return False


def containEnglish(text):
    zhPattern = re.compile("[A-Za-z]+")
    match = zhPattern.search(text)
    if match:
        return True
    else:
        return False


def is_all_english(strs):
    for i in strs:
        if i not in string.ascii_lowercase + string.ascii_uppercase + " ":
            return False
    return True


def chinese_ratio(text):
    if len(text) == 0:
        return 0
    chinese_chars = 0
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            chinese_chars += 1
    return chinese_chars / len(text)


def remove_space(texts):
    texts = texts.strip()
    tokens = list(texts)
    new_tokens = []
    i = 0
    while i < len(tokens):
        if tokens[i] == " ":
            j = i
            while j < len(tokens) and tokens[j] == " ":
                j += 1
            if containEnglish(tokens[i - 1]) and containEnglish(tokens[j]):
                new_tokens.append(tokens[i])
        else:
            new_tokens.append(tokens[i])
        i += 1
    return "".join(new_tokens).replace("\u200b", "")


def add_space(tokens, entity):
    """
    ['Hello', ',', 'Nice', 'to', 'meet', 'you', '.', '你', '今天', '吃', '了', '饭', '吗']
    "Nicetomeet"
    """
    i = 0
    while i < len(tokens):
        if entity.startswith(tokens[i]):
            start = i + 1
            tmp = tokens[i]
            while start < len(tokens):
                if entity.startswith(tmp + tokens[start]):
                    tmp = tmp + tokens[start]
                    start += 1
                elif tokens[start] == " ":
                    start += 1
                else:
                    break
            if tmp == entity:
                return tokens[i:start]
        i += 1
    return entity


def clean_u200b(s):
    return s.replace("\u200b", "")


def language_convert(s, language="zh"):
    """
    中文全部转换为中文简体
    """
    s = s.strip()
    if s is None:
        return None
    if language == "zh":
        return zhconv.convert(s, "zh-hans")
    return s
