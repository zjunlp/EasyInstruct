import sys
sys.path.append('./')
import argparse
import logging
from sqlitedict import SqliteDict

from kglm.util import generate_from_json_bz2, load_allowed_entities, LOG_FORMAT, language_convert
logger = logging.getLogger(__name__)

BAD_DATATYPES = ["Commons media file", "None", "External identifier", "URL"]


def render_time(value):
    posix_string = value['time']
    precision = int(value['precision'])
    return ['time', posix_string, precision] 


def render_quantity(value):
    amount = float(value['amount'])
    unit = value['unit']
    if unit.startswith("http://www.wikidata.org/entity/Q"):
        qid = unit.split("/")[-1]
        return ['quantity', qid, str(amount)]    
    else:
        return ['quantity', 'None', str(amount)]


def main(_):
    db = SqliteDict(FLAGS.db, autocommit=True, journal_mode='OFF')
    db_value = SqliteDict(FLAGS.db_value, autocommit=True, journal_mode='OFF')

    for data in generate_from_json_bz2(FLAGS.input):
        head = data['id']    # head entity

        claims = data['claims']
        relations = []
        relation_values = []
        for rel, snaks in claims.items():     # relation
            for snak in snaks:
                mainsnak = snak['mainsnak']
                if mainsnak['datatype'] in BAD_DATATYPES:
                    continue
                try:
                    value = mainsnak['datavalue']
                except KeyError:
                    continue

                # tail entity
                if value['type'] == 'wikibase-entityid':
                    tail = value['value']['id']
                    relations.append([rel, tail])
                elif value['type'] == 'time':
                    tail = render_time(value['value'])
                    relation_values.append([rel, tail])
                elif value['type'] == 'quantity':
                    tail = render_quantity(value['value'])
                    relation_values.append([rel, tail])
                else:
                    continue


        if len(relations) != 0:
            db[head] = relations
        if len(relation_values) != 0:
            db_value[head] = relation_values

    logger.info('Done')
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='path to wikidata dumps')
    parser.add_argument('--db', type=str, default='data/db/relation.db')
    parser.add_argument('--db_value', type=str, default='data/db/relation_value.db')
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)

