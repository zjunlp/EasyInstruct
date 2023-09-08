from .base_generator import BaseGenerator

class KG2InstructGenerator(BaseGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def generate(self):
        raise NotImplementedError
