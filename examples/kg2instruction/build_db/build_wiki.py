import sys
sys.path.append('./')
import argparse
import logging
from sqlitedict import SqliteDict

from kglm.util import format_wikilink, generate_from_json_bz2, LOG_FORMAT
logger = logging.getLogger(__name__)


def main(_):
    db = SqliteDict(FLAGS.db, journal_mode='OFF')
    language = FLAGS.language + "wiki"
    for i, data in enumerate(generate_from_json_bz2(FLAGS.input)):
        iid = data['id']
        try:
            wikilink = data['sitelinks'][language]['title']     
        except KeyError:
            logger.debug('No %s title found for entity "%s"', language, iid)
            continue
        else:
            wikilink = format_wikilink(wikilink, language)
        if wikilink in db:
            continue
        db[wikilink] = iid
        if i % 1000000 == 0:
            db.commit()
    logger.info('Done')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help="path to wikipedia dumps")
    parser.add_argument('--language', type=str, default='en')
    parser.add_argument('--db', type=str, default='data/db/wiki.db')
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)

