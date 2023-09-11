class BaseGenerator:
    def __init__(self, 
                 target_dir: str = "data/generations/"
                 ):
        self.target_dir = target_dir

    def generate(self):
        raise NotImplementedError
