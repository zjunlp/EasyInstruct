import sys
sys.path.append("./")
from typing import Any, Dict
import argparse
import json
import logging
import re
from tqdm import tqdm
from bs4 import BeautifulSoup
from sqlitedict import SqliteDict

from kglm.util import format_wikilink, format_title, format_titletext, load_already, language_convert, clean_u200b, get_length
from kglm.clean_html import clean_soup
logger = logging.getLogger(__name__) 


RE_WHITESPACE = re.compile(r'[\n\r\s]+')
RE_HEADER = re.compile(r'^h[1-6]')


def generate_instances(FLAGS: str) -> Dict[str, Any]:
    """Generates instances from an input JSON-lines file"""
    with open(FLAGS.input, 'r', encoding="utf-8") as f:
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
    # 1、First, search for qid in wiki.db (already resolved)
    try:
        title_id = wiki_db[format_wikilink(title, language)]      
    except KeyError:
        # 2、If the title is not found, just format (title) it in alias-rev.db. 
        # There must be multiple QIDs. Don't be afraid, symbolically choose the first QID. 
        # Here, the main purpose is to preliminarily identify the entity, without considering ambiguity
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
        '''
        If node is a link, make sure text is annotated with the corresponding title attribute. 
        NOTE: title is an attribute of the <a> tag. Don't get confused with the page title.
        '''
        if node.name == 'a':    
            try:
                key = format_wikilink(node['title'], language)     
            except KeyError:     
                key = None
            # For all <a></a>, they are generally entities and will first query wiki. db before querying alias-rev. db
            try:
                iid = wiki_db[key]       
            except KeyError:
                # Be careful with formatting when querying alias-rev.db, removing (), (), "", etc
                try:
                    stitle = format_wikilink(format_title(format_titletext(node['title'])), language)
                    iids = alias_rev_db[stitle]   
                except KeyError:                   
                    iid = None      
                else:
                    if len(iids) > 0: 
                        iid = iids[0]
                    else:
                        iid = None
            ids.append(iid)
            spans.append(node.text)
        elif RE_HEADER.search(str(node.name)):          
            pass
        elif node.name == 'b' and len(spans) < 10:      # For the first few<b></b>, they will be directly associated with the title, which is also consistent (although there are some exceptions)
            if len(node.text) > 1:
                ids.append(title_id)
                spans.append(format_titletext(node.text))
            else:
                ids.append(None)
                spans.append(format_titletext(node.text))
        else:                                          
            if hasattr(node, 'children'):
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
    '''
    Two segmentation scenarios:
    1. span=="\n"
    2. The paragraph length has reached max_len and has not encountered span=="\n"
    '''
    for tid, span in zip(ids, spans):
        span = clean_u200b(span)
        if span == "\n":
            if len(doc) != 0:
                processed = language_convert(''.join(doc), language)
                if len(processed.strip()) > 0:
                    doc_list.append(processed)
                    entity_list.append(entities)
                    entities = []
                    doc = []
        else:
            if get_length(''.join(doc) + span, language) > max_len and len(doc) > 0 and doc[-1].endswith("\n"):
                processed = language_convert(''.join(doc), language)
                if len(processed.strip()) > 0:
                    doc_list.append(processed)
                    entity_list.append(entities)
                    entities = []
                    doc = []
            if tid is not None:
                entities.append([language_convert(span.strip(), language), tid])
            doc.append(span)

    processed = language_convert(''.join(doc), language)
    if len(processed.strip()) > 0:
        doc_list.append(processed)
        entity_list.append(entities)
    
    out = {
        'title': title,
        'text': doc_list,
        'entity': entity_list,
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
            if instance['title'] in already:
                logger.info(f"{instance['title']} has exists!")
                continue
            try:
                if FLAGS.clean:
                    clean_html = clean_soup(instance['html'])
                else:
                    clean_html = BeautifulSoup(instance['html'], features="html.parser")
                processed = process(instance['title'], clean_html, wiki_db, alias_rev_db, FLAGS.language)
                writer.write(json.dumps(processed, ensure_ascii=False)+"\n")
            except TypeError:
                logger.info(f"{instance['title']} type error")
                continue
            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('--clean', action='store_true', help='Whether need clean the original html')
    parser.add_argument('--language', type=str, default='en')
    parser.add_argument('--wiki_db', type=str, default='data/db/wiki.db')
    parser.add_argument('--alias_rev_db', type=str, default='data/db/alias_rev.db')
    parser.add_argument('--mode', type=str, default='w', help='w: rewrite; a: append')
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO)
    logger.info(f"{FLAGS}")

    main(_)

