from .base_selector import BaseSelector


class MultiSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
        selectors_list: list = None,
    ):
        super(MultiSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )
        self.selectors_list = selectors_list

    def __process__(self, data):
        for selector in self.selectors_list:
            data = selector.__process__(data)
        return data
