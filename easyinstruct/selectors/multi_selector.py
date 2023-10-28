from .base_selector import BaseSelector


class MultiSelector(BaseSelector):
    def __init__(
        self,
        source_dir: str = "data/generations/",
        target_dir: str = "data/selections/",
        source_file_path: str = "generated_instances.jsonl",
        target_file_path: str = "selected_instructions.jsonl",
        selectors_list: list = None,
    ):
        super(MultiSelector, self).__init__(
            source_dir, target_dir, source_file_path, target_file_path
        )
        self.selectors_list = selectors_list

    def __process__(self, data):
        for selector in self.selectors_list:
            data = selector.__process__(data)
        return data
