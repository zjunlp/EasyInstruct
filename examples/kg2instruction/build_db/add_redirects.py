import sys
sys.path.append('./')
import argparse
import logging
from xml.etree import ElementTree
from sqlitedict import SqliteDict
import bz2

from kglm.util import LOG_FORMAT, format_wikilink


logger = logging.getLogger(__name__)


xmlns = '{http://www.mediawiki.org/xml/export-0.10/}'


def extract_redirect(elem: ElementTree.Element) -> str:
    """Extracts redirects from a <page> element in the Wikipedia dump.
    Args:
        elem : ``xml.etree.ElementTree.Element``
            The <page> element to process.

    Returns:
        A tuple ``(from, to)`` containing the titles of the pages being
        redirected from and to if the page is a redirect, otherwise ``None``.
    """
    # Get page title
    title = elem.find(f'{xmlns}title')
    if title is None:
        logger.debug('<page> has no <title> element')
        return
    _from = title.text.replace(' ', '_').capitalize()
    # Check if page is a redirect
    redirect = elem.find(f'{xmlns}redirect')
    if redirect is None:
        logger.debug('<page> has no <redirect> element')
        return
    _to = redirect.attrib['title'].replace(' ', '_').capitalize()
    logger.debug('Redirect from "%s" to "%s"', _from, _to)
    return _from, _to



def main(_):
    logger.info('Opening database file at: "%s"', FLAGS.db)
    wiki_db = SqliteDict(FLAGS.db, autocommit=True)

    with bz2.open(FLAGS.input, 'r') as f:
        tree = ElementTree.iterparse(f, events=('start', 'end'))
        root = None
        for event, elem in tree:
            if event == 'start':
                if root is None:
                    root = elem
                else:
                    continue
            if elem.tag == f'{xmlns}page':
                redirect = extract_redirect(elem)
                if redirect is None:
                    continue
                _from, _to = redirect
                logger.debug('Looking up "%s"', _to)
                try:
                    entity_id = wiki_db[_to]
                    logger.debug('Found id "%s"', entity_id)
                except KeyError:
                    logger.debug('Could not find "%s"', _to)
                    continue
                if _from not in wiki_db:
                    _from = format_wikilink(_from, FLAGS.language)
                    logger.warning('"%s" not in database', _from)
                    wiki_db[_from] = entity_id
                elem.clear()
                root.clear()

    wiki_db.commit()
    logger.info('Done')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('--db', type=str)
    parser.add_argument('--language', type=str, default='en')
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)

