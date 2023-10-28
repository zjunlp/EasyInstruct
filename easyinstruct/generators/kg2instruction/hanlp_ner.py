import hanlp
import argparse
import json
from tqdm import tqdm
import logging
from typing import List

from .util import load_already

logger = logging.getLogger(__name__)


def generate_instances(FLAGS):
    """Generates instances from an input JSON-lines file"""
    with open(FLAGS.input, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            data = json.loads(line)
            yield data


def ner(
    text: List[str], hanlp, language: str = "en", chunk: int = 3
) -> List[List[List[str]]]:
    all_processed = []
    for i in range(0, len(text), chunk):
        texts = text[i : i + chunk]
        if language == "zh":
            processed = hanlp(texts, tasks="ner/ontonotes")
        else:
            processed = hanlp(texts, tasks="ner")
        try:
            if language == "zh":
                entity = processed["ner/ontonotes"]
            else:
                entity = processed["ner"]
        except KeyError:
            entity = [[]]
        all_processed.extend(entity)
    return all_processed


def main(_):
    logger.info("Starting queue loader")
    if FLAGS.mode == "w":
        already = set()
    else:
        already = load_already(FLAGS.output, "title")

    HanLP = hanlp.load(FLAGS.model, devices=FLAGS.device)
    writer = open(FLAGS.output, FLAGS.mode, encoding="utf-8")
    for json_data in generate_instances(FLAGS):
        if json_data["title"] in already:
            print(f'{json_data["title"]} already exists')
            continue
        all_processed = ner(json_data["text"], HanLP, FLAGS.language, FLAGS.chunk)
        writer.write(
            json.dumps(
                {"title": json_data["title"], "entity": all_processed},
                ensure_ascii=False,
            )
            + "\n"
        )
    logger.info("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument(
        "--model",
        type=str,
        default="model/close_tok_pos_ner_srl_dep_sdp_con_electra_base",
    )
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--chunk", type=int, default=5)
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("--mode", type=str, default="w")
    FLAGS, _ = parser.parse_known_args()

    print(FLAGS)
    main(_)
