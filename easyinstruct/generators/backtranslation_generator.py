from .base_generator import BaseGenerator


class BacktranslationGenerator(BaseGenerator):
    def __init__(self):
        super().__init__()
    
    def generate(self):
        raise NotImplementedError