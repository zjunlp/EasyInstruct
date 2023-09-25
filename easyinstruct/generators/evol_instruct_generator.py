from easyinstruct import BasePrompt
from .base_generator import BaseGenerator

class EvolInstructGenerator(BaseGenerator):

    def __init__(self):
        super().__init__()

    def generate(self):
        raise NotImplementedError