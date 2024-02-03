import numpy as np
import random
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial
from rouge_score import rouge_scorer

from .base_selector import BaseSelector


class RougeSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
        threshold: float = 0.7,
        score_only: bool = False,
    ):
        super(RougeSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )
        self.threshold = threshold
        self.score_only = score_only

    def __process__(self, data):
        if len(data) == 0:
            return data
        scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)

        random.shuffle(data)
        selected_instructions = [data[0]["instruction"]]
        selected_data = [data[0]]

        for i in tqdm(range(1, len(data))):
            with Pool(4) as p:
                rouge_scores = p.map(
                    partial(scorer.score, data[i]["instruction"]), selected_instructions
                )
            rouge_scores = [score["rougeL"].fmeasure for score in rouge_scores]

            if self.score_only:
                data[i]["avg_rouge_score"] = float(np.mean(rouge_scores))
            elif max(rouge_scores) <= self.threshold:
                data[i]["avg_rouge_score"] = float(np.mean(rouge_scores))
                selected_instructions.append(data[i]["instruction"])
                selected_data.append(data[i])

        return data if self.score_only else selected_data
