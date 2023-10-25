import argparse
import json
import logging
import requests
import urllib3
from tqdm import tqdm

from .util import LOG_FORMAT, load_already

urllib3.disable_warnings()
logger = logging.getLogger(__name__)


def generate_instances(FLAGS):
    """Generates instances from an input JSON-lines file"""
    with open(FLAGS.input, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            title = line.strip()
            yield title


def parse_html(title, language):
    endpoint = f"http://{language}.wikipedia.org/w/api.php"
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "close",
    }
    params = {
        "action": "parse",
        "prop": "text",
        "format": "json",
        "contentmodel": "wikitext",
    }
    params["page"] = title

    response = requests.get(endpoint, params=params, headers=headers, verify=False)
    if response.status_code == 200:
        response_json = response.json()
        try:
            html = response_json["parse"]["text"]["*"]
        except KeyError:
            logger.info('No HTML returned for "%s"', title)
            return None
        out = {"title": title, "html": html}
    else:
        logger.info('Bad response for "%s"', title)
        return None
    return out


def main(_) -> None:
    logger.info("Starting queue loader")
    if FLAGS.mode == "w":
        already = set()
    else:
        already = load_already(FLAGS.output, "title")

    writer = open(FLAGS.output, FLAGS.mode, encoding="utf-8")
    for title in generate_instances(FLAGS):
        if title in already:
            print(f"{title} has exists!")
            continue
        out = parse_html(title, FLAGS.language)
        if out is not None:
            writer.write(json.dumps(out, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("-j", type=int, default=4, help="Number of processors")
    parser.add_argument("--mode", type=str, default="w", help="w: rewrite; a: append")
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)
