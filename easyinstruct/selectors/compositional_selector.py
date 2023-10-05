from .base_selector import BaseSelector

class CompositionalSelector(BaseSelector):
    def __init__(self, 
                 selectors_list: list = None
                 ):
        super().__init__()
        self.selectors_list = selectors_list

    def __process__(self, data):
        for selector in self.selectors_list:
            data = selector.__process__(data)
        return data