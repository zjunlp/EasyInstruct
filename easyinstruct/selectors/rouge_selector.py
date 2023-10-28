from tqdm import tqdm
from multiprocessing import Pool
from functools import partial
from rouge_score import rouge_scorer

from .base_selector import BaseSelector


class RougeSelector(BaseSelector):
    def __init__(
        self,
        source_dir: str = "data/generations/",
        target_dir: str = "data/selections/",
        source_file_path: str = "generated_instances.jsonl",
        target_file_path: str = "selected_instructions.jsonl",
        threshold: float = 0.7,
    ):
        super(RougeSelector, self).__init__(
            source_dir, target_dir, source_file_path, target_file_path
        )
        self.threshold = threshold

    def __process__(self, data):
        scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)

        selected_instructions = [data[0]["instruction"]]
        selected_data = [data[0]]

        for i in tqdm(range(1, len(data))):
            with Pool(4) as p:
                rouge_scores = p.map(
                    partial(scorer.score, data[i]["instruction"]), selected_instructions
                )
            rouge_scores = [score["rougeL"].fmeasure for score in rouge_scores]
            if max(rouge_scores) > self.threshold:
                continue
            selected_instructions.append(data[i]["instruction"])
            selected_data.append(data[i])

        return selected_data
