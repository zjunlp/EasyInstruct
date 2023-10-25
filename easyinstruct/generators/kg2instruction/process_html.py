from typing import Any, Dict
import argparse
import json
import logging
import re
from tqdm import tqdm
from bs4 import BeautifulSoup
from sqlitedict import SqliteDict

from .util import (
    format_wikilink,
    format_title,
    format_titletext,
    load_already,
    language_convert,
    clean_u200b,
    get_length,
)
from .clean_html import clean_soup

logger = logging.getLogger(__name__)


RE_WHITESPACE = re.compile(r"[\n\r\s]+")
RE_HEADER = re.compile(r"^h[1-6]")


def generate_instances(FLAGS: str) -> Dict[str, Any]:
    """Generates instances from an input JSON-lines file"""
    with open(FLAGS.input, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            data = json.loads(line)
            yield data


def process(
    title: str,
    root: BeautifulSoup,
    wiki_db: SqliteDict,
    alias_rev_db: SqliteDict,
    language: str,
    max_len: int = 512,
) -> Dict[str, Any]:
    ids = []
    spans = []
    # 1、先在wiki.db(已经消歧义了)中查找qid
    try:
        title_id = wiki_db[format_wikilink(title, language)]
    except KeyError:
        # 2、没找到title, 就format(title)到alias_rev.db中找, 肯定有多个Qid, 不要怕, 象征性地选第一个Qid, 这里主要是先初步识别出实体, 不需要考虑歧义
        try:
            ttitle = format_wikilink(format_title(title), language)
            title_id = alias_rev_db[ttitle]
        except KeyError:
            title_id = None
        else:
            if len(title_id) > 0:
                title_id = title_id[0]
            else:
                title_id = None

    def _recursion(node):
        """
        If node is a link, make sure text is annotated with the corresponding title attribute.
        NOTE: title is an attribute of the <a> tag. Don't get confused with the page title.
        ids、text总是同时append的, text添加的是文本, ids添加的是实体Qid
        """
        if node.name == "a":
            try:
                key = format_wikilink(node["title"], language)
            except KeyError:
                key = None
            # 对于所有的<a></a>, 一般来说都是实体, 会先查询wiki.db再查询alias_rev.db(一定要先查询wiki.db!!一定有wikipedia文章)
            try:
                iid = wiki_db[key]
            except KeyError:
                # 查询alias_rev.db的时候要小心格式, 去掉()、（）、《》等
                try:
                    stitle = format_wikilink(
                        format_title(format_titletext(node["title"])), language
                    )
                    iids = alias_rev_db[stitle]
                except KeyError:
                    iid = None  # 进一步思考, 如果<a></a>既没有在wiki.db中查到, 又没有在alias_rev.db中查到, 可以删了
                else:
                    if len(iids) > 0:
                        iid = iids[0]
                    else:
                        iid = None
            ids.append(iid)
            spans.append(node.text)
        elif RE_HEADER.search(str(node.name)):
            pass
        elif (
            node.name == "b" and len(spans) < 10
        ):  # 对于头几个<b></b>, 会直接将它们与title联系起来, 这也是符合的(当然也有些例外)
            if len(node.text) > 1:
                ids.append(title_id)
                spans.append(format_titletext(node.text))
            else:
                ids.append(None)
                spans.append(format_titletext(node.text))
        else:  # 其他情况（如果有children就需要递归）
            if hasattr(node, "children"):
                for child in node.children:
                    _recursion(child)
            else:
                ids.append(None)
                spans.append(str(node))

    _recursion(root)

    entity_list = []
    doc_list = []
    entities = []
    doc = []
    """
    两种分割情况：
    1、span == "\n"
    2、段落长度达到max_len, 且一直没有碰到span == "\n"
    """
    for tid, span in zip(ids, spans):
        span = clean_u200b(span)
        if span == "\n":
            if len(doc) != 0:
                processed = language_convert("".join(doc), language)
                if len(processed.strip()) > 0:
                    doc_list.append(processed)
                    entity_list.append(entities)
                    entities = []
                    doc = []
        else:
            if (
                get_length("".join(doc) + span, language) > max_len
                and len(doc) > 0
                and doc[-1].endswith("\n")
            ):
                processed = language_convert("".join(doc), language)
                if len(processed.strip()) > 0:
                    doc_list.append(processed)
                    entity_list.append(entities)
                    entities = []
                    doc = []
            if tid is not None:
                entities.append([language_convert(span.strip(), language), tid])
            doc.append(span)

    processed = language_convert("".join(doc), language)
    if len(processed.strip()) > 0:
        doc_list.append(processed)
        entity_list.append(entities)

    out = {
        "title": title,
        "text": doc_list,
        "entity": entity_list,
    }

    return out


def main(_):
    if FLAGS.mode == "w":
        already = set()
    else:
        already = load_already(FLAGS.output, "title")

    wiki_db = SqliteDict(FLAGS.wiki_db, flag="r")
    alias_rev_db = SqliteDict(FLAGS.alias_rev_db, flag="r")

    with open(FLAGS.output, FLAGS.mode, encoding="utf-8") as writer:
        for instance in generate_instances(FLAGS):
            if instance["title"] in already:
                logger.info(f"{instance['title']} has exists!")
                continue
            try:
                if FLAGS.clean:
                    clean_html = clean_soup(instance["html"])
                else:
                    clean_html = BeautifulSoup(instance["html"], features="html.parser")
                processed = process(
                    instance["title"], clean_html, wiki_db, alias_rev_db, FLAGS.language
                )
                writer.write(json.dumps(processed, ensure_ascii=False) + "\n")
            except TypeError:
                logger.info(f"{instance['title']} type error")
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument(
        "--clean", action="store_true", help="Whether need clean the original html"
    )
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("--wiki_db", type=str, default="data/db/wiki.db")
    parser.add_argument("--alias_rev_db", type=str, default="data/db/alias_rev.db")
    parser.add_argument("--mode", type=str, default="w", help="w: rewrite; a: append")
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO)
    logger.info(f"{FLAGS}")

    main(_)
