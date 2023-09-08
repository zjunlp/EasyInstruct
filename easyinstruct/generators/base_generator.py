class BaseGenerator:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def generate(self):
        raise NotImplementedError
    
    def post_process(self):
        raise NotImplementedError