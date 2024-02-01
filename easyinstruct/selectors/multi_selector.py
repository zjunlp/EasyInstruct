from .base_selector import BaseSelector

selectors_priority = {
    "Deduplicator": 0,
    "LengthSelector": 1,
    "MTLDSelector": 2,
    "RougeSelector": 3,
    "PPLSelector": 4,
    "GPTScoreSelector": 5,
    "RandomSelector": 6,
}


class MultiSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
        selectors_list: list = None,
        resort: bool = True,
    ):
        super(MultiSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )
        if resort:
            selectors_list.sort(key=lambda x: selectors_priority[x.__class__.__name__])
        self.selectors_list = selectors_list

    def __process__(self, data):
        for selector in self.selectors_list:
            print(f"Processing {selector.__class__.__name__}...")
            selector.data_format = self.data_format
            data = selector.__process__(data)
        return data
