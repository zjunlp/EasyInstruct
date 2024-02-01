import pandas as pd
from tqdm import tqdm
from lexicalrichness import LexicalRichness
from pandarallel import pandarallel

from .base_selector import BaseSelector


class MTLDSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
        ttr_threshold: float = 0.72,
        min_mtld: float = 8,
        max_mtld: float = 22,
        score_only: bool = False,
    ):
        super(MTLDSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )
        self.ttr_threshold = ttr_threshold
        self.min_mtld = min_mtld
        self.max_mtld = max_mtld
        self.score_only = score_only

    def mtld(self, text):
        lex = LexicalRichness(text)
        return lex.mtld(threshold=self.ttr_threshold)

    def __process__(self, data):
        tqdm.pandas()
        df = pd.DataFrame(data)
        if df.shape[0] > 15000:
            pandarallel.initialize()
            df["mtld_score"] = df["instruction"].parallel_apply(lambda x: self.mtld(x))
        else:
            df["mtld_score"] = df["instruction"].progress_apply(lambda x: self.mtld(x))
        if self.score_only:
            data = df.to_dict(orient="records")
        else:
            selected_data = df[
                (df["mtld_score"] >= self.min_mtld)
                & (df["mtld_score"] <= self.max_mtld)
            ].to_dict(orient="records")

        return data if self.score_only else selected_data
