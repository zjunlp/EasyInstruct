import argparse
import json
import logging
import os
import re
from tqdm import tqdm
from bs4 import BeautifulSoup, Comment

from .util import LOG_FORMAT

logger = logging.getLogger(__name__)


RE_WHITESPACE = re.compile(r"[\n\r\s]+")
RE_HEADER = re.compile(r"^h[1-6]")


def load_already(soutput: str):
    already = set()
    if os.path.exists(soutput):
        with open(soutput, "r", encoding="utf-8") as reader:
            for line in reader:
                already.add(json.loads(line.strip())["title"])
    return already


def generate_instances(FLAGS, already):
    """Generates instances from an input JSON-lines file"""
    with open(FLAGS.input, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            data = json.loads(line)
            if data["title"] in already:
                logger.info(f"{data['title']} already exists!")
                continue
            yield data


def clean_soup(html) -> None:
    """Cleans the parsed HTML tree.
    This is done in the following steps:
        - Remove all unwanted elements and their children from the tree.
        - Replacing all math elements with a <formula> token.
        - Clearing formatting
    """
    # Remove all top-level unwanted elements
    soup = BeautifulSoup(html, features="html.parser")
    root = soup.div

    unwanted_tags = ["div", "table", "style"]
    for tag in unwanted_tags:
        for branch in root(tag, recusive=False):
            branch.decompose()

    # Remove all reference tags
    for reference in root.select(".reference"):
        reference.decompose()
    # Remove all 'edit section' spans from headings
    for edit in root.select("span.mw-editsection"):
        edit.decompose()
    # Remove any page elements which are not rendered
    for invisible in root.select(".noprint,.mw-empty-elt"):
        invisible.decompose()
    # Comments need to be handled seperately
    for comment in root(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    # Math is typically rendered two ways: inline (as a <span>), and as a
    # seperate line (as a <dl><dd><span>). Unfortunately, math can also just be
    # italicized text
    for equation in root.select("span.mwe-math-element"):
        equation.replace_with("__LATEX_FORMULA__")
    # We can clear formatting by using replace_with_children
    format_tags = ["i", "span", "dl", "dt"]
    for tag in format_tags:
        for branch in root(tag):
            branch.replaceWithChildren()
    return root


def main(_):
    if FLAGS.mode == "w":
        already = set()
    else:
        already = load_already(FLAGS.output)

    with open(FLAGS.output, FLAGS.mode, encoding="utf-8") as writer:
        for json_data in generate_instances(FLAGS, already):
            try:
                clean_html = clean_soup(json_data["html"])
            except TypeError:
                logger.info(f"{json_data['title']} type error")
                continue
            if clean_html is None or clean_html == "":
                logger.info(f"{json_data['title']} clean html is None or empty")
                continue
            writer.write(
                json.dumps(
                    {"title": json_data["title"], "html": str(clean_html)},
                    ensure_ascii=False,
                )
                + "\n"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument("-j", type=int, default=4, help="Number of processors")
    parser.add_argument("--mode", type=str, default="w", help="w: rewrite; a: append")
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)
