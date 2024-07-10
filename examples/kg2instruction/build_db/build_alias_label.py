'''zh、zh-hans、zh-cn、zh-hk、zh-tw、zh-hant、zh-my、zh-sg、zh-mo'''
import sys
sys.path.append('./')
import logging
import argparse
from sqlitedict import SqliteDict

from kglm.util import generate_from_json_bz2, LOG_FORMAT, format_wikilink
logger = logging.getLogger(__name__)


def en_process(db, db_rev, label_db):
    for data in generate_from_json_bz2(FLAGS.input):
        iid = data['id']
        if iid in db:
            continue
        aliases = set()
        label = ""
        if 'labels' in data:
            if "en" in data['labels']:
                label = format_wikilink(data['labels']['en']['value'], 'en')

        if label != "":
            label_db[iid] = label
            aliases.add(label)

        if 'aliases' not in data:
            continue
        if "en" in data['aliases']:
            for x in data['aliases']['en']:
                aliases.add(format_wikilink(x['value'], 'en'))
        else:
            if len(aliases) == 0:
                continue
        if len(aliases) > 0:
            db[iid] = list(aliases)
        for x in aliases:
            if x in db_rev:
                db_rev.update({x:iid})
            else:
                db_rev[x] = [iid, ]

    logger.info('Done')



def zh_process(db, db_rev, label_db):
    for data in generate_from_json_bz2(FLAGS.input):
        iid = data['id']
        aliases = set()
        label = ""
        if 'labels' in data:
            if "zh" in data['labels']:
                label = format_wikilink(data['labels']['zh']['value'], 'zh')
            elif "zh-hans" in data['labels']:
                label = format_wikilink(data['labels']['zh-hans']['value'], 'zh')
            elif "zh-cn" in data['labels']:
                label = format_wikilink(data['labels']['zh-cn']['value'], 'zh')
            elif "zh-hk" in data['labels']:
                label = format_wikilink(data['labels']['zh-hk']['value'], 'zh')
            elif "zh-tw" in data['labels']:
                label = format_wikilink(data['labels']['zh-tw']['value'], 'zh')
            elif "zh-hant" in data['labels']:
                label = format_wikilink(data['labels']['zh-hant']['value'], 'zh')
            elif "zh-my" in data['labels']:
                label = format_wikilink(data['labels']['zh-my']['value'], 'zh')
            elif "zh-sg" in data['labels']:
                label = format_wikilink(data['labels']['zh-sg']['value'], 'zh')
            elif "zh-mo" in data['labels']:
                label = format_wikilink(data['labels']['zh-mo']['value'], 'zh')
        
        if label != "":
            label_db[iid] = label
            aliases.add(label)

        if 'aliases' not in data:
            continue
        if "zh" in data['aliases']:
            for x in data['aliases']['zh']:
                aliases.add(format_wikilink(x['value'], 'zh'))
        elif "zh-hans" in data['aliases']:
            for x in data['aliases']['zh-hans']:
                aliases.add(format_wikilink(x['value'], 'zh'))
        elif "zh-cn" in data['aliases']:
            for x in data['aliases']['zh-cn']:
                aliases.add(format_wikilink(x['value'], 'zh'))
        elif "zh-hk" in data['aliases']:
            for x in data['aliases']['zh-hk']:
                aliases.add(format_wikilink(x['value'], 'zh'))
        elif "zh-tw" in data['aliases']:
            for x in data['aliases']['zh-tw']:
                aliases.add(format_wikilink(x['value'], 'zh'))
        elif "zh-hant" in data['aliases']:
            for x in data['aliases']['zh-hant']:
                aliases.add(format_wikilink(x['value'], 'zh'))
        elif "zh-my" in data['aliases']:
            for x in data['aliases']['zh-my']:
                aliases.add(format_wikilink(x['value'], 'zh'))
        elif "zh-sg" in data['aliases']:
            for x in data['aliases']['zh-sg']:
                aliases.add(format_wikilink(x['value'], 'zh'))
        elif "zh-mo" in data['aliases']:
            for x in data['aliases']['zh-mo']:
                aliases.add(format_wikilink(x['value'], 'zh'))
        else:
            if len(aliases) == 0:
                continue
        
        if len(aliases) > 0:
            db[iid] = list(aliases)
        for x in aliases:
            if x in db_rev:
                db_rev.update({x:iid})
            else:
                db_rev[x] = [iid, ]

    logger.info('Done')


def main(_):
    logger.info('Opening data file at: "%s"', FLAGS.db)

    db = SqliteDict(FLAGS.db, autocommit=True, journal_mode='OFF')
    db_rev = SqliteDict(FLAGS.db_rev, autocommit=True, journal_mode='OFF')
    label_db = SqliteDict(FLAGS.label_db, autocommit=True, journal_mode='OFF')

    if FLAGS.language == "zh":
        zh_process(db, db_rev, label_db)
    else:
        en_process(db, db_rev, label_db)

    allowed_entity = set()
    for key, _ in db.iteritems():
        allowed_entity.add(key)
    with open(FLAGS.entities, "w") as writer:
        for x in allowed_entity:
            writer.write(x+"\n")
    logger.info(f'Store allowed list to {FLAGS.entities}, Length = {len(allowed_entity)}')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='path to wikidata dumps (JSON)')
    parser.add_argument('--language', type=str, default='en')
    parser.add_argument('--db', type=str, default='data/db/alias.db')
    parser.add_argument('--db_rev', type=str, default='data/db/alias_rev.db')
    parser.add_argument('--label_db', type=str, default='data/db/label.db')
    parser.add_argument('-e', '--entities', type=str, default='data/other/allowed_entity.txt')
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)


