from tqdm import tqdm

from .base_selector import BaseSelector


class MTLDSelector(BaseSelector):
    def __init__(
        self,
        source_dir: str = "data/generations/",
        target_dir: str = "data/selections/",
        source_file_path: str = "generated_instances.jsonl",
        target_file_path: str = "selected_instructions.jsonl",
        lower_threshold: float = 20,
        upper_threshold: float = 150,
        ttr_standard=0.72,
    ):
        super(MTLDSelector, self).__init__(
            source_dir, target_dir, source_file_path, target_file_path
        )
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold
        self.ttr_standard = ttr_standard

    def calculate_MTLD(self, text, ttr_standard):
        tokens = text.split()
        # if len(tokens) < 50:
        #     return -1.0

        types = []
        factors = 0.0
        now_ttr = 1.0
        tokens_number = 0
        types_number = 0

        for token in tokens:
            token = token.lower()
            tokens_number += 1

            if token not in types:
                types_number += 1
                types.append(token)

            now_ttr = types_number * 1.0 / tokens_number

            if now_ttr < ttr_standard:
                factors += 1.0
                now_ttr = 1.0
                tokens_number = 0
                types_number = 0
                types = []

        RS = now_ttr
        IFS = (1 - RS) * 1.0 / (1 - ttr_standard)
        IFS += factors

        if IFS != 0:
            mtld_score = len(tokens) / IFS
            return mtld_score
        else:
            return -1.0

    def __process__(self, data):
        selected_data = []

        for i in tqdm(range(0, len(data))):
            mtld_score = self.calculate_MTLD(
                text=data[i]["instruction"], ttr_standard=self.ttr_standard
            )
            if (
                mtld_score < self.lower_threshold or mtld_score > self.upper_threshold
            ) and mtld_score != -1:
                continue
            # if not isinstance(data[i], dict):
            #         data[i] = {}
            # data[i]["mtld_score"] = mtld_score
            selected_data.append(data[i])

        return selected_data
